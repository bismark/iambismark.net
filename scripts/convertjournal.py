import os
import re
import sys
import json
from datetime import datetime
import calendar

#files = ["well-i-graduated.md"]
files = os.listdir(os.getcwd())

output_dir = os.path.join(os.getcwd(), "converted")

comment_start = re.compile('^[0-9]{1,2}\) (.+) on ([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})$')
commenter_website = re.compile('^\[(.*)\]\((.*)\)$')

output_comments_filename = os.path.join(output_dir, "comments.md")

all_comments = []

for filename in files:

    if os.path.isdir(filename):
        continue

    print filename

    with open(filename, 'r') as input_file:
        metadata = {}

        metadata['title'] = input_file.readline().strip("\n# ")
        input_file.readline()

        while True:
            line = input_file.readline()
            if line == "\n":
                break
            parts = [x.strip() for x in line.split(":", 1)]
            parts[0] = parts[0].lower()
            if parts[0] == "published on":
                date = datetime.strptime(parts[1], "%Y-%m-%d %H:%M:%S")
                parts[1] = date.isoformat()
                parts[0] = "date"
                metadata['slug'] = str(calendar.timegm(date.timetuple()))
                metadata['archive'] = [date.strftime("%Y-%m")]

            if parts[0] == "category":
                parts[0] = "tags"
                parts[1] = [parts[1]]

            metadata[parts[0]] = parts[1]

        output_filename = os.path.join(output_dir, metadata['slug']+".md")
        with open(output_filename, 'w') as output_file:
            output_file.write("+++\n")
            for k,v in metadata.iteritems():
                if type(v) is list:
                    output_file.write("{} = [{}]\n".format(k, ",".join(["\"{}\"".format(v2) for v2 in v])))
                else:
                    v = v.replace("\"", "\\\"")
                    output_file.write("{} = \"{}\"\n".format(k, v))
            output_file.write("+++\n")
            output_file.write("\n")
            while True:
                line = input_file.readline()
                if line.startswith("comments:"):
                    break
                output_file.write(line)

        next_line = None
        while True:
            next_line = input_file.readline()
            if next_line.strip() != "":
                break

        if next_line.startswith("no comments"):
            continue

        lines = input_file.readlines()
        lines.insert(0, next_line)

        line_starts = [a[0] for a in enumerate(lines) if comment_start.match(a[1].strip()) != None]
        comments = [lines[a[1]:line_starts[a[0]+1]] for a in enumerate(line_starts[:-1])]
        comments.append(lines[line_starts[-1]:])

        parsed_comments = []
        for comment in comments:
            matched = comment_start.match(comment[0].strip())
            groups = matched.groups()
            name = groups[0]
            date = datetime.strptime(groups[1], "%Y-%m-%d %H:%M:%S").isoformat()
            text = "".join([l.replace("\n", " ") for l in comment[1:]]).strip()


            website = None
            website_match = commenter_website.match(name)
            if website_match:
                groups = website_match.groups()
                name = groups[0]
                website = groups[1]

            parsed_comments.append({'name': name, 'website': website, 'date': date, 'text': text})

        all_comments.append(
                {
                    'title': metadata['title'],
                    'slug': metadata['slug'],
                    'date': metadata['date'],
                    'comments': parsed_comments,
                }
        )

with open(output_comments_filename, 'w') as comments_file:
    json.dump(all_comments, comments_file)

