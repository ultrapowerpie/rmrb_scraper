#!/usr/bin/env python
from scraper import Scraper
import _thread
import argparse, os

parser = argparse.ArgumentParser(description='Scrape articles from rmrb.')

parser.add_argument('--folder', default='webpages', type=str,
    help='the folder to write downloaded pages to (default: webpages)')
parser.add_argument('--headless', action='store_true',
    help='whether to run Chrome in headless mode (default: True)')
parser.add_argument('--maxworkers', default='4', type=int,
    help='maximum number of workers we can run at once (default: 4)')

args = parser.parse_args()

n = args.maxworkers

scrapers = []
years = range(1989, 2013)
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
            Scraper(headless=args.headless, checkpoint=checkpoint, folder=args.folder, query=year)
        )

    for s in scrapers:
        s.start()

    for s in scrapers:
        s.join()
