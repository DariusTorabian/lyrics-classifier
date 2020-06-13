#!/usr/bin/env python
# coding: utf-8

'''
This module scrapes lyrics and songtitles of a given artist and saves them
in a JSON file.
'''

import random
from time import sleep
import re
import argparse
import warnings
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
import pandas as pd

warnings.filterwarnings("ignore")

s = requests.Session()
adapter = HTTPAdapter(max_retries=10)
s.mount('http://', adapter)
s.mount('https://', adapter)
s.get('https://www.lyrics.com')


def get_soup_songpage(link):
    '''
    Gets soup of songpage from provided sublink
    '''
    response_songpage = s.get("https://www.lyrics.com/" + link)
    soup_songpage = BeautifulSoup(response_songpage.text)
    sleep(random.uniform(0.3, 0.5))
    return soup_songpage

def get_lyrics(soup_songpage):
    '''
    Gets lyrics from soup of one songpage.
    '''
    lyric_text = soup_songpage.find(id="lyric-body-text")
    return lyric_text.text

def get_title(soup_songpage):
    '''
    Gets titles from soup of one songpage.
    '''
    lyric_title = soup_songpage.find(class_="lyric-title")
    return lyric_title.text

def get_songlinks(artisturl):
    '''
    Get songlinks from artistpage. Input is artisturl of lyrics.com,
    output is list of sublinks to songpages.
    '''
    response_artistpage = s.get(artisturl)
    soup_artistpage = BeautifulSoup(response_artistpage.text)
    sleep(random.uniform(0.1, 0.3))
    temp = []
    pattern = re.compile("/lyric/.+?(?=\")")
    for el in soup_artistpage.find_all("a"):
        temp.append(el)
        links = re.findall(pattern, str(temp))
    return links

def get_titlesandlyrics(artisturl, fileoutput):
    '''
    Get titles and lyrics from an artist.
    Input URL of lyrics.com artistpage and a filename for json.
    Output is a DataFrame and a json file.
    '''
    songlinks = get_songlinks(artisturl)
    dictionary_result = {"title":[], "lyrics":[]}
    x = 0
    skipped_songs = 0
    for link in songlinks[:-1]:
        try:
            soup_songpage = get_soup_songpage(link)
            song_title = get_title(soup_songpage)
            song_lyrics = get_lyrics(soup_songpage)
            if song_title not in dictionary_result["title"]:
                dictionary_result["title"].append(song_title)
                dictionary_result["lyrics"].append(song_lyrics)
                x += 1
                print(f"Saved {x} of {len(songlinks)-skipped_songs} songs.")
            else:
                print(f"Song named {song_title} already crawled, skipped.")
                skipped_songs += 1
        except Exception:
            print(f"Something went wrong with number {x}.")
    print(f"Saved {x} songs and skipped {skipped_songs} duplicates.")
    df = pd.DataFrame(data=dictionary_result)
    df.to_json("data/"+fileoutput+'.json')
    print(f"Crawled songs have been saved in './data/{fileoutput}.json'.")
    return df

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Scrapes lyrics from lyrics.com. Please provide the following arguments:')
    parser.add_argument('artisturl', help='lyrics.com artist page url, e.g. "https://www.lyrics.com/artist/Eminem/347307"')
    parser.add_argument('fileoutput', help='filename for .json output, e.g. "Eminem"')
    args = parser.parse_args()

    from pyfiglet import Figlet
    f = Figlet(font="graffiti")

    print(f.renderText('Lyrics Scraper 9000'))
    print(f"Lyrics scraper initialized with artisturl {args.artisturl}.")
    print(f"Lyrics will be saved in ./data/{args.fileoutput}.json.")
    get_titlesandlyrics(args.artisturl, args.fileoutput)
