from PIL import Image
from jpegtran import JPEGImage
from click import ClickException, echo
import shutil
import os
import tempfile
from subprocess import call
import yaml
from urllib.parse import urlparse
from dateutil import parser
import json
from datetime import datetime
import pathlib
from collections import Counter
import calendar

supported_images = {'JPEG': 'jpg', 'PNG': 'png'}
SITE_PATH = os.path.join(os.getcwd(), 'iambismark.net')
POST_PATH = os.path.join(SITE_PATH, 'content', 'post')
ORIGINAL_IMAGES_PATH = os.path.join(SITE_PATH, 'original_images')
STATIC_MEDIA_PATH = os.path.join(SITE_PATH, 'static', 'post')
WIDTHS = [360, 720, 1200]

def process_image(slug, photo):
    echo(photo)

    if not os.path.isfile(photo):
        raise ClickException("Photo file not found")

    try:
        with Image.open(photo) as im:
            image_format = im.format
            image_size = im.size
    except IOError:
        raise ClickException("Cannot process photo")

    if not image_format in supported_images.keys():
        raise ClickException("Unsupported image type")

    extension = supported_images[image_format]

    original_file_dir = os.path.join(ORIGINAL_IMAGES_PATH, slug)
    if not os.path.isdir(original_file_dir):
        os.mkdir(original_file_dir)
    original_file_path = os.path.join(original_file_dir, '1.{}'.format(extension))
    shutil.copyfile(photo, original_file_path)

    with tempfile.NamedTemporaryFile(suffix=".{}".format(extension), delete=False) as f:
        tempfile_name = f.name

    if image_format == 'JPEG':
        image = JPEGImage(photo)
        orientation = image.exif_orientation
        if orientation and orientation != 1:
            corrected = image.exif_autotransform()
            corrected.save(tempfile_name)
        else:
            image.save(tempfile_name)
    else:
        shutil.copyfile(photo, tempfile_name)

    media_dir = os.path.join(STATIC_MEDIA_PATH, slug)
    if not os.path.isdir(media_dir):
        os.mkdir(media_dir)

    sizes = []
    if image_format == 'JPEG':
        for width in WIDTHS:
            if image_size[0] > width:
                make_thumbnail(media_dir, tempfile_name, width)
                sizes.append(width)
            else:
                make_thumbnail(media_dir, tempfile_name, image_size[0])
                sizes.append(image_size[0])
                break
    elif image_format == 'PNG':
        new_path = os.path.join(media_dir, "1-{}.png".format(image_size[0]))
        call(['zopflipng', tempfile_name, new_path])
        sizes.append(image_size[0])

    os.remove(tempfile_name)
    if sizes == WIDTHS:
        sizes = None

    return extension, sizes

def make_thumbnail(media_dir, tempfile_name, width):
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

    call(['jpeg-recompress', '-m', 'smallfry', '-s', '-Q', new_path, new_path])

def get_imported_tweet_ids():
    status_ids = []
    for root, dirs, files in os.walk(POST_PATH):
        for filename in files:
            if not filename.endswith(".md"):
                continue

            full_path = os.path.join(root, filename)
            metadata = read_metadata_from_path(full_path)

            for url in metadata.get('alturls',[]):
                parsed = urlparse(url)
                if parsed.hostname == 'www.facebook.com':
                    status_ids.append(os.path.basename(parsed.path))
    #print json.dumps(status_ids, indent=4, separators=(',', ': '))
    return status_ids

def find_dupe_social_networks():
    note_urls = []
    for root, dirs, files in os.walk(POST_PATH):
        for filename in files:
            if not filename.endswith(".md"):
                continue

            full_path = os.path.join(root, filename)
            metadata = read_metadata_from_path(full_path)

            alturls = metadata.get('alturls',[])
            counter = Counter()

            for url in alturls:
                parsed = urlparse(url)
                counter[parsed.hostname] += 1
                if parsed.hostname not in ['alpha.app.net', 'twitter.com', 'www.flickr.com', 'www.instagram.com', 'www.facebook.com']:
                    print(parsed.hostname)
            for (_,count) in counter.items():
                if count > 1:
                    print(path_to_slug(full_path))

def read_metadata_from_path(path):
    with open(path, 'r') as f:
        return read_metadata(f)

def read_metadata(f):
    f.readline()
    metadata_yaml = ""
    while True:
        line = f.readline()
        if line.startswith("---"):
            break
        metadata_yaml += line
    return yaml.load(metadata_yaml)

def timestamp_to_slug(timestamp):
    ts = parser.parse(timestamp)
    return str(calendar.timegm(ts.timetuple()))

def timestamp_to_archive(timestamp):
    ts = parser.parse(timestamp)
    return [ts.strftime("%Y-%m")]

def format_timestamp(timestamp):
    ts = parser.parse(timestamp)
    return ts.isoformat()

def path_to_slug(path):
    return pathlib.Path(path).stem

def slug_to_path(slug):
    slug_datetime = datetime.utcfromtimestamp(int(slug))
    path = os.path.join(POST_PATH, str(slug_datetime.year), slug_datetime.strftime("%m"))
    file_path = os.path.join(path, "{}.md".format(slug))
    return file_path

def slug_to_metadata(slug):
    path = slug_to_path(slug)
    metadata = read_metadata_from_path(path)
    return metadata

def update_metadata_slug(slug, metadata):
    path = slug_to_path(slug)
    update_metadata(path, metadata)

def update_metadata(path, metadata):
    with open(path, 'r') as f:
        read_metadata(f)
        text = f.read()
    with open(path, 'w') as f:
        f.write("---\n")
        yaml.safe_dump(metadata, f, encoding='utf-8', default_flow_style=False, indent=4)
        f.write("---\n")
        f.write(text)

def map_posts(func):
    for root, dirs, files in os.walk(POST_PATH):
        for filename in files:
            if not filename.endswith(".md"):
                continue

            full_path = os.path.join(root, filename)
            func(full_path)


def highest_dir(path):
    highest = None
    for entry in os.scandir(path):
        if entry.is_dir() and (highest is None or highest < entry.name):
            highest = entry.name
    return highest


def latest_post():
    year_path = os.path.join(POST_PATH, highest_dir(POST_PATH))
    month_path = os.path.join(year_path, highest_dir(year_path))
    highest_slug = None
    for entry in os.scandir(month_path):
        if entry.is_file():
            root,ext = os.path.splitext(entry.name)
            if ext == '.md':
                if highest_slug is None or highest_slug < root:
                    highest_slug = root
    return highest_slug

def parse_tweet_url(url):
    print(url)
    return os.path.split(urlparse(url).path)[-1]

