from PIL import Image
from jpegtran import JPEGImage
from click import ClickException, echo
import shutil
import os
import tempfile
from subprocess import call

supported_images = {'JPEG': 'jpg', 'PNG': 'png'}
SITE_PATH = os.path.join(os.getcwd(), 'iambismark.net')
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

