import os
import json
import pytoml as toml
from collections import OrderedDict
from datetime import datetime


map_path = os.path.join(os.getcwd(), "map.json")
with open(map_path, 'r') as map_file:
    map_json = json.load(map_file)

blacklist = ['1262240820.md', '1264182740.md']

def convert_file(root, filename, correct_ts, aliases):
    full_path = os.path.join(root, filename)
    with open(full_path, 'r') as content_file:
        content_file.readline()
        metadata = OrderedDict()
        while True:
            line = content_file.readline()
            if line.startswith("+++"):
                break
            if line == "\n":
                continue
            k,v = toml.loads(line).items()[0]
            metadata[k] = v

        body = content_file.read()
        metadata['aliases'] = aliases

    if correct_ts:
        metadata['slug'] = str(correct_ts)
        metadata['date'] = datetime.utcfromtimestamp(correct_ts).isoformat()
        os.remove(full_path)
        full_path = os.path.join(root, metadata['slug'] + ".md")

    with open(full_path, 'w') as output_file:
        output_file.write("+++\n")
        toml.dump(output_file, metadata)
        output_file.write("+++\n")
        output_file.write(body)

for root, dirs, files in os.walk(os.getcwd()):
    for filename in files:
        if filename in map_json and not filename in blacklist:
            convert_file(root, filename, None, map_json[filename])
        elif filename.endswith(".md"):
            correct_ts = int(filename.split(".")[0])
            correct_ts -= 3600
            new_filename = str(correct_ts) + ".md"
            if new_filename in map_json:
                convert_file(root, filename, correct_ts, map_json[new_filename])


