#! /usr/bin/env python

import os
import click
from datetime import datetime
import calendar
import yaml
from subprocess import call

POST_PATH = os.path.join(os.getcwd(), 'iambismark.net', 'content', 'post')
KINDS = ['link', 'quote', 'video', 'answer', 'photo', 'audio']

@click.command()
@click.option('--kind', default=None, type=click.Choice(KINDS))
@click.option('--title', default=None)
def new_post(kind, title):
    now = datetime.utcnow().replace(microsecond=0)
    metadata = {}
    metadata["date"] = now.isoformat()
    metadata["slug"] = str(calendar.timegm(now.timetuple()))
    metadata["archive"] = [now.strftime("%Y-%m")]

    post_dir = os.path.join(POST_PATH, now.strftime("%Y"), now.strftime("%m"))
    if not os.path.isdir(post_dir):
        os.makedirs(post_dir)
    filename = "{}.md".format(metadata['slug'])
    file_path = os.path.join(post_dir, filename)
    if os.path.isfile(file_path):
        raise click.ClickException("File name conflict")

    if kind == 'photo':
        metadata['imagealt'] = ''
        metadata['imagetype'] = ''
    elif kind == 'link':
        metadata['link'] = ''
        metadata['title'] = ''

    if title:
        metadata['title'] = title.encode('utf-8')

    with open(file_path, 'w') as f:
        f.write("---\n")
        yaml.dump(metadata, f, encoding='utf-8')
        f.write("---\n\n")

    call(['vim', file_path])

if __name__ == '__main__':
    new_post()
