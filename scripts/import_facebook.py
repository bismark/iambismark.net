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

with open('status_update.json', 'r') as f:
    tweets = json.load(f)
    for post in tweets:
        metadata = utils.slug_to_metadata(post['slug'])
        if 'alturls' in metadata:
            if 'permalink_url' in post:
                metadata['alturls'].append(post['permalink_url'])
            else:
                metadata['alturls'] += post['permalink_urls']
        else:
            if 'permalink_url' in post:
                metadata['alturls'] = [post['permalink_url']]
            else:
                metadata['alturls'] = post['permalink_urls']

        utils.update_metadata(post['slug'], metadata)

