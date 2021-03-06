import argparse
import json
import logging
import os
import subprocess
import tempfile
import time
import math
import shutil

import PIL.Image
import PIL.ImageFilter
import PIL.ImageChops
import PIL.ImageStat


_logger = logging.getLogger(__name__)


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('image_filename', nargs='*')
    arg_parser.add_argument('--debug-image', action='store_true')
    arg_parser.add_argument('--diff-threshold', type=int, default=5)
    arg_parser.add_argument('--max-threshold', type=int, default=150)
    arg_parser.add_argument('--positive-only', action='store_true')
    arg_parser.add_argument('--concise', action='store_true')
    arg_parser.add_argument('--save-screenshot-filename')
    arg_parser.add_argument('--url-cache-filename')
    args = arg_parser.parse_args()
    logging.basicConfig(level=logging.INFO)

    if not args.image_filename:
        temp_dir = tempfile.TemporaryDirectory(suffix='-tppip')
        temp_filename = os.path.join(temp_dir.name,
                                     str(int(time.time())) + '.png')

        url = get_stream_url(args.url_cache_filename)

        subprocess.check_call([
            'ffmpeg', '-i', url, '-vframes', '1', '-f', 'image2', temp_filename
        ])

        if args.save_screenshot_filename:
            dest_new_filename = args.save_screenshot_filename + '-new'
            shutil.copy2(temp_filename, dest_new_filename)
            os.rename(dest_new_filename, args.save_screenshot_filename)

        filenames = [temp_filename]
    else:
        filenames = args.image_filename

    for filename in filenames:
        _logger.info('Analyzing %s', filename)

        result_doc = analyze_image(
            filename, args.diff_threshold, args.max_threshold,
            debug_image=args.debug_image)

        token_detected = any(
            button_doc['token_detected']
            for button_doc in result_doc['buttons'].values()
        )

        if not args.positive_only or args.positive_only and token_detected:
            if args.concise:
                diff_mean_value = max(
                    button_doc['pixel_diff_mean']
                    for button_doc in result_doc['buttons'].values()
                )
                diff_max_value = max(
                    button_doc['pixel_diff_max']
                    for button_doc in result_doc['buttons'].values()
                )
                print(result_doc['filename'], diff_mean_value, diff_max_value)
            else:
                print(json.dumps(result_doc))


def get_stream_url(cache_filename=None):
    _logger.info('Getting stream url...')

    if cache_filename and os.path.isfile(cache_filename) and \
            time.time() - os.path.getmtime(cache_filename) < 60 * 5:
        with open(cache_filename) as file:
            _logger.info('Got stream url from cache')
            return file.read().strip()

    url = subprocess.check_output([
        'livestreamer', 'twitch.tv/twitchplayspokemon',
        'best',
        '--stream-url', '--hls-live-edge', '1',
    ]).decode('utf-8').strip()

    if cache_filename:
        with open(cache_filename, 'w') as file:
            file.write(url)

    _logger.info('Got stream url')

    return url


def analyze_image(filename, diff_threshold, max_threshold, debug_image=False,
                  sanity_threshold=30):
    image = PIL.Image.open(filename)

    scale = image.size[0] / 1920

    # Check for black pixels above timer
    sanity_check_x = round(1526 * scale)
    sanity_check_y = round(920 * scale)
    sanity_check_width = round(60 * scale)
    sanity_check_height = round(4 * scale)

    sanity_sample_image = image.crop(
        (sanity_check_x, sanity_check_y,
         sanity_check_x + sanity_check_width,
         sanity_check_y + sanity_check_height))

    sanity_stats = PIL.ImageStat.Stat(sanity_sample_image)
    sanity_mean_value = sum(sanity_stats.mean[:3]) / 3

    sanity_ok = sanity_mean_value <= sanity_threshold

    if not sanity_ok:
        _logger.warning('%s does not appear to be a sidegame image (value %s)',
                        filename, sanity_mean_value)

    # Crop for the space where token bribes appear
    crop_x = round(1622 * scale)
    crop_y = round(916 * scale)
    crop_width = round(16 * scale)
    crop_height = round(160 * scale)

    processed_image = image.crop(
        (crop_x, crop_y, crop_x + crop_width, crop_y + crop_height))
    processed_image = PIL.Image.eval(processed_image, lambda x: 0 if x < 50 else x)

    if debug_image:
        processed_image.save(filename + '.debug-crop.png', 'PNG')

    processed_image = processed_image.filter(PIL.ImageFilter.FIND_EDGES)

    row_height = crop_height / 10
    button_labels = tuple(['a', 'b', 'up', 'down', 'left', 'right', 'start',
                           'select', 'l', 'r'])

    result_doc = {
        'filename': filename,
        'buttons': {},
        'sanity_mean_value': sanity_mean_value,
    }

    snippet_width = crop_width - 2
    snippet_height = 2

    snippet_x = 1

    for row, button_label in enumerate(button_labels):
        row_y = math.ceil(row * row_height)

        # Grab some rows of pixels within the input row
        y1 = row_y + math.ceil(4 * scale)
        snippet_1 = processed_image.crop(
            (snippet_x, y1, snippet_x + snippet_width, y1 + snippet_height))

        # Then near the bottom of the input row
        y2 = row_y + math.floor(10 * scale)
        snippet_2 = processed_image.crop(
            (snippet_x, y2, snippet_x + snippet_width, y2 + snippet_height))

        # If they are different, then it must be text and not the vote tally
        # bar
        diff_image = PIL.ImageChops.difference(snippet_1, snippet_2)

        if debug_image:
            row_overlay = PIL.Image.new('RGB', (snippet_width, snippet_height), (255, 0, 0))

            processed_image.paste(row_overlay, (snippet_x, y1), diff_image.convert('L'))
            processed_image.paste(row_overlay, (snippet_x, y2), diff_image.convert('L'))

        diff_stats = PIL.ImageStat.Stat(diff_image)
        mean_value = sum(diff_stats.mean[:3]) / 3
        max_value = sum(item[1] for item in diff_stats.extrema[:3]) / 3
        token_detected = mean_value > diff_threshold and max_value > max_threshold and sanity_ok

        result_doc['buttons'][button_label] = {
            'row': row,
            'token_detected': token_detected,
            'pixel_diff_mean': mean_value,
            'pixel_diff_max': max_value,
        }

    if debug_image:
        processed_image.save(filename + '.debug.png', 'PNG')

    return result_doc


if __name__ == '__main__':
    main()
