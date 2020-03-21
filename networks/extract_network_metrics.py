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
import numpy as np
from tarjan import tarjan
from scipy import sparse
from sknetwork import ranking

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
from utils.helper import Timer


def write_to_file(filename, data):
    with open(filename, 'wb') as fout:
        pickle.dump({key: value for key, value in data}, fout)


def main():
    timer = Timer()
    timer.start()

    n_max = 500

    app_name = 'cyberbullying'

    for date_type in ['sample', 'complete']:
        uid_hid_stats = pickle.load(open('./{0}_uid_hid_stats.p'.format(date_type), 'rb'))
        hid_uid_stats = pickle.load(open('./{0}_hid_uid_stats.p'.format(date_type), 'rb'))

        num_users = len(uid_hid_stats)
        num_hashtags = len(hid_uid_stats)
        print('in {0} set, {1} users, {2} hashtags'.format(date_type, num_users, num_hashtags))

        all_graph = {uid: [x[0] for x in lst[1:]] for uid, lst in uid_hid_stats.items()}
        rev_all_graph = {hid: [x[0] for x in lst[1:]] for hid, lst in hid_uid_stats.items()}
        all_graph.update(rev_all_graph)

        all_bipartites = tarjan(all_graph)
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

        # re-embed
        new_user_embed = {uid: embed for embed, uid in enumerate(sorted(largest_bipartite_users))}
        new_embed_user = {v: k for k, v in new_user_embed.items()}
        new_hashtag_embed = {hid: embed for embed, hid in enumerate(sorted(largest_bipartite_hashtags))}
        new_embed_hashtag = {v: k for k, v in new_hashtag_embed.items()}

        bipartite_edges = {}
        for uid in largest_bipartite_users:
            bipartite_edges[new_user_embed[uid]] = []
            for hid, _ in uid_hid_stats[uid][1:]:
                bipartite_edges[new_user_embed[uid]].append(new_hashtag_embed[hid])
        row, col = [], []
        for key, item in bipartite_edges.items():
            row += [key] * len(item)
            col += item
        biadjacency = sparse.csr_matrix((np.ones(len(row), dtype=int), (row, col)))

        print('built the biadjacency')

        bipagerank = ranking.BiPageRank()
        print('running BiPageRank...')
        row_col_scores = bipagerank.fit_transform(biadjacency)
        print('completed BiPageRank...')
        user_scores = row_col_scores[: len(largest_bipartite_users)]
        sorted_user_scores = sorted(enumerate(user_scores), key=lambda x: x[1], reverse=True)[:n_max]
        hashtag_scores = row_col_scores[len(largest_bipartite_users):]
        sorted_hashtag_scores = sorted(enumerate(hashtag_scores), key=lambda x: x[1], reverse=True)[:n_max]

        user_pagerank_top = []
        for embed, score in sorted_user_scores:
            user_pagerank_top.append((new_embed_user[embed], score))
        print('{0}_user_pagerank_top.p'.format(date_type))
        print(user_pagerank_top)
        write_to_file('{0}_user_pagerank_top.p'.format(date_type), user_pagerank_top)

        hashtag_pagerank_top = []
        for embed, score in sorted_hashtag_scores:
            hashtag_pagerank_top.append((new_embed_hashtag[embed], score))
        print('{0}_hashtag_pagerank_top.p'.format(date_type))
        print(hashtag_pagerank_top)
        write_to_file('{0}_hashtag_pagerank_top.p'.format(date_type), hashtag_pagerank_top)

        hits = ranking.HITS(mode='hubs')
        print('running HITS...')
        user_scores = hits.fit(biadjacency).scores_
        hashtag_scores = hits.col_scores_
        print('completed HITS...')
        sorted_user_scores = sorted(enumerate(user_scores), key=lambda x: x[1], reverse=True)[:n_max]
        sorted_hashtag_scores = sorted(enumerate(hashtag_scores), key=lambda x: x[1], reverse=True)[:n_max]

        user_hits_top = []
        for embed, score in sorted_user_scores:
            user_hits_top.append((new_embed_user[embed], score))
        print('{0}_user_hits_top.p'.format(date_type))
        print(user_hits_top)
        write_to_file('{0}_user_hits_top.p'.format(date_type), user_hits_top)

        hashtag_hits_top = []
        for embed, score in sorted_hashtag_scores:
            hashtag_hits_top.append((new_embed_hashtag[embed], score))
        print('{0}_hashtag_hits_top.p'.format(date_type))
        print(hashtag_hits_top)
        write_to_file('{0}_hashtag_hits_top.p'.format(date_type), hashtag_hits_top)

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

    timer.stop()


if __name__ == '__main__':
    main()
