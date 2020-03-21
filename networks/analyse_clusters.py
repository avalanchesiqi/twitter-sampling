import sys, os, platform, pickle
from collections import defaultdict, Counter
import numpy as np
from scipy.special import comb
from scipy import optimize, stats
import sknetwork

import matplotlib as mpl
if platform.system() == 'Linux':
    mpl.use('Agg')  # no UI backend

import matplotlib.pyplot as plt
from powerlaw import Fit, plot_ccdf


def main():
    app_name = 'cyberbullying'
    n_cluster = 6

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.3))

    for date_type in ['complete', 'sample']:
        hid_uid_stats = pickle.load(open('./{0}_hid_uid_stats.p'.format(date_type), 'rb'))
        for i in range(n_cluster):
            hashtag_cnt = {}
            with open('{0}_cluster{1}.txt'.format(date_type, i), 'r') as fin:
                # B = nx.Graph()
                # Add edges only between nodes of opposite node sets
                bipartite_edges = []

                nodes = fin.readline().split(',')
                uid_set = set([node for node in nodes if node.startswith('u')])
                hid_set = set([node for node in nodes if node.startswith('h')])
                print('in {0}_cluster{1}, {2} users, {3} hashtags'.format(date_type, i, len(uid_set), len(hid_set)))

                for hid in hid_set:
                    temp_dict = {uid: cnt for uid, cnt in hid_uid_stats[hid][1:]}
                    intersect_users = set(temp_dict.keys()).intersection(uid_set)
                    if len(intersect_users) > 0:
                        for uid in intersect_users:
                            bipartite_edges.append((uid, hid, {'weight': temp_dict[uid]}))
                        hashtag_cnt[hid] = sum([temp_dict[uid] for uid in intersect_users])

                print('total mentions', sum(hashtag_cnt.values()))
                print('avg weighted degree', sum(hashtag_cnt.values()) / (len(uid_set) + len(hid_set)))

                # B.add_edges_from(bipartite_edges)
                # print('built the weight network')
                # print('density', nx.density(B))
                # print('diameter', nx.diameter(B))
                # print('average clustering', nx.average_clustering(B))

                # print('avg degree per users', sum(hashtag_cnt.values()) / len(uid_set))
                # most_popular_hashtags = sorted(hashtag_cnt.items(), key=lambda x: x[1], reverse=True)[:5]
                # decoded_most_popular_hashtags = [(hid_hashtag_dict[x[0]], x[1]) for x in most_popular_hashtags]
                # print('most popular hashtags', decoded_most_popular_hashtags)

                # compute the powerlaw fit in the complete set
                complete_freq_list = list(hashtag_cnt.values())
                complete_powerlaw_fit = Fit(complete_freq_list)
                complete_alpha = complete_powerlaw_fit.power_law.alpha
                complete_xmin = complete_powerlaw_fit.power_law.xmin
                print('cluster {0} alpha {1}, xmin {2}'.format(i, complete_alpha, complete_xmin))
                plot_ccdf(complete_freq_list, ax=axes[0 if date_type=='complete' else 1], ls='-', label='{0} {1}'.format(date_type, i+1))
                print('============================')

    axes[0].legend()
    axes[1].legend()

    plt.tight_layout()
    if not platform.system() == 'Linux':
        plt.show()


if __name__ == '__main__':
    main()
