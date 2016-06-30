#! /usr/bin/env python

import os
import shutil
import click
from datetime import datetime
import calendar
import yaml
from subprocess import call
from PIL import Image
from jpegtran import JPEGImage
import tempfile

SITE_PATH = os.path.join(os.getcwd(), 'iambismark.net')
POST_PATH = os.path.join(SITE_PATH, 'content', 'post')
ORIGINAL_IMAGES_PATH = os.path.join(SITE_PATH, 'original_images')
STATIC_MEDIA_PATH = os.path.join(SITE_PATH, 'static', 'post')
KINDS = ['link', 'quote', 'video', 'answer', 'photo', 'audio']
WIDTHS = [1200, 720, 360]

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
            process_photo(metadata['slug'], photo)
            metadata['imagetype'] = 'jpg'
        else:
            metadata['imagetype'] = ''

        metadata['imagealt'] = ''
    elif kind == 'link':
        metadata['link'] = ''
        metadata['title'] = ''

    if kind != None:
        metadata['kind'] = kind

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

def process_photo(slug, photo):
    if not os.path.isfile(photo):
        raise click.ClickException("Photo file not found")

    try:
        with Image.open(photo) as im:
            image_format = im.format
            image_size = im.size
    except IOError:
        raise click.ClickException("Cannot process photo")

    if image_format != 'JPEG':
        raise click.ClickExcpetion("Unsupported image type")


    original_file_dir = os.path.join(ORIGINAL_IMAGES_PATH, slug)
    if not os.path.isdir(original_file_dir):
        os.mkdir(original_file_dir)
    original_file_path = os.path.join(original_file_dir, '1.jpg')
    shutil.copyfile(photo, original_file_path)

    image = JPEGImage(photo)

    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        tempfile_name = f.name

    orientation = image.exif_orientation
    if orientation and orientation != 1:
        corrected = image.exif_autotransform()
        corrected.save(tempfile_name)
    else:
        image.save(tempfile_name)

    media_dir = os.path.join(STATIC_MEDIA_PATH, slug)
    if not os.path.isdir(media_dir):
        os.mkdir(media_dir)

    for width in WIDTHS:
        if image_size[0] >= width:

            new_path = os.path.join(media_dir, "1-{}.jpg".format(width))
            shutil.copyfile(tempfile_name, new_path)
            call(['mogrify',
                '-filter', 'Triangle',
                '-define', 'filter:support=2',
                '-thumbnail', str(width),
                '-unsharp', '0.25x0.08+8.3+0.045',
                '-dither', 'None',
                '-posterize', '136',
                '-quality', '82',
                '-define', 'jpeg:fancy-upsampling=off',
                '-define', 'png:compression-filter=5',
                '-define', 'png:compression-level=9',
                '-define', 'png:compression-strategy=1',
                '-define', 'png:exclude-chunk=all',
                '-interlace', 'none',
                '-colorspace', 'sRGB',
                new_path])
            call(['jpeg-recompress',
            '-m', 'smallfry',
            '-s',
            '-Q',
            new_path,
            new_path])
    os.remove(tempfile_name)

