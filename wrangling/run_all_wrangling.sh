#!/bin/bash
# usage: ./run_all_wrangling.sh

log_file=data_wrangling.log

if [ -f "$log_file" ]; then
  rm "$log_file"
fi

python extract_tweet_status.py >> "$log_file"

sleep 60
echo '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++' >> "$log_file"

python extract_entities.py >> "$log_file"

sleep 60
echo '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++' >> "$log_file"

python merge_subcrawlers.py >> "$log_file"

sleep 60
echo '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++' >> "$log_file"
