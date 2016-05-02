import os
from datetime import datetime
import calendar

#files = ["2009-12-12-testing-out-the-new-blog.md"]
files = os.listdir(os.getcwd())

output_dir = os.path.join(os.getcwd(), "converted")

for filename in files:
    if filename.endswith(".rst"):
        continue

    if os.path.isdir(filename):
        continue

    with open(filename, 'r') as input_file:
        metadata = {}
        for line in input_file:
            if line == "\n":
                break
            if line.startswith("Author") or \
               line.startswith("Status") or \
               line.startswith("Slug"):
               continue
            parts = [x.strip() for x in line.split(":", 1)]
            parts[0] = parts[0].lower()
            if parts[0] == "date":
                date = datetime.strptime(parts[1], "%Y-%m-%d %H:%M:%S")
                parts[1] = date.isoformat()
                metadata['slug'] = str(calendar.timegm(date.timetuple()))
                metadata['archive'] = [date.strftime("%Y-%m")]

            if parts[0] == "category":
                parts[0] = "type"

            if parts[0] == "tags":
                parts[1] = [parts[1]]

            metadata[parts[0]] = parts[1]

        if metadata['title'].lower() == metadata['type']:
            del metadata['title']
        if metadata['type'] == "text":
            del metadata['type']


        output_filename = os.path.join(output_dir, metadata['slug']+".md")
        with open(output_filename, 'w') as output_file:
            output_file.write("+++\n")
            for k,v in metadata.iteritems():
                if type(v) is list:
                    output_file.write("{} = [{}]\n".format(k, ",".join(["\"{}\"".format(v2) for v2 in v])))
                else:
                    output_file.write("{} = \"{}\"\n".format(k, v))
            output_file.write("+++\n")
            output_file.write("\n")
            for line in input_file:
                output_file.write(line)









