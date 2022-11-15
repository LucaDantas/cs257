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

    lowest_rating = flask.request.args.get("lowest_rating")
    highest_rating = flask.request.args.get("highest_rating")
    max_users = flask.request.args.get("max_users")
    institution_name = flask.request.args.get("institution_name")
    # institution_type = flask.request.args.get("institution_type")
    print("received args:", flask.request.args)
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
    # a user can ask for a query without any tag
    tag = flask.request.args.get("tag")
    lowest_rating = flask.request.args.get("lowest_rating")
    highest_rating = flask.request.args.get("highest_rating")
    max_problems = flask.request.args.get("max_problems")

    print("received args:", flask.request.args)

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
    # values of the data requested must be either total_solves or difficulty
    # data_requested = flask.request.args.get("data_requested")
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
                tags[tag].append((element[0], element[1]))
            
            cursor.close()
            connection.close()
        except Exception as e:
            traceback.print_exc()

    return json.dumps(tags)


@api.route('/tag_names')
def get_tag_names():
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
    received_tags = received_tags.split(',')

    print("received args:", received_tags)

    query = """SELECT problems.rating, COUNT(problems.rating) FROM tags, problem_tags, problems WHERE"""

    for tag in received_tags:
        query += " tags.name = %s AND"
    query += " tags.id = problem_tags.tag_id AND problem_tags.problem_id = problems.problem_id GROUP BY problems.rating ORDER BY problems.rating"
    problems = []
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        cursor.execute(query, received_tags)
        for element in list(cursor):
            print(element)
            problems.append((element[0], element[1]))
        
        cursor.close()
        connection.close()
    except Exception as e:
        traceback.print_exc()
    print(problems)
    return json.dumps(problems)

