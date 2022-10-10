# Written by Luca Araújo, October 10th

import csv
from collections import OrderedDict

csv_athletes = 'athlete_events.csv'
csv_regions = 'noc_regions.csv'

csv_olympiad = 'olympiad.csv'
csv_noc_reg = 'noc_reg.csv'
csv_athlete = 'athlete.csv'
csv_athlete_year = 'athlete_year.csv'
csv_event = 'event.csv'
csv_medal = 'medal.csv'

athletes_events = []

noc_reg = {}
olympiad = {}
athlete = {}
athlete_year = {}
event = {}
medal = {}

def read_athletes_events():
    with open(csv_athletes, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',',quotechar='"')
        for row in reader:
            athletes_events.append(row)

def read_noc_regions():
    global noc_reg
    noc_reg.update({"NOC" : (0, "Team", "Notes")})
    with open(csv_regions, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',',quotechar='"')
        first = True
        for row in reader:
            if not first:
                noc_reg[row[0]] = (len(noc_reg), row[1], row[2]) # I want to save the index as the value
            else:
                first = False

    noc_reg["SGP"] = noc_reg["SIN"] # fortunately even when we change they remain in the same spot
    noc_reg.pop("SIN")

    noc_reg = OrderedDict(sorted(noc_reg.items(), key=lambda d: d[1][0])) # sort by value the dict to keep singapore in place

    with open(csv_noc_reg, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for key in noc_reg:
            print_out = [noc_reg[key][0], key, noc_reg[key][1], noc_reg[key][2]]
            writer.writerow(print_out)

def create_olympiad():
    for row in athletes_events:
        if (row[8], row[9], row[10], row[11]) not in olympiad:
            olympiad[(row[8], row[9], row[10], row[11])] = len(olympiad)

    with open(csv_olympiad, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for key in olympiad:
            print_out = [olympiad[key], key[0], key[1], key[2], key[3]]
            writer.writerow(print_out)

def create_athlete():
    athlete[("Name", "Sex")] = 0
    for row in athletes_events[1:]:
        if (row[1], row[2]) not in athlete:
            athlete[(row[1], row[2])] = len(athlete)

    with open(csv_athlete, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for key in athlete:
            print_out = [athlete[key], key[0], key[1]]
            writer.writerow(print_out)

def create_athlete_year():
    global athlete_year
    athlete_year[("olympiad_id", "athlete_id", "noc_reg_id", "Age", "Height", "Weight")] = 0
    for row in athletes_events[1:]:
        key = (olympiad[(row[8], row[9], row[10], row[11])],
               athlete[(row[1], row[2])], noc_reg[row[7]][0],
               row[3], row[4], row[5])
        if key not in athlete_year:
            athlete_year[key] = len(athlete_year)

    with open(csv_athlete_year, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for key in athlete_year:
            print_out = [athlete_year[key]] + [key[i] for i in range(len(key))]
            writer.writerow(print_out)

def create_event():
    global event
    for row in athletes_events:
        if (row[13], row[12]) not in event:
            event[(row[13], row[12])] = len(event)

    with open(csv_event, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for key in event:
            print_out = [event[key], key[0], key[1]]
            writer.writerow(print_out)

def create_medal():
    global medal
    medal[("athlete_year_id", "event_id", "Medal")] = 0
    for row in athletes_events[1:]:
        key_athlete_year = (olympiad[(row[8], row[9], row[10], row[11])],
                            athlete[(row[1], row[2])], noc_reg[row[7]][0],
                            row[3], row[4], row[5])
        key = (athlete_year[key_athlete_year], event[(row[13], row[12])], row[14])

        if key not in medal:
            medal[key] = len(medal)

    with open(csv_medal, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for key in medal:
            print_out = [medal[key], key[0], key[1], key[2]]
            writer.writerow(print_out)

def main():
    read_athletes_events()
    read_noc_regions()
    create_olympiad()
    create_athlete()
    create_athlete_year()
    create_event()
    create_medal()

if __name__ == '__main__':
    main()
