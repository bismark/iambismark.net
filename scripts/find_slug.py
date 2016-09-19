 # -*- coding: utf-8 -*-
import subprocess
import os
import json
from dateutil import parser, tz
from datetime import datetime

def encode(string):
    return string.replace("^", "\\^") \
            .replace("\"", "\\\"") \
            .replace("?", "\\?") \
            .replace("+", "\\+") \
            .replace("*", "\\*") \
            .replace("(", "\\(") \
            .replace(")", "\\)") \
            .replace("[", "\\[") \
            .replace("]", "\\]") \
            .replace("-", "\\-") \
            .replace("`", "\\`") \
            .replace(u"’", "'") \
            .replace(u"“", "\\\"") \
            .replace(u"”", "\\\"") \
            .replace(u"…", "...") \

def run_search(string, ts):
    string = encode(string)
    command = "pt -i \"{}\" iambismark.net/content/post/{}/{}".format(string.encode("utf-8"), ts.strftime("%Y"), ts.strftime("%m"))
    #print command
    return subprocess.check_output(command, shell=True)

def search(string, ts):
    options = []
    res_1 = run_search(string, ts).strip()
    if res_1 != "" and len(res_1.split("\n")) == 1:
        return parse_slug(res_1)
    else:
        options.append(res_1)
        res_2 = run_search(string[:len(string)/2], ts).strip()
        if res_2 != "" and len(res_2.split("\n")) == 1:
            return parse_slug(res_2)
        elif string.startswith("is "):
            res_3 =  run_search(string[3:], ts).strip()
            if res_3 != "" and len(res_3.split("\n")) == 1:
                return parse_slug(res_3)
            else:
                options.append(res_2)
                options.append(res_3)
        else:
            options.append(res_2)

    best_match = None
    for idx, option in enumerate(options):
        if option != "":
            length = len(option.split("\n"))
            if best_match == None:
                best_match = (idx, length)
            elif length < best_match[1]:
                best_match = (idx, length)
    if best_match:
        return present_options(string, ts, options[best_match[0]])
    else:
        return None

def parse_slug(line):
    return os.path.basename(line.split(":", 1)[0]).split(".")[0]

def split_line(line):
    [path, _, text] = line.split(":", 2)
    return (os.path.basename(path).split(".")[0], text)

def present_options(string, ts, results):
    options = [split_line(line) for line in results.split("\n")]
    if all([o[0] == options[0][0] for o in options]):
        return options[0][0]

    print u"Search string: {}".format(string)
    print ts.strftime("%Y-%m-%d")
    for idx, option in enumerate(options):
       slug_datetime = datetime.utcfromtimestamp(int(option[0]))
       print "{}: {} {}".format(idx, slug_datetime.strftime("%Y-%m-%d"), option[1])
    choice = raw_input("choice: ")
    if choice != "":
        return options[int(choice)][0]
    else:
        return None

#filename = "created_note.json"
filename = "status_update.json"
key = 'message'

with open(filename, 'r') as f:
    data = json.load(f)

epoch = datetime.fromtimestamp(1188765812, tz.tzutc())
for post in data:
#for post in data[14:15]:
    if 'slug' in post:
        continue
    try:
        string = post[key]
        ts = parser.parse(post['created_time'])
    except:
        print post['id']
        raise
    if ts < epoch:
        continue
    res = search(string, ts)
    if res:
        #post['slug'] = res
        print res
    else:
        print "https://www.facebook.com/{}/posts/{}".format(*post['id'].split("_")), post[key]
        #pass

#with open(filename, 'w') as f:
#    json.dump(data,f,sort_keys=True,indent=4, separators=(',', ': '))

