#!/usr/bin/env python3

import csv

import bs4
import dateutil.parser
import requests

from collections import namedtuple
from datetime import timedelta
from itertools import chain


days = [
'http://www.tomorrowland.com/en/friday-22-july',
'http://www.tomorrowland.com/en/saturday-23-july',
'http://www.tomorrowland.com/en/sunday-24-july',
]


TimeSlot = namedtuple('TimeSlot', ['stage', 'artist', 'time_start', 'time_end', 'duration'])


def fetch_day(url, parser="lxml"):
    day_html = requests.get(url).text
    soup = bs4.BeautifulSoup(day_html, parser)
    return soup


def parse_day(url):
    soup = fetch_day(url)
    day_str = soup.find('h1', class_='page-title').text
    day = dateutil.parser.parse(day_str)

    stage_titles = {}
    for title in soup.find_all('div', class_='stage-logo'):
        stage_titles[title['data-id']] = title.find('img', class_='stage-icon')['title']

    stages = soup.find_all('div', class_='stage')
    return [parse_stage(stage, stage_titles, day) for stage in stages]


def parse_stage(stage, titles, day):
    timeslots = stage.find('div', class_='artists').find_all('div', class_="time-slot performance")
    stage_id = stage['data-id']
    stage_title = titles[stage_id]

    return [parse_timeslot(timeslot, day, stage_title) for timeslot in timeslots]


def parse_timeslot(timeslot, day, stage):
    artist = timeslot.find('a').text
    time_start, time_end = timeslot.find('span', class_='time').text.split('-')
    set_start = parse_time(day, time_start)
    set_end = parse_time(day, time_end)

    return TimeSlot(stage, artist, set_start, set_end, set_end - set_start)


def parse_time(day, time):
    # push times before 6am to the following day
    if int(time.partition(':')[0]) < 6:
        day = day + timedelta(days=1)

    return dateutil.parser.parse(time, default=day)


def main():
    sets = [parse_day(day) for day in days]
    sets

    # completely flatten the day[stage[set]] nested list structure
    flat_sets = chain.from_iterable((chain.from_iterable(sets)))

    # write out file
    with open("tomorrowland2016.csv", 'w') as outfile:
        csvfile = csv.writer(outfile)
        csvfile.writerow(TimeSlot._fields)
        csvfile.writerows(flat_sets)


if __name__ == '__main__':
    main()
