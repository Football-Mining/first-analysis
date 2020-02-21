# coding:utf-8
import argparse
import requests
from urllib.parse import quote
from bs4 import BeautifulSoup
import datetime as dt
from datetime import datetime
import re
import os
from tqdm import tqdm
from infos import *

parser = argparse.ArgumentParser("xml crawing")
parser.add_argument('--start', help='date: %y-%m-%d', type=str, default='2019-10-01')
parser.add_argument('--end', help='date: %y-%m-%d', type=str, default='2020-02-21')
parser.add_argument('--id', help='league id', type=int, default=None)
parser.add_argument('--save_dir', help='date', type=str, default='../data/raw/')
args=parser.parse_args()

days = []
start = args.start
end = args.end


if start is None:
    start = datetime.date.today()
else:
    start = datetime.strptime(start, "%Y-%m-%d")
if end is None:
    end = datetime.date.today()+dt.timedelta(days=1)
else:
    end = datetime.strptime(end, "%Y-%m-%d")

if not os.path.exists(args.save_dir):
    os.mkdir(args.save_dir)

def gen_dates(b_date, days):
    day = dt.timedelta(days=1)
    for i in range(days):
        yield b_date + day*i

for d in gen_dates(start, (end-start).days):
        days.append(d.strftime("%Y-%m-%d"))

for day in days:
    url = base_url + str(day)

    # get xml links
    wbdata = requests.get(url).text
    soup = BeautifulSoup(wbdata,'lxml')
    tmps = soup.select("div > a")

    all_links = dict()

    print("Dealing with repilications...")
    for i in tqdm(range(len(tmps))):
        n = tmps[i]
        content = n.get_text()
        link = n.get("href")

        d1 = content[:19]
        n1 = content[20:-4]

        all_links[content] = link
        for _ in all_links.keys():
            if n1 not in _:
                continue
            else:
                d2 = _[:19]
                n2 = _[20:-4]
                dt1 = datetime.strptime(d1,'%Y-%m-%d %H:%M:%S')
                dt2 = datetime.strptime(d2,'%Y-%m-%d %H:%M:%S')
                print('{} -> {}'.format(_, content))
                if dt1 > dt2:
                    all_links.pop(_)
                break

    results_links = []
    match_results_links = []
    standing_links = []
    squads_links = []
    bet_links = []
    prevew_links = []
    others = []

    # save xmls
    contents = list(all_links.keys())
    if args.id is not None:
        contents = [_ for _ in contents if '-'+str(args.id)+'-' in _]

    print("Saving {} files...".format(len(contents)))
    for i in tqdm(range(len(contents))):
        content = contents[i]
        name = content[20:-4]
        link = all_links[content]
        wbdata = requests.get(url).text
        dir_name = 'other'

        # filter the newsest
        if "matchresults" in content:
            match_results_links.append(link)
            dir_name = 'matchresults/'

        elif "squads" in content:
            squads_links.append(link)
            dir_name = 'squads/'

        elif "betfeed" in content:
            bet_links.append(link)
            dir_name = 'betfeeds/'

        elif "standings" in content:
            standing_links.append(link)
            dir_name = 'standings/'

        elif "-results" in content:
            results_links.append(link)
            dir_name = 'results/'

        elif "matchpreview" in content:
            prevew_links.append(link)
            dir_name = 'matchpreviews/'

        else:
            others.append(link)
        
        path = args.save_dir+dir_name+name
        if not os.path.exists(args.save_dir+dir_name):
            os.mkdir(args.save_dir+dir_name)

        furl = file_url+quote(day+'/'+content)
        wbxml = requests.get(furl).text
        with open(path, 'w') as f:
            f.write(wbxml)
