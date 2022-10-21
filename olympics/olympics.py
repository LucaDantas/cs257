#! /usr/bin/python3
"""
Written by Luca Araújo, 20 October 2022
"""

import sys
import argparse
import psycopg2

import config

def main():

    parser = argparse.ArgumentParser(usage='python3 olympiad.py [--help | -h] <command> <args>', add_help=False)
    subparsers = parser.add_subparsers(title='commands', metavar='')

    # noc_athletes subcommand
    parser_title = subparsers.add_parser('noc_athletes', aliases=['n'], usage=argparse.SUPPRESS, add_help=False)
    parser_title.add_argument('noc_name', nargs=1)

    # gold subcommand
    parser_author = subparsers.add_parser('gold', aliases=['g'], usage=argparse.SUPPRESS, add_help=False)

    # medals_by_noc subcommand
    parser_date = subparsers.add_parser('medals_by_noc', aliases=['m'], usage=argparse.SUPPRESS, add_help=False)
    parser_date.add_argument('noc_name', nargs=1)

    # parse the arguments
    if '--help' in sys.argv or '-h' in sys.argv:
        display_usage_statement()
        return

    # If user not asking for help, continue as normal
    arguments = parser.parse_args()

    # Search data source and display results
    if 'gold' in sys.argv or 'g' in sys.argv:
        nocs_gold = get_nocs_gold()
        for row in nocs_gold:
            print(f'{row[0]}: {row[1]}')

    elif 'noc_athletes' in sys.argv or 'n' in sys.argv:
        noc_athletes = get_noc_athletes(arguments.noc_name[0])
        for athlete in noc_athletes:
            print(athlete)

    elif 'medals_by_noc' in sys.argv or 'm' in sys.argv:
        medals = get_medals_by_noc(arguments.noc_name[0])
        for medal in medals:
            print(f'{medal[0]} {medal[1]}: {medal[2]}')

# connects to the database, imports the login information from config.py
def get_connection():
    try:
        return psycopg2.connect(database=config.database,
                                user=config.user,
                                password=config.password)
    except Exception as e:
        print(e, file=sys.stderr)
        exit()

def get_nocs_gold():
    nocs_gold = {}
    try:
        connection = get_connection()
        cursor = connection.cursor()

        # Queries the NOCs that have gold medals at all and get their count
        query = '''
        SELECT noc_reg.noc, COUNT(medal.medal) AS gold_medal_count
        FROM noc_reg, athlete_year, medal
        WHERE noc_reg.id = athlete_year.noc_reg_id
        AND medal.athlete_year_id = athlete_year.id
        AND medal.medal = 'Gold'
        GROUP BY noc_reg.noc
        ORDER BY COUNT(medal.medal) DESC
        '''
        cursor.execute(query)

        # Iterate over the query results and save the values in a dictionary.
        for row in cursor:
            nocs_gold[row[0]] = row[1]

        # Queries all NOCs and add those that don't have gold medals to the dictionary
        query_all_nocs = 'SELECT noc_reg.noc FROM noc_reg'
        cursor.execute(query_all_nocs)
        
        for row in cursor:
            if row[0] not in nocs_gold:
                nocs_gold[row[0]] = 0


    except Exception as e:
        print(e, file=sys.stderr)

    connection.close()
    # Return the values in a array sorted by the number of gold medals decreasingly and then alphabetically
    return sorted([(key, nocs_gold[key]) for key in nocs_gold], key=lambda a: (-a[1], a[0]))

def get_noc_athletes(noc):
    athletes = []
    try:
        query = '''SELECT DISTINCT athlete.name
                FROM athlete, athlete_year, noc_reg
                WHERE noc_reg.noc = %s
                AND noc_reg.id = athlete_year.noc_reg_id
                AND athlete_year.athlete_id = athlete.id
                ORDER BY athlete.name
                '''
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(query, (noc,))
        for athlete in cursor:
            athletes.append(athlete[0])

    except Exception as e:
        print(e, file=sys.stderr)

    connection.close()
    return athletes

def get_medals_by_noc(noc):
    medals = []
    try:
        query = '''SELECT olympiad.year, athlete.name, medal.medal
                FROM athlete, athlete_year, noc_reg, olympiad, medal
                WHERE noc_reg.noc = %s
                AND noc_reg.id = athlete_year.noc_reg_id
                AND athlete_year.athlete_id = athlete.id
                AND athlete_year.olympiad_id = olympiad.id
                AND athlete_year.id = medal.athlete_year_id
                AND medal.medal != 'None'
                ORDER BY olympiad.year DESC
                '''
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(query, (noc,))
        for medal in cursor:
            medals.append(medal)

    except Exception as e:
        print(e, file=sys.stderr)

    connection.close()
    return medals

def display_usage_statement():
    with open('./usage.txt') as usage_statement:
        print(usage_statement.read())


if __name__ == '__main__':
    main()
