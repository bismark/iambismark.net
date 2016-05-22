#! /usr/bin/env python
import os
import json
import pytoml as toml
from datetime import datetime
from collections import OrderedDict

blacklist = ['1262240820.md', '1264182740.md']

def convert_file(root, filename):
    full_path = os.path.join(root, filename)
    with open(full_path, 'r') as content_file:
        content_file.readline()
        metadata = {}
        while True:
            line = content_file.readline()
            if line.startswith("+++"):
                break
            if line == "\n":
                continue
            k,v = toml.loads(line).items()[0]
            metadata[k] = v

        metadata = OrderedDict(sorted(metadata.items(), key=lambda t: t[0]))

        body = content_file.read()

    with open(full_path, 'w') as output_file:
        output_file.write("+++\n")
        toml.dump(output_file, metadata)
        output_file.write("+++\n")
        output_file.write(body)

for root, dirs, files in os.walk(os.getcwd()):
    for filename in files:
        if not filename in blacklist and filename.endswith(".md"):
            convert_file(root, filename)

