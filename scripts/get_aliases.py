import os
from datetime import datetime
import calendar
import json
import requests

files = os.listdir(os.getcwd())

metadata = {}

for filename in files:
    if os.path.isdir(filename):
        continue
    with open(filename, 'r') as input_file:
        print filename
        file_json = json.load(input_file)
        slug = str(file_json['timestamp']) + ".md"
        post_id = file_json['id']
        post_slug = file_json['slug']
        urls = [u'/post/{}'.format(post_id), u'/post/{}/{}'.format(post_id, post_slug)]
        metadata[slug] = urls

with open('map.json', 'w') as output_file:
    json.dump(metadata, output_file)

