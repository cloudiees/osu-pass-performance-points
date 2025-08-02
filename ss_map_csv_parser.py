# Used to parse a csv file for maps
from mapsubmitter9000 import submit_map
import csv
import asyncio

with open("ss_maps.csv", newline='') as csvfile:
    first = True
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        if first:
            first = False
            continue
        rank = int(row[0])
        map_id = int(row[1].split("/")[-1])
        submit_map(map_id, rank)
        asyncio.sleep(.5)