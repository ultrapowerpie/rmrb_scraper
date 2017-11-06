#!/usr/bin/env python
from scraper import Scraper

import concurrent.futures.ThreadPoolExecutor
import argparse, os

parser = argparse.ArgumentParser(description='Scrape articles from rmrb.')

parser.add_argument('--folder', default='webpages', type=str,
    help='the folder to write downloaded pages to (default: webpages)')
parser.add_argument('--checkpoint', default='0', type=int,
    help='the last completed page of search results saved (default: 0)')
parser.add_argument('--headless', action='store_true',
    help='whether to run Chrome in headless mode (default: True)')
parser.add_argument('--maxthreads', default='4', type=int,
    help='maximum number of threads we can run at once (default: 4)')

args = parser.parse_args()

scrapers = []

executor = ThreadPoolExecutor(max_workers=args.maxthreads)

for year in range(1989, 2013):
    filename = str(year)+'.txt'
    if not os.path.exists(filename):
        with open(filename, 'wb') as f:
            f.write((str(0)).encode('utf-8'))

    with open(filename, 'rb') as f:
        checkpoint = int(f.readline())

    s = Scraper(headless=args.headless, checkpoint=checkpoint, folder=args.folder, query=year)
    scrapers.append(s)
    executor.submit(s.scrape_pages)
