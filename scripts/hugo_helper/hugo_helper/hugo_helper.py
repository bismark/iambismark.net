#! /usr/bin/env python

import webbrowser
import os
import shutil
import click
from datetime import datetime
import calendar
import yaml
from subprocess import call

import utils

SITE_PATH = os.path.join(os.getcwd(), 'iambismark.net')
POST_PATH = os.path.join(SITE_PATH, 'content', 'post')
KINDS = ['link', 'quote', 'video', 'answer', 'photo', 'audio']

@click.group()
def cli():
    pass

@cli.command()
@click.option('--kind', default=None, type=click.Choice(KINDS))
@click.option('--title', default=None)
@click.option('--photo', default=None)
def new_post(kind, title, photo):
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
        if photo:
            ext = utils.process_photo(metadata['slug'], photo)[0]
            metadata['imagetype'] = ext
        else:
            metadata['imagetype'] = ''

        metadata['imagealt'] = ''
    elif kind == 'link':
        metadata['link'] = ''
        metadata['title'] = ''

    if kind != None:
        metadata['type'] = kind

    if title:
        metadata['title'] = title.encode('utf-8')

    with open(file_path, 'w') as f:
        f.write("---\n")
        yaml.dump(metadata, f, encoding='utf-8')
        f.write("---\n\n")

    call(['vim', file_path])

@cli.command()
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

@cli.command()
@click.argument('slug')
def edit_post(slug):
    slug_datetime = datetime.utcfromtimestamp(int(slug))
    path = os.path.join(POST_PATH, str(slug_datetime.year), slug_datetime.strftime("%m"))
    file_path = os.path.join(path, "{}.md".format(slug))
    call(['vim', file_path])

@cli.command()
@click.argument('slug')
def open_post(slug):
    url = 'localhost:1313/post/{}'.format(slug)
    webbrowser.open(url)




