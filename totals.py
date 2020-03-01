import datetime
from dateutil import parser
import json
import sys

def parse_entry(entry):
	start = parser.parse(entry['start'])
	stop = parser.parse(entry['stop'])
	delta = stop - start
	return start.date(), delta.total_seconds()


def sum_by_day(parsed_entries):
	day_totals = {}
	for parsed_entry in parsed_entries:
		key = (parsed_entry[0].strftime("%Y,%m,%d"))
		day_totals[key] = day_totals.get(key, 0) + parsed_entry[1]
	return day_totals


def main():
	# json.loads takes second parameter so it should be possible to convert the JSON on the fly to tuples
	entries = []
	raw = json.loads(sys.stdin.read())
	for entry in raw:
		entries.append(parse_entry(entry))
	print(sum_by_day(entries))


main()
