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
    """
    Returns a connection to the database specified in the
    config file, or raise an exception as specified in the
    psycopg2.connect method
    """
    return psycopg2.connect(database=config.database,
                            user=config.user,
                            password=config.password)

@api.route('/help')
def get_help():
    return '<p>' + '<br>'.join(open('.' + flask.url_for('static', filename='api-design.txt'), 'r').readlines()) + '</p>'

@api.route('/users')
def get_users():
    """
    Returns a list of up to 50 users in the database matching
    the specified criteria. Criteria can be:
        lowest_rating - the lowest rating to allow for a user
        highest_rating - the highest rating to allow for a user
        max_users - the maximum number of users to return
        institution_name - the name of the instutition to search by. If this is
        specified, institution_type must also be specified
        institution_type - country to search for users by country,
                            any other value to search for users by organization. Does nothing
                            if instutition_name is not specified

    The users will be sorted by their max rating descending, breaking ties 
    alphabetically by full name
    """

    lowest_rating = flask.request.args.get("lowest_rating")
    highest_rating = flask.request.args.get("highest_rating")
    max_users = flask.request.args.get("max_users")
    institution_name = flask.request.args.get("institution_name")
    institution_type = flask.request.args.get("institution_type")
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
            users.append({"handle": row[0], "first_name": row[1], "last_name": row[2],
                          "rating": row[3], "max_rating": row[4], "user_rank": row[5],
                          "max_user_rank": row[6]})

        cursor.close()
        connection.close()
    except Exception as e:
        traceback.print_exc()

    return json.dumps(users)


@api.route('/problems')
def get_problems():
    lowest_rating = flask.request.args.get("lowest_rating")
    highest_rating = flask.request.args.get("highest_rating")
    max_problems = flask.request.args.get("max_problems")
    print("received args:", flask.request.args)
    query = """SELECT problem_id, name, rating, solved_count FROM problems"""

    predicates = []
    args = {}

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


