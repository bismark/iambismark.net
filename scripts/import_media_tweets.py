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
image_dir = os.path.expanduser("~/Desktop/TweetPhotos")
processed_dir = os.path.join(image_dir, "processed")

post = """
    [
    {
        "application": {
            "name": "Twitter"
        },
        "created_time": "2012-01-14T02:57:47+0000",
        "id": "17803937_10100289073880599",
        "link": "http://t.co/qpIYpAmN",
        "message": "waiting for the luau.",
        "permalink_url": "https://www.facebook.com/17803937/posts/10100289073880599",
        "status_type": "published_story",
        "filename": "IMG_1104.JPG",
        "tweet_id": "158019945467363328",
        "type": "link"
    }
    ]
"""

#with open('media_tweets.json', 'r') as f:
def foo():
    tweets = json.loads(post)
    for tweet in tweets:
        if os.path.isfile(os.path.join(processed_dir, tweet['filename'])):
            continue
        #indices = tweet['entities']['media'][0]['indices']
        #text = tweet['text']
        #text = text[:indices[0]].strip() + text[indices[1]:].strip()

        metadata = {}
        ts = parser.parse(tweet['created_time'])
        metadata['date'] = ts.isoformat()
        metadata['slug'] = str(calendar.timegm(ts.timetuple()))
        metadata['archive'] = [ts.strftime("%Y-%m")]
        metadata['alturls'] = ["https://twitter.com/bismark/status/{}".format(tweet['tweet_id'], tweet['permalink_url'])]
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

        media_file = os.path.join(image_dir, tweet['filename'])
        ext, sizes = utils.process_image(metadata['slug'], media_file)
        metadata['imagetype'] = ext
        if sizes:
            metadata['imagesizes'] = sizes

        with codecs.open(output_filename, 'w', encoding='utf-8') as output_file:
            output_file.write("---\n")
            yaml.safe_dump(metadata, output_file, encoding='utf-8', default_flow_style=False, indent=4)
            output_file.write("---\n\n")

            output_file.write(text)
            output_file.write("\n")

        #os.rename(media_file, os.path.join(processed_dir, tweet['filename']))

foo()
