import urllib.request
import json

API_BASE_URL = 'https://codeforces.com/api/'

def get_problems():
    url = f'{API_BASE_URL}/problemset.problems?tags=2-sat'
    result = json.loads(urllib.request.urlopen(url).read().decode('utf-8'))
    if result['status'] != "OK":
        print("ERROR GETTING THE DATA")
        return
    data = result['result']
    print(data)

def get_users():
    url = f'{API_BASE_URL}/user.ratedList?activeOnly=true&includeRetired=false'
    result = json.loads(urllib.request.urlopen(url).read().decode('utf-8'))
    print(result['status'])
    if result['status'] != "OK":
        print("ERROR GETTING THE DATA")
        return
    data = result['result']
    # print(data)

def get_contests():
    url = f'{API_BASE_URL}/contest.list?gym=false'
    result = json.loads(urllib.request.urlopen(url).read().decode('utf-8'))
    print(result['status'])
    if result['status'] != "OK":
        print("ERROR GETTING THE DATA")
        return
    data = result['result']
    print(data)

def main():
    get_contests()

if __name__ == '__main__':
    main()
