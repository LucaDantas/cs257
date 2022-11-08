import urllib.request
import json
import csv

API_BASE_URL = 'https://codeforces.com/api/'

csv_problems = 'data/problems.csv'
csv_contests = 'data/contests.csv'
csv_users = 'data/users.csv'
csv_tags = 'data/tags.csv'
csv_problem_tags = 'data/problem_tags.csv'

def get_problems():
    url = f'{API_BASE_URL}/problemset.problems'
    result = json.loads(urllib.request.urlopen(url).read().decode('utf-8'))
    if result['status'] != "OK":
        print("error getting problems:", result)
        exit(1)
    
    problems = result['result']['problems']
    problems_statistics = result['result']['problemStatistics']

    n = len(problems)

    tags = {}
    ordered_tags = []
    for problem in problems:
        for tag in problem['tags']:
            if tag not in tags:
                tags[tag] = 0
                ordered_tags.append(tag)
    
    ordered_tags.sort()
    for i in range(len(ordered_tags)):
        tags[ordered_tags[i]] = i

    with open(csv_tags, 'w') as out_f:
        out = csv.writer(out_f)
        for i in range(len(ordered_tags)):
            out.writerow((i, ordered_tags[i]))

    with open(csv_problems, 'w') as out_f, open(csv_problem_tags, 'w') as linking_f:
        linking = csv.writer(linking_f)
        out = csv.writer(out_f)
        for i in range(n):
            problem = []
            problem_id = str(problems[i]['contestId']) + problems[i]['index']
            problem.append(problem_id)
            problem.append(problems[i]['contestId'])
            problem.append(problems[i]['name'])
            problem.append(problems[i]['rating'] if 'rating' in problems[i] else 0)
            problem.append(problems_statistics[i]['solvedCount'])
            out.writerow(problem)

            for tag in problems[i]['tags']:
                linking.writerow((problem_id, tags[tag]))

def get_users():
    #url = 'https://codeforces.com/api/user.info?handles=Luca;column;batmendbar'
    url = f'{API_BASE_URL}/user.ratedList?activeOnly=false&includeRetired=false'
    result = json.loads(urllib.request.urlopen(url).read().decode('utf-8'))
    print(result['status'])
    if result['status'] != "OK":
        print("error getting users:", result)
        exit(1)

    with open(csv_users, 'w') as out_f:
        out = csv.writer(out_f)
        for user in result['result']:
            a = []
            a.append(user['handle'])
            a.append(user['firstName'] if 'firstName' in user else '')
            a.append(user['lastName'] if 'lastName' in user else '')
            a.append(user['country'] if 'country' in user else '')
            a.append(user['organization'] if 'organization' in user else '')
            a.append(user['rating'])
            a.append(user['maxRating'])
            a.append(user['rank'])
            a.append(user['maxRank'])
            out.writerow(a)

def get_contests():
    url = f'{API_BASE_URL}/problemset.problems'
    result = json.loads(urllib.request.urlopen(url).read().decode('utf-8'))
    if result['status'] != "OK":
        print("error getting problems:", result)
        exit(1)
    
    problems = result['result']['problems']
    problems_statistics = result['result']['problemStatistics']

    n = len(problems)

    contests = [[0,0,0] for i in range(2000)] # we save a tuple of (solves, sum of difficulties, cnt of problems)

    for i in range(n):
        contests[problems[i]['contestId']][0] += problems_statistics[i]['solvedCount']
        contests[problems[i]['contestId']][1] += problems[i]['rating'] if 'rating' in problems[i] else 0
        contests[problems[i]['contestId']][2] += 1

    with open(csv_contests, 'w') as out_f:
        out = csv.writer(out_f)
        i = -1
        for contest in contests:
            i += 1
            if contest[2] == 0:
                continue
            out.writerow((i, contest[0], contest[1] // contest[2]))

def main():
    # get_problems()
    # get_users()
    # get_contests()

if __name__ == '__main__':
    main()
