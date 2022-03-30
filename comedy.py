#!/usr/bin/python3
import requests
from bs4 import BeautifulSoup
import bs4
from datetime import datetime, timezone

# get the lineup page for today just to get timestamps of all the dates
parms = {'_date':datetime.now().timestamp()}
response = requests.get('https://www.comedycellar.com/line-up/', params=parms)
parsed_html = BeautifulSoup(response.text, features="html.parser")
dates = parsed_html.body.find('select', attrs={'class':'dropkick filter-lineup-shows'})

# dict to hold the comedians and a list of their dates
coms = {}

# get the comedians for each date
for date in dates:
    # we only care about tags with the value attr
    if type(date) != bs4.element.Tag:
        continue
    # get the value attr which is the unix TS
    date_ts = date.get('value').strip()

    print(".")
    # request to linupe for that date timestamp
    parms = {'_date':date_ts}
    response = requests.get('https://www.comedycellar.com/line-up/', params=parms)
    parsed_html = BeautifulSoup(response.text, features="html.parser")
    lineups = parsed_html.body.find_all('span', attrs={'class':'comedian-block-desc-name'})

    # get all the comedians in the lineups
    for c in lineups:
        # comedian name will be a child
        for ch in c.children:
            # only stringss
            if type(ch) == bs4.element.NavigableString:
                # stripe the whitesapce
                com = ch.text.strip()
                
                # ignore empry
                if len(com) == 0:
                    continue

                # add to existing list or create new
                try:
                    coms[com].append(datetime.fromtimestamp(int(date_ts),timezone.utc))
                except:
                    coms[com] = [datetime.fromtimestamp(int(date_ts),timezone.utc)]

print("")

# compile list of comedians and their earliest next date
out = []
for com in coms:
    date = coms[com][0].strftime("%Y-%m-%d")
    out.append("{} {}".format(com, date))

# sort by name
out.sort()

# print it
for line in out:
    print(line)

