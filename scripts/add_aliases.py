import os
import json
import pytoml as toml

map_path = os.path.join(os.getcwd(), "map.json")
with open(map_path, 'r') as map_file:
    map_json = json.load(map_file)

for root, dirs, files in os.walk(os.getcwd()):
    for filename in files:
        if filename in map_json:
            full_path = os.path.join(root, filename)
            with open(full_path, 'r') as content_file:
                content_file.readline()
                lines = []
                while True:
                    line = content_file.readline()
                    if line.startswith("+++"):
                        break
                    lines.append(line)

                body = content_file.read()
                lines = "".join(lines)
                metadata = toml.loads(lines)
                metadata['aliases'] = map_json[filename]
                with open(full_path + "new", 'w') as output_file:
                    output_file.write("+++\n")
                    toml.dump(metadata)
                    output_file.write("+++\n")
                    output_file.write(body)


