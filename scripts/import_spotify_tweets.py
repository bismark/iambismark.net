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


with open('spotify_tweets.json', 'r') as f:
    tweets = json.load(f)
    for tweet_id, tweet in tweets.iteritems():

        metadata = {}
        ts = parser.parse(tweet['timestamp'])
        metadata['date'] = ts.isoformat()
        metadata['slug'] = str(calendar.timegm(ts.timetuple()))
        metadata['archive'] = [ts.strftime("%Y-%m")]
        metadata['alturls'] = ["https://twitter.com/bismark/status/{}".format(tweet_id)]
        metadata['type'] = 'audio'

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

            if 'track' in tweet:
                output = "{{{{< spotify track=\"{}\" >}}}}".format(tweet['track'])
            else:
                output = "{{{{< spotify album=\"{}\" >}}}}".format(tweet['album'])

            output_file.write(output)

            output_file.write("\n\n")
            output_file.write(tweet['text'])
            output_file.write("\n\n")

