#!/usr/bin/env python
from scraper import Scraper
import _thread
import argparse, os

parser = argparse.ArgumentParser(description='Scrape articles from rmrb.')

parser.add_argument('--folder', default='webpages', type=str,
    help='the folder to write downloaded pages to (default: webpages)')
parser.add_argument('--headless', action='store_true',
    help='whether to run Chrome in headless mode (default: False)')
parser.add_argument('--query', default='南朝鲜 + 韩国 + 日本 + 台湾', type=str,
    help='the keyword query to search for (default: 南朝鲜 + 韩国 + 日本 + 台湾)')
parser.add_argument('--maxworkers', default='1', type=int,
    help='maximum number of workers we can run at once (default: 1)')
parser.add_argument('--wait', default='200', type=float,
    help='milliseconds to wait for between requests')

args = parser.parse_args()

n = args.maxworkers

scrapers = []
years = reversed(range(1989, 2013))
blocks = []

i = 0
while i < len(years):
    blocks.append(years[i:i+n])
    i += n

for block in blocks:
    for year in block:
        filename = str(year)+'.txt'
        if not os.path.exists(filename):
            with open(filename, 'wb') as f:
                f.write((str(0)+'\n').encode('utf-8'))

        with open(filename, 'rb') as f:
            lines = f.readlines()
            checkpoint = int(lines[-1])

        scrapers.append(
            Scraper(args.headless, checkpoint, args.folder, year, args.query, wait=args.wait)
        )

    for s in scrapers:
        s.start()

    for s in scrapers:
        s.join()
