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


with open('youtube_posts.json', 'r') as f:
    tweets = json.load(f)
    for tweet in tweets:
        if 'slug' in tweet:
            continue

        metadata = {}
        ts = parser.parse(tweet['created_time'])
        metadata['date'] = ts.isoformat()
        metadata['slug'] = str(calendar.timegm(ts.timetuple()))
        metadata['archive'] = [ts.strftime("%Y-%m")]
        metadata['alturls'] = [tweet['permalink_url']]

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

            if 'url' in tweet:
                output = "{{{{< youtube_nocookie {} >}}}}".format(tweet['url'])
                output_file.write(output)
                output_file.write("\n\n")
                #output_file.write(tweet['text'])
                #output_file.write("\n\n")
            else:
                for url in tweet['urls']:
                    output = "{{{{< youtube_nocookie {} >}}}}".format(url)
                    output_file.write(output)
                    output_file.write("\n\n")

