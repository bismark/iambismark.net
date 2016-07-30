#! /usr/bin/env python

import codecs
import json
from dateutil import parser
from hugo_helper import utils
import calendar

import os
import sys
import yaml

output_dir = os.path.join(os.getcwd(), "iambismark.net", "content", "post")

def parse_new(tweet):
    url = tweet['entities']['urls'][0]['expanded_url']
    indices = tweet['entities']['urls'][0]['indices']
    text = tweet['text']
    text = text[:indices[0]].strip() + text[indices[1]:].strip()
    return url, text

def parse_old(tweet):
    url = tweet['url']
    text = tweet['text']
    return url, text


with open('old_url_tweets.json', 'r') as f:
    tweets = json.load(f)
    for tweet_id, tweet in tweets.iteritems():
        url, text = parse_old(tweet)

        metadata = {}
        ts = parser.parse(tweet['timestamp'])
        metadata['date'] = ts.isoformat()
        metadata['slug'] = str(calendar.timegm(ts.timetuple()))
        metadata['archive'] = [ts.strftime("%Y-%m")]
        metadata['alturls'] = ["https://twitter.com/bismark/status/{}".format(tweet_id)]
        metadata['type'] = 'link'
        metadata['title'] = tweet['title']
        if 'tags' in tweet:
            metadata['tags'] = tweet['tags']
        metadata['link'] = url

        year = ts.strftime("%Y")
        month = ts.strftime("%m")

        output_path = os.path.join(output_dir, year, month)
        if not os.path.isdir(output_path):
            os.makedirs(output_path)

        output_filename = os.path.join(output_path, metadata['slug']+".md")
        if os.path.isfile(output_filename):
            print "filename conflict", output_filename
            sys.exit(1)


        with codecs.open(output_filename, 'w', encoding='utf-8') as output_file:
            output_file.write("---\n")
            yaml.safe_dump(metadata, output_file, encoding='utf-8', default_flow_style=False, indent=4)
            output_file.write("---\n\n")

            output_file.write(text)
            output_file.write("\n\n")

