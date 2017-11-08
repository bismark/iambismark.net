#! /usr/bin/env python

import webbrowser
import os
import shutil
import click
from datetime import datetime
import calendar
import yaml
from subprocess import call
from dateutil import parser
import twitter

from hugo_helper import utils

SITE_PATH = os.path.join(os.getcwd(), 'iambismark.net')
POST_PATH = os.path.join(SITE_PATH, 'content', 'post')
KINDS = ['link', 'quote', 'video', 'answer', 'photo', 'audio']

@click.group()
def cli():
    pass

@cli.command()
@click.option('--output', default=lambda: os.path.expanduser('~/.twitter_oauth'))
def auth_twitter(output):
    consumer_key = os.environ.get('TWITTER_CONSUMER_KEY')
    consumer_secret = os.environ.get('TWITTER_CONSUMER_SECRET')
    click.echo(consumer_key)
    click.echo(consumer_secret)
    click.echo(output)
    twitter.oauth_dance("twitter", consumer_key, consumer_secret, output)

@cli.command()
@click.option('--tweet', prompt='Tweet required!')
@click.option('--auth', default=lambda: os.path.expanduser('~/.twitter_oauth'))
def import_tweet(tweet, auth):
    tweet_id = utils.parse_tweet_url(tweet)
    consumer_key = os.environ.get('TWITTER_CONSUMER_KEY')
    consumer_secret = os.environ.get('TWITTER_CONSUMER_SECRET')
    token, token_secret = twitter.read_token_file(auth)
    t = twitter.Twitter(auth=twitter.OAuth(token, token_secret, consumer_key, consumer_secret))
    print(tweet_id)
    print(t.statuses.show(_id=tweet_id, trim_user=True))


@cli.command()
def latest_post():
    slug = utils.latest_post()
    date = datetime.utcfromtimestamp(int(slug))
    click.echo(date.isoformat())

@cli.command()
@click.option('--slug', default=None)
@click.option('--kind', default=None, type=click.Choice(KINDS))
@click.option('--title', default=None)
@click.option('--photo', default=None)
def new_post(slug, kind, title, photo):
    if slug:
        try:
            now = parser.parse(slug)
        except ValueError:
            now = datetime.utcfromtimestamp(int(slug))
    else:
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
            ext = utils.process_image(metadata['slug'], photo)[0]
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

    with open(file_path, 'r') as f:
        metadata = utils.read_metadata(f)
        body = f.read()

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
    file_path = utils.slug_to_path(slug)
    call(['vim', file_path])

@cli.command()
@click.argument('slug')
def open_post(slug):
    url = 'localhost:1313/post/{}'.format(slug)
    webbrowser.open(url)


@cli.command()
def print_tweet_ids():
    utils.get_imported_tweet_ids()

