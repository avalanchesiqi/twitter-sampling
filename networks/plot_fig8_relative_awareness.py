#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Measure relative importance of entities in a bipartite graph.

Usage: python plot_fig8_relative_importance.py
Input data files: ../data/[app_name]_out/*.txt.bz
Output data files: ../data/[app_name]_out/[ts|user|vid|mention|hashtag|retweet]_*.txt
Time: ~4M
"""

import sys, os, platform, pickle
import numpy as np
from scipy.stats import percentileofscore

import matplotlib as mpl
if platform.system() == 'Linux':
    mpl.use('Agg')  # no UI backend

import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
from utils.helper import Timer
from utils.metrics import mean_confidence_interval
from utils.plot_conf import ColorPalette, hide_spines


def main():
    timer = Timer()
    timer.start()

    cc4 = ColorPalette.CC4
    blue = cc4[0]

    num_bin = 20
    width = 100 // num_bin
    top_n = 1000

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.3))

    for ax_idx, entity in enumerate(['user', 'hashtag']):
        if entity == 'user':
            complete_stats = pickle.load(open('./complete_uid_hid_stats.p', 'rb'))
            sample_stats = pickle.load(open('./sample_uid_hid_stats.p', 'rb'))
        else:
            complete_stats = pickle.load(open('./complete_hid_uid_stats.p', 'rb'))
            sample_stats = pickle.load(open('./sample_hid_uid_stats.p', 'rb'))

        print('in complete set: {1} {0}s; in sample set: {2} {0}s'.format(entity, len(complete_stats), len(sample_stats)))

        complete_popularity_dict = {id: lst[0] for id, lst in complete_stats.items()}
        # complete_popularity_dict = {id: lst[0] for id, lst in complete_stats.items()}
        top_complete = sorted(complete_popularity_dict.keys(), key=lambda x: complete_popularity_dict[x], reverse=True)[:top_n]
        complete_boxplots = [[] for _ in range(num_bin)]
        sample_boxplots = [[] for _ in range(num_bin)]
        delta_boxplots = [[] for _ in range(num_bin)]

        for id in top_complete:
            if len(complete_stats[id][1:]) >= num_bin:
                # print(id)
                # print(complete_stats[id])
                print('number of tweets', complete_stats[id][0], ', number of total tweet occur', complete_popularity_dict[id],
                      ', number of distinct tweet', len(complete_stats[id][1:]), ', avg tweet occur', complete_popularity_dict[id]/len(complete_stats[id][1:]))

                complete_freq_dict = {x[0]: x[1] for x in complete_stats[id][1:]}
                complete_freq_list = list(complete_freq_dict.values())
                complete_percentile_dict = {}
                for value in set(complete_freq_list):
                    complete_percentile_dict[value] = percentileofscore(complete_freq_list, value, kind='rank')

                sample_freq_dict = {x[0]: x[1] for x in sample_stats[id][1:]}
                sample_freq_list = list(sample_freq_dict.values())
                sample_percentile_dict = {}
                for value in set(sample_freq_list):
                    sample_percentile_dict[value] = percentileofscore(sample_freq_list, value, kind='rank')

                # entity_freq_dict = {x[0]: (x[1], sample_freq_dict[x[0]]) if x[0] in sample_freq_dict else (x[1], 0) for x in complete_stats[id][1:]}

                # sorted_complete_id_list = sorted(entity_freq_dict.keys(), key=lambda x: entity_freq_dict[x][0], reverse=True)
                #
                # complete_freq = [entity_freq_dict[x][0] for x in sorted_complete_id_list]
                # sample_freq = [entity_freq_dict[x][1] for x in sorted_complete_id_list]

                # complete_freq = sorted(complete_freq_dict.values(), reverse=True)
                # sample_freq = sorted(sample_freq_dict.values(), reverse=True) + [0] * (len(complete_freq_dict) - len(sample_freq_dict))

                # print(complete_freq)
                # print(sample_freq)

                # width = len(sorted_complete_id_list) / num_bin

                # complete_freq = np.array(complete_freq) / np.sum(complete_freq) * 100
                # binned_complete_freq = np.zeros(num_bin)
                # for i in range(num_bin):
                #     binned_complete_freq[i] = sum(complete_freq[int(width * i): int(width * (i+1))])
                #
                # sample_freq = np.array(sample_freq) / np.sum(sample_freq) * 100
                # binned_sample_freq = np.zeros(num_bin)
                # for i in range(num_bin):
                #     binned_sample_freq[i] = sum(sample_freq[int(width * i): int(width * (i+1))])

                for entity in complete_freq_dict.keys():
                    complete_percentile = complete_percentile_dict[complete_freq_dict[entity]]
                    if entity in sample_freq_dict:
                        sample_percentile = sample_percentile_dict[sample_freq_dict[entity]]
                    else:
                        sample_percentile = 0
                    delta_percentile = sample_percentile - complete_percentile

                    bin_idx = int(complete_percentile // width)
                    if bin_idx == num_bin:
                        bin_idx = num_bin - 1

                    complete_boxplots[bin_idx].append(complete_percentile)
                    sample_boxplots[bin_idx].append(sample_percentile)
                    delta_boxplots[bin_idx].append(delta_percentile)
                    # if complete_percentile > 100 - width:
                    #     if entity in sample_freq_dict:
                    #         print(complete_percentile, '{0}'.format(complete_freq_dict[entity]), sample_percentile, '{0}'.format(sample_freq_dict[entity]))
                    #     else:
                    #         print(complete_percentile, '{0}'.format(complete_freq_dict[entity]), sample_percentile, '{0}'.format(0))

                # print(binned_complete_freq, sum(binned_complete_freq))
                # print(binned_sample_freq, sum(binned_sample_freq))
                # print(delta_relative_importance, sum(delta_relative_importance))
                print(np.mean(complete_boxplots[-1]), np.mean(sample_boxplots[-1]), np.mean(delta_boxplots[-1]))
                print('=========')

        # axes[ax_idx].boxplot(boxplots, showmeans=True, showfliers=False)

        x_axis = [100 // num_bin * i for i in range(1, num_bin + 1)]

        for box in complete_boxplots:
            print(len(box))

        complete_mean_list = []
        complete_error_list = []
        for i in range(num_bin):
            mean, lb, ub = mean_confidence_interval(complete_boxplots[i])
            complete_mean_list.append(mean)
            complete_error_list.append((ub - lb) / 2)

        sample_mean_list = []
        sample_error_list = []
        for i in range(num_bin):
            mean, lb, ub = mean_confidence_interval(sample_boxplots[i])
            sample_mean_list.append(mean)
            sample_error_list.append((ub - lb) / 2)

        delta_mean_list = []
        delta_error_list = []
        for i in range(num_bin):
            mean, lb, ub = mean_confidence_interval(delta_boxplots[i])
            delta_mean_list.append(mean)
            delta_error_list.append((ub - lb) / 2)

        axes[ax_idx].errorbar(x_axis, complete_mean_list, yerr=complete_error_list, c='k', lw=1.5, ls='-', marker='o', label='complete')
        axes[ax_idx].errorbar(x_axis, sample_mean_list, yerr=sample_error_list, c=blue, lw=1.5, ls='-', marker='o', label='sample')
        # axes[ax_idx].errorbar(x_axis, delta_mean_list, yerr=delta_error_list, c='k', lw=1.5, ls='-', marker='.')
        print(complete_mean_list)
        print(sample_mean_list)
        print(delta_mean_list)
        # axes[ax_idx].fill_between(x_axis, lb_list, mean_list,
        #                           facecolor=blue, alpha=0.8, lw=0, zorder=10)
        # axes[ax_idx].fill_between(x_axis, ub_list, mean_list,
        #                           facecolor=blue, alpha=0.8, lw=0, zorder=10)
        # axes[ax_idx+2].plot((x_axis[0], x_axis[-1]), (0, 0), color='gray', ls='--', lw=1)

        axes[ax_idx].set_xticks([100 // num_bin * i for i in range(1, num_bin + 1, 2)])
        axes[ax_idx].set_xlim([5, 105])
        axes[ax_idx].set_xlabel('rank percentile (%)', fontsize=16)
        axes[ax_idx].tick_params(axis='both', which='major', labelsize=16)

    # axes[0].set_ylim([-2, 2])
    # axes[0].set_yticks([-1, 0, 1])
    axes[0].set_ylabel(r'$\beta_s$ - $\beta_c$ (%)', fontsize=16)
    axes[0].set_title('(a) user', size=18, pad=-3*72)

    # axes[1].set_ylim([-6, 6])
    # axes[1].set_yticks([-4, -2, 0, 2, 4])
    axes[1].set_title('(b) hashtag', size=18, pad=-3*72)

    hide_spines(axes)

    timer.stop()

    plt.tight_layout(rect=[0, 0.05, 1, 1])
    plt.savefig('../images/relative_awareness.pdf', bbox_inches='tight')
    if not platform.system() == 'Linux':
        plt.show()


if __name__ == '__main__':
    main()
