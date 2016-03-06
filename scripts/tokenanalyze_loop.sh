#!/bin/bash

while true; do
    python3 -m tppip.tokenanalyze \
        --url-cache-filename /tmp/tppip_stream_url_cache.txt \
        --save-screenshot-filename /tmp/tpp-current.png \
        > /tmp/tokenanalyze-new.json

    if [ $? -eq 0 ]; then
        mv /tmp/tokenanalyze-new.json /tmp/tokenanalyze.json 
        sleep 15
    else
        sleep 300
    fi
done
