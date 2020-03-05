import argparse
import datetime
import hashlib
import json
import sys
import time

from dateutil import parser


def parse_entry(entry):
    start = parser.parse(entry['start'])
    stop = parser.parse(entry['stop'])
    delta = stop - start
    return (start.year, start.month, start.day), delta.total_seconds()


def total_seconds_per_day(parsed_entries):
    day_totals = {}
    for day, seconds in parsed_entries:
        day_totals[day] = day_totals.get(day, 0) + seconds
    return day_totals


def hours_minutes(day_totals):
    return {key: time.strftime("%Hh %Mm", time.gmtime(day_totals.get(key))) for key in day_totals.keys()}


def output_console(formatted_daily_totals):
    for day, total in sorted(formatted_daily_totals.items()):
        day_as_date = datetime.date(*day)
        print(day_as_date.isoformat(), total)


def output_json(formatted_daily_totals):
    output_object = {}
    for day, total in sorted(formatted_daily_totals.items()):
        day_as_date = datetime.date(*day)
        output_object[day_as_date.isoformat()] = total
    print(json.dumps(output_object))


def output_calendar(formatted_daily_totals):
    calendar = [
        'BEGIN:VCALENDAR',
        'VERSION:2.0',
        'PRODID:-//dusokat.io//watson_total',
    ]

    dt_stamp = time.strftime("%Y%m%dT%H%m%SZ", time.gmtime())
    for day, total in sorted(formatted_daily_totals.items()):
        day_as_date = datetime.date(*day)
        calendar.extend(daily_total_to_calendar_event(dt_stamp, day_as_date, total))

    calendar.append('END:VCALENDAR')
    print("\n".join(calendar))


def daily_total_to_calendar_event(dt_stamp, day: datetime, total):
    event_date = day.strftime("%Y%m%d")
    hash_object = hashlib.md5(event_date.encode())
    return [
        'BEGIN:VEVENT',
        'UID:' + hash_object.hexdigest(),
        'DTSTAMP:' + dt_stamp,
        'ORGANIZER;CN=Watson:MAILTO:watson@test.tld',
        'DTSTART:' + event_date,
        'DTEND:' + event_date,
        'SUMMARY:' + total,
        'END:VEVENT',
    ]


def main():
    arg_parser = argparse.ArgumentParser(description="Output daily totals from watson JSON logs")
    arg_parser.add_argument("-j", "--json", help="output as JSON", action="store_true")
    arg_parser.add_argument("-c", "--calendar", help="output as iCal", action="store_true")
    args = arg_parser.parse_args()

    entries = json.loads(sys.stdin.read(), object_hook=parse_entry)
    if args.json:
        output_json(hours_minutes(total_seconds_per_day(entries)))
    elif args.calendar:
        output_calendar(hours_minutes(total_seconds_per_day(entries)))
    else:
        output_console(hours_minutes(total_seconds_per_day(entries)))


main()
