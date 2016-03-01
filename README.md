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
              "pixel_diff_max": 0.0,
              "pixel_diff_mean": 0.0,
              "row": 0,
              "token_detected": false
            },
            "b": {
              "pixel_diff_max": 0.0,
              "pixel_diff_mean": 0.0,
              "row": 1,
              "token_detected": false
            },
            "down": {
              "pixel_diff_max": 0.0,
              "pixel_diff_mean": 0.0,
              "row": 3,
              "token_detected": false
            },
            [...]
            "select": {
              "pixel_diff_max": 255.0,
              "pixel_diff_mean": 112.78571428571429,
              "row": 7,
              "token_detected": true
            }
          },
          "filename": "/tmp/tmp7g3hs5sv-tppip/1456803062.png"
        }

