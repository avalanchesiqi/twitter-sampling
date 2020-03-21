#!/bin/bash
# usage: ./run_network_analysis.sh

log_file=network_analysis.log

if [ -f "$log_file" ]; then
  rm "$log_file"
fi

python build_entity_embedding.py.py >> "$log_file"

sleep 60
echo '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++' >> "$log_file"

python build_user_hashtag_bipartite.py >> "$log_file"

sleep 60
echo '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++' >> "$log_file"

python build_retweet_network.py >> "$log_file"

sleep 60
echo '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++' >> "$log_file"

python extract_clustering.py >> "$log_file"

sleep 60
echo '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++' >> "$log_file"

python analyse_cluster_hashtags.py >> "$log_file"
