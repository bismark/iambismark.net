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

with open('dupes.json', 'r') as f:
    tweets = json.load(f)
    for tweet in tweets:
        metadata = utils.slug_to_metadata(tweet['slug'])
        if 'alturls' in metadata:
            metadata['alturls'].append("https://alpha.app.net/bismark/post/{}".format(tweet['id']))
        else:
            metadata['alturls'] = ["https://alpha.app.net/bismark/post/{}".format(tweet['id'])]

        utils.update_metadata(tweet['slug'], metadata)



        #os.rename(media_file, os.path.join(processed_dir, tweet['filename']))

