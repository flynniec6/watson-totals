#!/usr/local/opt/python/bin/python3.7
import datetime
from dateutil import parser
import json
import sys

entries = []

def convert(entry):
	start = parser.parse(entry['start'])
	stop = parser.parse(entry['stop'])
	delta = stop - start
	return (start, delta.total_seconds())

def totals():
	# json.loads takes second parameter so it should be possible to convert the JSON on the fly to tuples
	raw = json.loads(sys.stdin.read())
	for entry in raw:
		entries.append(convert(entry))

totals()
print(entries)
