import argparse
import json
import os
import subprocess
import tempfile
import atexit
import time
import math
import shutil

import PIL.Image
import PIL.ImageFilter
import PIL.ImageChops
import PIL.ImageStat


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('image_filename', nargs='*')
    arg_parser.add_argument('--debug-image', action='store_true')
    arg_parser.add_argument('--diff-threshold', type=int, default=20)
    arg_parser.add_argument('--max-threshold', type=int, default=150)
    arg_parser.add_argument('--positive-only', action='store_true')
    arg_parser.add_argument('--concise', action='store_true')
    arg_parser.add_argument('--save-screenshot-filename')
    args = arg_parser.parse_args()

    if not args.image_filename:
        temp_dir = tempfile.TemporaryDirectory(suffix='-tppip')
        temp_filename = os.path.join(temp_dir.name,
                                     str(int(time.time())) + '.png')
        url = subprocess.check_output([
            'livestreamer', 'twitch.tv/twitchplayspokemon',
            'best',
            '--stream-url', '--hls-live-edge', '1',
            ]).decode('utf-8').strip()

        subprocess.check_call([
            'ffmpeg', '-i', url, '-vframes', '1', '-f', 'image2', temp_filename
        ])

        if args.save_screenshot_filename:
            shutil.copy2(temp_filename, args.save_screenshot_filename)

        filenames = [temp_filename]
    else:
        filenames = args.image_filename

    for filename in filenames:
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


def analyze_image(filename, diff_threshold, max_threshold, debug_image=False):
    image = PIL.Image.open(filename)

    scale = image.size[0] / 1920

    crop_x = round(1616 * scale)
    crop_y = round(916 * scale)
    crop_width = round(16 * scale)
    crop_height = round(160 * scale)

    processed_image = image.crop(
        (crop_x, crop_y, crop_x + crop_width, crop_y + crop_height))
    # processed_image = processed_image.filter(PIL.ImageFilter.SMOOTH_MORE)
    processed_image = processed_image.filter(PIL.ImageFilter.FIND_EDGES)

    row_height = crop_height / 10
    button_labels = tuple(['a', 'b', 'up', 'down', 'left', 'right', 'start',
                           'select', 'l', 'r'])

    result_doc = {
        'filename': filename,
        'buttons': {}
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
        token_detected = mean_value > diff_threshold and max_value > max_threshold

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
