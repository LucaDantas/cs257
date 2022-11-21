"""
Zimri Leisher and Luca Araujo
Codeforces database, API and web app
"""

import sys
import traceback
import psycopg2
import json
import config
import flask 
from collections import defaultdict


api = flask.Blueprint('api', __name__)


def get_connection():
    return psycopg2.connect(database=config.database,
                            user=config.user,
                            password=config.password)

@api.route('/help')
def get_help():
    return flask.send_file('.' + flask.url_for('static', filename='api-design.txt'), mimetype='text')

@api.route('/users/<institution_type>')
def get_users(institution_type):
    """REQUEST: /users/<institution_type>

institution_type (Required) -- defines whether we should search users
    by their university or country

GET parameters
    search_name (Optional, default: '') -- gives the name of the unversity/country
        to search for
    
    lowest_rating (Optional, default: -infinity) -- return only users with
        rating bigger than or equal to the one given
    
    highest_rating (Optional, default: infinity) -- return only users with
        rating less than or equal to the one given

    max_users (Optional, default: 10) -- the maximum number of users to return
        if value given is higher than 500 it is changed to 500

RESPONSE: a JSON list of dictionaries, each of which represents one
user, sorted decreasingly by rating. Each dictionary in this list
will have the following fields.

   handle -- (TEXT) the user's handle
   name -- (TEXT) the user's name
   rating -- (INTEGER) the user's current rating
   max_rating -- (INTEGER) the user's maximum rating
   rank -- (TEXT) the user's current rank
   max_rank -- (TEXT) the user's maximum rank"""

    lowest_rating = flask.request.args.get("lowest_rating")
    highest_rating = flask.request.args.get("highest_rating")
    max_users = flask.request.args.get("max_users")
    institution_name = flask.request.args.get("institution_name")
    query = """SELECT handle, first_name, last_name, rating, max_rating, user_rank, max_user_rank FROM users"""

    predicates = []
    args = {}

    if lowest_rating:
        predicates.append("""users.rating >= %(lowest_rating)s""")
        args["lowest_rating"] = int(lowest_rating)

    if highest_rating:
        predicates.append("""users.rating <= %(highest_rating)s""")
        args["highest_rating"] = int(highest_rating)

    if institution_type and institution_name:
        if institution_type == 'country':
            predicates.append("""users.country ILIKE CONCAT('%%', %(institution_name)s, '%%')""")
        else:
            predicates.append("""users.organization ILIKE CONCAT('%%', %(institution_name)s, '%%')""")
        args["institution_name"] = institution_name


    if len(predicates) > 0:
        query += " WHERE " + " AND ".join(predicates)

    query += " ORDER BY (-users.rating, users.handle) LIMIT %(max_users)s"

    args["max_users"] = int(max_users) if max_users else 50

    users = []
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(query, args)

        for row in list(cursor):
            users.append({"handle": row[0], "name": (row[1] if row[1] else "") + " " + (row[2] if row[2] else ""),
                          "rating": row[3], "max_rating": row[4], "user_rank": row[5], "max_user_rank": row[6]})

        cursor.close()
        connection.close()
    except Exception as e:
        traceback.print_exc()

    return json.dumps(users)


@api.route('/problems')
def get_problems():
    """REQUEST: /problems

GET parameters
    tag (Optional, default: '') -- returns only problems that contain
        the defined tag. If left blank returns problems of any tag
    
    lowest_rating (Optional, default: -infinity) -- return only problems with
        rating bigger than or equal to the one given
    
    highest_rating (Optional, default: infinity) -- return only problems with
        rating less than or equal to the one given

    max_problems (Optional, default: 10) -- the maximum number of problems to return
        if value given is higher than 500 it is changed to 500

RESPONSE: a JSON list of dictionaries, each of which represents one
problem, sorted decreasingly by number of users who solved the problem.
Each dictionary in this list will have the following fields.

   id -- (INTEGER) the codeforces id of the problem
   name -- (TEXT) the problem's name
   rating -- (INTEGER) the problem's rating
   tags -- (TEXT) the list of tags of a problem separated by commas
   solved_count -- (INTEGER) the number of users that solved that problem"""
    # a user can ask for a query without any tag
    tag = flask.request.args.get("tag")
    lowest_rating = flask.request.args.get("lowest_rating")
    highest_rating = flask.request.args.get("highest_rating")
    max_problems = flask.request.args.get("max_problems")

    query = """SELECT problems.problem_id, problems.name, rating, solved_count FROM problems"""

    predicates = []
    args = {}

    if tag:
        query += ", problem_tags, tags" # we only search through the tags if we need

        predicates.append("""tags.name = %(tag)s
                             AND tags.id = problem_tags.tag_id
                             AND problem_tags.problem_id = problems.problem_id""")
        args["tag"] = tag

    if lowest_rating:
        predicates.append("""problems.rating >= %(lowest_rating)s""")
        args["lowest_rating"] = int(lowest_rating)

    if highest_rating:
        predicates.append("""problems.rating <= %(highest_rating)s""")
        args["highest_rating"] = int(highest_rating)

    if len(predicates) > 0:
        query += " WHERE " + " AND ".join(predicates)

    query += " ORDER BY problems.solved_count DESC LIMIT %(max_problems)s"
    args["max_problems"] = int(max_problems) if max_problems else 50

    problems = []
    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(query, args)
        for row in list(cursor):
            problems.append({"id": row[0], "name": row[1], "rating": row[2], "solved_count": row[3]})

        for problem in problems:
            local_query= """SELECT tags.name FROM tags, problem_tags
                            WHERE problem_tags.problem_id = %(id)s
                            AND problem_tags.tag_id = tags.id"""
            local_args = {"id" : problem['id']}
            
            cursor.execute(local_query, local_args)

            problem["tags"] = []
            for tag in list(cursor):
                problem["tags"].append(tag[0])
            problem["tags"] = ", ".join(problem["tags"])

        cursor.close()
        connection.close()
    except Exception as e:
        traceback.print_exc()

    return json.dumps(problems)

@api.route('/contests/<data_requested>')
def get_contest_graph(data_requested):
    """REQUEST: /contests/<data_requested>

data_requested (Required) -- defines whether to display the graph by difficulty
    of the contest (calculated by the average difficulty of each contest)
    or by the number of users that solved any problem of that contest
    
GET parameters
    lowest_id (Optional, default: 0) -- return only the contests with id
        bigger than or equal to the given value
    
    highest_id (Optional, default: infinity) -- return only the contests with id
        less than or equal to the given value

RESPONSE: a JSON list of tuples of two elements, each of which represents one
contest, sorted increasingly by index. Each tuple contains a pair of (id, difficulty)
if the requested information was difficulty or a pair of (index, solved_count) if the
requested information was solved count"""
    # values of the data requested must be either total_solves or difficulty
    lowest_id = flask.request.args.get("lowest_id")
    highest_id = flask.request.args.get("highest_id")

    print("received args:", flask.request.args)

    predicates = []
    args = {}

    query = """SELECT contests.id, contests.%(data_requested)s FROM contests"""
    args["data_requested"] = psycopg2.extensions.AsIs(data_requested)

    if lowest_id:
        predicates.append("""contests.id >= %(lowest_id)s""")
        args["lowest_id"] = int(lowest_id)

    if highest_id:
        predicates.append("""contests.id <= %(highest_id)s""")
        args["highest_id"] = int(highest_id)

    if len(predicates) > 0:
        query += " WHERE " + " AND ".join(predicates)

    query += " ORDER BY contests.id"

    contests = []
    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(query, args)
        for row in list(cursor):
            contests.append((row[0], row[1]))
        
        cursor.close()
        connection.close()
    except Exception as e:
        traceback.print_exc()

    return json.dumps(contests)


@api.route('/tags_graph/<received_tags>')
def get_tags_graph(received_tags):
    """REQUEST: /tags_graph/<tags>

tags (Required) -- returns a plot graph for each of the required
    tags. The input is a list of tags separated by commas

RESPONSE: a JSON dictionary, each of which represents one
tag, sorted alphabetically by the name of the tag.
There is a field of the dictionary for every tag, the field
contains a list of tuples with the following parameters:

   rating -- (INTEGER) the rating range being counted
   count -- (INTEGER) the number of problems with that tag in that rating range"""
    received_tags = received_tags.split(',')

    print("received args:", received_tags)

    tags = {}
    for tag in received_tags:
        args = {}

        query = """SELECT problems.rating, COUNT(problems.rating) FROM tags, problem_tags, problems
                   WHERE tags.name = %(tag)s
                   AND tags.id = problem_tags.tag_id
                   AND problem_tags.problem_id = problems.problem_id
                   GROUP BY problems.rating
                   ORDER BY problems.rating"""

        args["tag"] = tag

        try:
            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute(query, args)
            tags[tag] = []
            for element in list(cursor):
                if(element[0]): # I don't want the problems that have no rating (which is represented as 0)
                    tags[tag].append((element[0], element[1]))
            
            cursor.close()
            connection.close()
        except Exception as e:
            traceback.print_exc()

    return json.dumps(tags)


@api.route('/tag_names')
def get_tag_names():
    """REQUEST: /tag_names

RESPONSE: a JSON list of TEXT with all the tag names"""
    query = """SELECT name FROM tags"""

    tags = []
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(query,)
        tags = []
        for tag in list(cursor):
            tags.append(tag[0])
        cursor.close()
        connection.close()
    except Exception as e:
        traceback.print_exc()

    return json.dumps(tags)


@api.route('/tags_intersection/<received_tags>')
def get_tags_intersection(received_tags):
    """REQUEST: /tags_intersection/<tags>

tags (Required) -- returns the information for the problems that
    contain all tags. The input is a list of tags separated by commas

RESPONSE: a JSON list of tuples, each of which represents a rating range,
    sorted decreasingly by rating. Each tuple will have the following fields:

   rating -- (INTEGER) the beginning of the rating range (all problems ratings' are multiples of 100)
   problem_count -- (INTEGER) the count of problems in that range
      with those tags
   solved_count -- (INTEGER) the count of solutions of problems
      in that range with those tags"""
    received_tags = received_tags.split(',')

    query = """SELECT problems.rating, SUM(problems.solved_count)
               FROM problems, problem_tags, tags
               WHERE problem_tags.tag_id = tags.id AND problems.problem_id = problem_tags.problem_id
               AND tags.name IN (
               """
    # match only problems with all of the given tags
    query += ','.join(['%s' for i in range(len(received_tags))])

    query += """) GROUP BY (problems.problem_id, problems.rating) HAVING COUNT(problems.problem_id) = %s"""

    ratingCount = defaultdict(int)
    solvedCount = defaultdict(int)
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        cursor.execute(query, received_tags + [len(received_tags)])
        for element in list(cursor):
            rating = element[0]
            solves = element[1]
            if not rating: 
                continue
            ratingCount[rating] += 1
            solvedCount[rating] += solves
        
        cursor.close()
        connection.close()
    except Exception as e:
        traceback.print_exc()

    # return a list of (rating, count at that rating, solutions at that rating) of problems with these tags
    return json.dumps(sorted([(rating, ratingCount[rating], solvedCount[rating]) for rating in ratingCount]))

