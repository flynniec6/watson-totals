import datetime
import time

from dateutil import parser
import json
import sys


def parse_entry(entry):
	start = parser.parse(entry['start'])
	stop = parser.parse(entry['stop'])
	delta = stop - start
	return start.strftime("%Y,%m,%d"), delta.total_seconds()


def total_seconds_per_day(parsed_entries):
	day_totals = {}
	for day, seconds in parsed_entries:
		day_totals[day] = day_totals.get(day, 0) + seconds
	return day_totals


def hours_minutes(day_totals):
	formatted_daily_totals = {}
	for day, total in day_totals.items():
		formatted_daily_totals[day] = time.strftime("%Hh %Mm", time.gmtime(total))
	return formatted_daily_totals


def main():
	entries = json.loads(sys.stdin.read(), object_hook=parse_entry)
	print(hours_minutes(total_seconds_per_day(entries)))


main()
