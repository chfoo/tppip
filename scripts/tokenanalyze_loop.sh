#!/bin/bash

while true; do
    python3 -m tppip.tokenanalyze > /tmp/tokenanalyze-new.json

    if [ $? -eq 0 ]; then
        mv /tmp/tokenanalyze-new.json /tmp/tokenanalyze.json 
        sleep 60
    else
        sleep 300
    fi
done
