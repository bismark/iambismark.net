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
image_dir = os.path.expanduser("~/Desktop/FlickrPhotos")
processed_dir = os.path.join(image_dir, "processed")

with open('flickr_tweets.json', 'r') as f:
    tweets = json.load(f)
    for tweet_id, tweet in tweets.iteritems():
        text = tweet['text']

        metadata = {}
        ts = parser.parse(tweet['timestamp'])
        metadata['date'] = ts.isoformat()
        metadata['slug'] = str(calendar.timegm(ts.timetuple()))
        metadata['archive'] = [ts.strftime("%Y-%m")]
        metadata['alturls'] = [
            "https://twitter.com/bismark/status/{}".format(tweet_id),
            tweet['flickr_url'],
        ]
        metadata['type'] = 'photo'

        year = ts.strftime("%Y")
        month = ts.strftime("%m")

        output_path = os.path.join(output_dir, year, month)
        if not os.path.isdir(output_path):
            os.makedirs(output_path)

        output_filename = os.path.join(output_path, metadata['slug']+".md")
        if os.path.isfile(output_filename):
            print "filename conflict", output_filename
            sys.exit(1)

        #media_file = os.path.join(image_dir, tweet['filename'])
        #ext, sizes = utils.process_image(metadata['slug'], media_file)
        #if ext:
        #    metadata['imagetype'] = ext
        #if sizes:
        #    metadata['imagesizes'] = sizes

        with codecs.open(output_filename, 'w', encoding='utf-8') as output_file:
            output_file.write("---\n")
            yaml.safe_dump(metadata, output_file, encoding='utf-8', default_flow_style=False, indent=4)
            output_file.write("---\n\n")

            output_file.write(text)
            output_file.write("\n\n")

#        os.rename(media_file, os.path.join(processed_dir, tweet['filename']))

