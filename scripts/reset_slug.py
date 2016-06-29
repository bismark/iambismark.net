#! /usr/bin/env python

import os
import click
from datetime import datetime
import calendar
import yaml

POST_PATH = os.path.join(os.getcwd(), 'iambismark.net', 'content', 'post')

@click.command()
@click.argument('slug')
def reset_slug(slug):
    slug_datetime = datetime.utcfromtimestamp(int(slug))
    path = os.path.join(POST_PATH, str(slug_datetime.year), slug_datetime.strftime("%m"))

    file_path = os.path.join(path, "{}.md".format(slug))
    if not os.path.isfile(file_path):
        raise click.ClickException("File not foud")

    metadata_yaml = ""
    with open(file_path, 'r') as f:
        f.readline()
        while True:
            line = f.readline()
            if line.startswith("---"):
                break
            metadata_yaml += line
        body = f.read()
    metadata = yaml.load(metadata_yaml)

    now = datetime.utcnow().replace(microsecond=0)
    metadata["date"] = now.isoformat()
    metadata["slug"] = str(calendar.timegm(now.timetuple()))
    metadata["archive"] = [now.strftime("%Y-%m")]

    new_filename = "{}.md".format(metadata['slug'])
    new_file_path = os.path.join(path, new_filename)
    if os.path.isfile(new_file_path):
        raise click.ClickException("File name conflict")

    with open(new_file_path, 'w') as f:
        f.write("---\n")
        yaml.dump(metadata, f, encoding='utf-8')
        f.write("---\n")
        f.write(body)

    os.remove(file_path)

if __name__ == '__main__':
    reset_slug()

