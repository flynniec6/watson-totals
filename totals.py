import argparse
import calendar
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
    return start.date(), delta.total_seconds()


def total_seconds_per_day(parsed_entries):
    day_totals = {}
    for day, seconds in parsed_entries:
        day_totals[day] = day_totals.get(day, 0) + seconds
    return day_totals


def prepare_output(seconds_per_day, rollup):
    output_object = []
    monthly_totals = {}
    for day, total in seconds_per_day.items():
        output_object.append((day, time.strftime("%Hh %Mm", time.gmtime(total)), "day"))
        if rollup:
            last_day = datetime.date(day.year, day.month, calendar.monthrange(day.year, day.month)[1])
            monthly_totals[last_day] = monthly_totals.get(last_day, 0) + total
    for day, total in monthly_totals.items():
        minutes, _ = divmod(total, 60)
        hours, minutes = divmod(minutes, 60)
        output_object.append((day, "Total %dh %dm" % (hours, minutes), "summary"))
    return sorted(output_object)


def output_console(prepared_output):
    for day, total, entry_type in prepared_output:
        print(day, total)


def output_json(prepared_output):
    json_object = [{day.isoformat(): total} for day, total, entry_type in prepared_output]
    print(json.dumps(json_object))


def output_calendar(prepared_output):
    calendar = [
        'BEGIN:VCALENDAR',
        'VERSION:2.0',
        'PRODID:-//dusokat.io//watson_total',
    ]

    dt_stamp = time.strftime("%Y%m%dT%H%m%SZ", time.gmtime())
    for day_entry in prepared_output:
        calendar.extend(daily_total_to_calendar_event(dt_stamp, *day_entry))

    calendar.append('END:VCALENDAR')
    print("\n".join(calendar))


def daily_total_to_calendar_event(dt_stamp, day: datetime, total, entry_type):
    event_date = day.strftime("%Y%m%d")
    hash_object = hashlib.md5(event_date.join(entry_type).encode())
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
    arg_parser.add_argument("-r", "--rollup", help="include month summary", action="store_true")
    args = arg_parser.parse_args()

    entries = json.loads(sys.stdin.read(), object_hook=parse_entry)
    rollup = args.rollup
    formatted_daily_totals = prepare_output(total_seconds_per_day(entries), rollup)

    if args.json:
        output_json(formatted_daily_totals)
    elif args.calendar:
        output_calendar(formatted_daily_totals)
    else:
        output_console(formatted_daily_totals)


main()
