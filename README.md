# tppip
Twitch Plays Pokemon Image Processing Scripts

## Quick Start

Requirements

* Python 3.4+
* Pillow (PIL fork)

### Token Analysis

Running:

        python3 -m tppip.tokenanalysis


Will output something like:

        {
          "buttons": {
            "a": {
              "pixel_diff_max": 12.0,
              "pixel_diff_mean": 3.392857142857143,
              "row": 0,
              "token_detected": false
            },
            "b": {
              "pixel_diff_max": 7.0,
              "pixel_diff_mean": 1.607142857142857,
              "row": 1,
              "token_detected": false
            },
            "down": {
              "pixel_diff_max": 5.0,
              "pixel_diff_mean": 0.2857142857142857,
              "row": 3,
              "token_detected": false
            },
            "l": {
              "pixel_diff_max": 0.0,
              "pixel_diff_mean": 0.0,
              "row": 8,
              "token_detected": false
            },
            "left": {
              "pixel_diff_max": 0.0,
              "pixel_diff_mean": 0.0,
              "row": 4,
              "token_detected": false
            },
            "r": {
              "pixel_diff_max": 0.0,
              "pixel_diff_mean": 0.0,
              "row": 9,
              "token_detected": false
            },
            "right": {
              "pixel_diff_max": 0.0,
              "pixel_diff_mean": 0.0,
              "row": 5,
              "token_detected": false
            },
            "select": {
              "pixel_diff_max": 0.0,
              "pixel_diff_mean": 0.0,
              "row": 7,
              "token_detected": false
            },
            "start": {
              "pixel_diff_max": 0.0,
              "pixel_diff_mean": 0.0,
              "row": 6,
              "token_detected": false
            },
            "up": {
              "pixel_diff_max": 0.0,
              "pixel_diff_mean": 0.0,
              "row": 2,
              "token_detected": false
            }
          },
          "filename": "/tmp/tmp2os59co9-tppip/1456803932.png"
        }
