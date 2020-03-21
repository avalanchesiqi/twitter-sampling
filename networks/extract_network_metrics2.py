#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Extract timestamp_ms, user posting, hashtag, and user mentioned.
In the process, correct timestamp_ms in rate limit message, remove duplicate tweets, and sort tweets chronologically.

Usage: python plot_fig6_bipartite_dist.py
Input data files: ../data/[app_name]_out/*.txt.bz
Output data files: ../data/[app_name]_out/[ts|user|vid|mention|hashtag|retweet]_*.txt
Time: ~4H
"""

import sys, os, platform, pickle
from collections import defaultdict, Counter
from tarjan import tarjan

import matplotlib as mpl
if platform.system() == 'Linux':
    mpl.use('Agg')  # no UI backend

import matplotlib.pyplot as plt
import networkx as nx
from networkx.algorithms import bipartite, link_analysis, centrality

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
from utils.helper import Timer
from utils.plot_conf import ColorPalette, hide_spines


def write_to_file(filename, data):
    with open(filename, 'wb') as fout:
        pickle.dump({key: value for key, value in data}, fout)


def main():
    timer = Timer()
    timer.start()

    cc4 = ColorPalette.CC4
    blue = cc4[0]

    n_max = 500

    app_name = 'cyberbullying'

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.3))

    for date_type in ['sample', 'complete']:
        uid_hid_stats = pickle.load(open('./{0}_uid_hid_stats.p'.format(date_type), 'rb'))
        hid_uid_stats = pickle.load(open('./{0}_hid_uid_stats.p'.format(date_type), 'rb'))

        num_users = len(uid_hid_stats)
        num_hashtags = len(hid_uid_stats)
        print('in {0} set, {1} users, {2} hashtags'.format(date_type, num_users, num_hashtags))

        all_graph1 = {uid: [x[0] for x in lst[1:]] for uid, lst in uid_hid_stats.items()}
        all_graph2 = {hid: [x[0] for x in lst[1:]] for hid, lst in hid_uid_stats.items()}
        all_graph1.update(all_graph2)

        all_bipartites = tarjan(all_graph1)
        all_bipartites = sorted(all_bipartites, key=lambda x: len(x), reverse=True)
        print('number of bipartites: {0}'.format(len(all_bipartites)))

        largest_bipartite = all_bipartites[0]
        largest_bipartite_users = [x for x in largest_bipartite if x.startswith('u')]
        largest_bipartite_hashtags = [x for x in largest_bipartite if x.startswith('h')]
        largest_bipartite_num_users = len(largest_bipartite_users)
        largest_bipartite_num_hashtags = len(largest_bipartite_hashtags)
        print('components of largest bipartite: {0} users; {1} hashtags'.format(largest_bipartite_num_users, largest_bipartite_num_hashtags))

        # B = nx.Graph()
        # # Add edges only between nodes of opposite node sets
        # bipartite_edges = []
        # for uid in largest_bipartite_users:
        #     for hid, cnt in uid_hid_stats[uid]:
        #         bipartite_edges.append((uid, hid, {'weight': cnt}))
        # B.add_edges_from(bipartite_edges)

        B = nx.Graph()
        B.add_nodes_from(largest_bipartite_users, bipartite=0)
        B.add_nodes_from(largest_bipartite_hashtags, bipartite=1)
        bipartite_edges = []
        for uid in largest_bipartite_users:
            for hid, _ in uid_hid_stats[uid][1:]:
                bipartite_edges.append((uid, hid))
        B.add_edges_from(bipartite_edges)

        degree_container = bipartite.degree_centrality(B, largest_bipartite_users)
        sorted_degree_container = sorted(degree_container.items(), key=lambda x: x[1], reverse=True)

        user_degree_top = []
        cnt = 0
        for item in sorted_degree_container:
            if item[0].startswith('u'):
                user_degree_top.append(item)
                cnt += 1
                if cnt == n_max:
                    break
        print('{0}_user_degree_top.p'.format(date_type))
        print(user_degree_top)
        write_to_file('{0}_user_degree_top.p'.format(date_type), user_degree_top)

        hashtag_degree_top = []
        cnt = 0
        for item in sorted_degree_container:
            if item[0].startswith('h'):
                hashtag_degree_top.append(item)
                cnt += 1
                if cnt == n_max:
                    break
        print('{0}_hashtag_degree_top.p'.format(date_type))
        print(hashtag_degree_top)
        write_to_file('{0}_hashtag_degree_top.p'.format(date_type), hashtag_degree_top)

        betweenness_container = bipartite.betweenness_centrality(B, largest_bipartite_users)
        sorted_betweenness_container = sorted(betweenness_container.items(), key=lambda x: x[1], reverse=True)

        user_betweenness_top = []
        cnt = 0
        for item in sorted_betweenness_container:
            if item[0].startswith('u'):
                user_betweenness_top.append(item)
                cnt += 1
                if cnt == n_max:
                    break
        print('{0}_user_betweenness_top.p'.format(date_type))
        print(user_betweenness_top)
        write_to_file('{0}_user_betweenness_top.p'.format(date_type), user_betweenness_top)

        hashtag_betweenness_top = []
        cnt = 0
        for item in sorted_betweenness_container:
            if item[0].startswith('h'):
                hashtag_betweenness_top.append(item)
                cnt += 1
                if cnt == n_max:
                    break
        print('{0}_hashtag_betweenness_top.p'.format(date_type))
        print(hashtag_betweenness_top)
        write_to_file('{0}_hashtag_betweenness_top.p'.format(date_type), hashtag_betweenness_top)

        # pagerank_container = link_analysis.pagerank(B)
        # sorted_pagerank_container = sorted(pagerank_container.items(), key=lambda x: x[1], reverse=True)
        #
        # user_pagerank_top = []
        # cnt = 0
        # for item in sorted_pagerank_container:
        #     if item[0].startswith('u'):
        #         user_pagerank_top.append(item)
        #         cnt += 1
        #         if cnt == n_max:
        #             break
        # print('{0}_user_pagerank_top.p'.format(date_type))
        # print(user_pagerank_top)
        # write_to_file('{0}_user_pagerank_top.p'.format(date_type), user_pagerank_top)
        #
        # hashtag_pagerank_top = []
        # cnt = 0
        # for item in sorted_pagerank_container:
        #     if item[0].startswith('h'):
        #         hashtag_pagerank_top.append(item)
        #         cnt += 1
        #         if cnt == n_max:
        #             break
        # print('{0}_hashtag_pagerank_top.p'.format(date_type))
        # print(hashtag_pagerank_top)
        # write_to_file('{0}_hashtag_pagerank_top.p'.format(date_type), hashtag_pagerank_top)
        #
        # weighted_pagerank_container = link_analysis.pagerank(B, weight='weight')
        # sorted_weighted_pagerank_container = sorted(weighted_pagerank_container.items(), key=lambda x: x[1], reverse=True)
        #
        # weighted_user_pagerank_top = []
        # cnt = 0
        # for item in sorted_weighted_pagerank_container:
        #     if item[0].startswith('u'):
        #         weighted_user_pagerank_top.append(item)
        #         cnt += 1
        #         if cnt == n_max:
        #             break
        # print('{0}_weighted_user_pagerank_top.p'.format(date_type))
        # print(weighted_user_pagerank_top)
        # write_to_file('{0}_weighted_user_pagerank_top.p'.format(date_type), weighted_user_pagerank_top)
        #
        # weighted_hashtag_pagerank_top = []
        # cnt = 0
        # for item in sorted_weighted_pagerank_container:
        #     if item[0].startswith('h'):
        #         weighted_hashtag_pagerank_top.append(item)
        #         cnt += 1
        #         if cnt == n_max:
        #             break
        # print('{0}_weighted_hashtag_pagerank_top.p'.format(date_type))
        # print(weighted_hashtag_pagerank_top)
        # write_to_file('{0}_weighted_hashtag_pagerank_top.p'.format(date_type), weighted_hashtag_pagerank_top)
        #
        # hub_container, authority_container = link_analysis.hits(B)
        # sorted_hub_container = sorted(hub_container.items(), key=lambda x: x[1], reverse=True)
        # sorted_authority_container = sorted(authority_container.items(), key=lambda x: x[1], reverse=True)
        #
        # user_hub_top = []
        # cnt = 0
        # for item in sorted_hub_container:
        #     if item[0].startswith('u'):
        #         user_hub_top.append(item)
        #         cnt += 1
        #         if cnt == n_max:
        #             break
        # print('{0}_user_hub_top.p'.format(date_type))
        # print(user_hub_top)
        # write_to_file('{0}_user_hub_top.p'.format(date_type), user_hub_top)
        #
        # hashtag_hub_top = []
        # cnt = 0
        # for item in sorted_hub_container:
        #     if item[0].startswith('h'):
        #         hashtag_hub_top.append(item)
        #         cnt += 1
        #         if cnt == n_max:
        #             break
        # print('{0}_hashtag_hub_top.p'.format(date_type))
        # print(hashtag_hub_top)
        # write_to_file('{0}_hashtag_hub_top.p'.format(date_type), hashtag_hub_top)
        #
        # user_authority_top = []
        # cnt = 0
        # for item in sorted_authority_container:
        #     if item[0].startswith('u'):
        #         user_authority_top.append(item)
        #         cnt += 1
        #         if cnt == n_max:
        #             break
        # print('{0}_user_authority_top.p'.format(date_type))
        # print(user_authority_top)
        # write_to_file('{0}_user_authority_top.p'.format(date_type), user_authority_top)
        #
        # hashtag_authority_top = []
        # cnt = 0
        # for item in sorted_authority_container:
        #     if item[0].startswith('h'):
        #         hashtag_authority_top.append(item)
        #         cnt += 1
        #         if cnt == n_max:
        #             break
        # print('{0}_hashtag_authority_top.p'.format(date_type))
        # print(hashtag_authority_top)
        # write_to_file('{0}_hashtag_authority_top.p'.format(date_type), hashtag_authority_top)
        #

    timer.stop()


if __name__ == '__main__':
    main()
