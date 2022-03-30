#!/usr/bin/python3
import requests
from bs4 import BeautifulSoup
import bs4
from datetime import datetime, timezone
import aiohttp
import asyncio


# get the lineup page for today just to get timestamps of all the dates
parms = {'_date':datetime.now().timestamp()}
response = requests.get('https://www.comedycellar.com/line-up/', params=parms)
parsed_html = BeautifulSoup(response.text, features="html.parser")
dates = parsed_html.body.find('select', attrs={'class':'dropkick filter-lineup-shows'})

# dict to hold the comedians and a list of their dates
coms = {}

# get coms compiles all the comedians on the given date
async def get_coms(session, ts):
    url = 'https://www.comedycellar.com/line-up/?_date=' + str(ts) 
    async with session.get(url) as resp:
        html = await resp.text()
        parsed_html = BeautifulSoup(html, features="html.parser")
        lineups = parsed_html.body.find_all('span', attrs={'class':'comedian-block-desc-name'})

        # get all the comedians in the lineups
        for c in lineups:
            # comedian name will be a child
            for ch in c.children:
                # only stringss
                if type(ch) == bs4.element.NavigableString:
                    # stripe the whitesapce
                    com = ch.text.strip()
                    
                    # ignore empty
                    if len(com) == 0:
                        continue

                    # add to existing list or create new
                    try:
                        coms[com].append(datetime.fromtimestamp(int(ts),timezone.utc))
                    except:
                        coms[com] = [datetime.fromtimestamp(int(ts),timezone.utc)]


async def get_com_dates():
    async with aiohttp.ClientSession() as session:

        tasks = []

        # get the comedians for each date
        for date in dates:
            # we only care about tags with the value attr
            if type(date) != bs4.element.Tag:
                continue

            # get the value attr which is the unix TS
            date_ts = date.get('value').strip()

            # async request the lineup for that date timestamp
            tasks.append(asyncio.ensure_future(get_coms(session, date_ts)))

        # wait for requests to finish
        await asyncio.gather(*tasks)

# get all the comedians with asyncio
asyncio.run(get_com_dates())

# compile list of comedians and their dates
out = []
for com in coms:
    # sort timestamps first
    coms[com].sort()
    dates = coms[com]
    line = "{} -".format(com)
    i = 0
    for t in dates:
        if i == 0:
            line = "{} {}".format(line, t.strftime("%m/%d"))
        else:
            line = "{}, {}".format(line, t.strftime("%m/%d"))
        i = i+1

    out.append(line)
    

# sort by name
out.sort()


# print it
for line in out:
    print(line)

