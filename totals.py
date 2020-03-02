import argparse
import datetime
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


def print_console(formatted_daily_totals):
    for day, total in sorted(formatted_daily_totals.items()):
        day_as_date = datetime.date(*day)
        print(day_as_date.isoformat(), total)


def print_json(formatted_daily_totals):
    output_object = {}
    for day, total in sorted(formatted_daily_totals.items()):
        day_as_date = datetime.date(*day)
        output_object[day_as_date.isoformat()] = total
    print(json.dumps(output_object))


def main():
    arg_parser = argparse.ArgumentParser(description="Output daily totals from watson JSON logs")
    arg_parser.add_argument("-j", "--json", help="output as JSON", action="store_true")
    args = arg_parser.parse_args()

    entries = json.loads(sys.stdin.read(), object_hook=parse_entry)
    if args.json:
        print_json(hours_minutes(total_seconds_per_day(entries)))
    else:
        print_console(hours_minutes(total_seconds_per_day(entries)))


main()
