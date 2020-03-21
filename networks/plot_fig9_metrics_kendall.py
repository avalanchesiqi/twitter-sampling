import sys, os, platform, pickle
from scipy.stats import kendalltau

import matplotlib as mpl
if platform.system() == 'Linux':
    mpl.use('Agg')  # no UI backend

import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
from utils.helper import Timer
from utils.metrics import mean_confidence_interval
from utils.plot_conf import ColorPalette, hide_spines


def main():
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.3))

    for ax_idx, entity in enumerate(['user', 'hashtag']):
        for metric in ['degree', 'pagerank', 'hits']:
            sample_dict = pickle.load(open('./sample_{0}_{1}_top.p'.format(entity, metric), 'rb'))
            complete_dict = pickle.load(open('./complete_{0}_{1}_top.p'.format(entity, metric), 'rb'))

            print(entity, metric)
            print(len(set(sample_dict.keys()).intersection(set(complete_dict.keys()))))

            sorted_complete = sorted(complete_dict.keys(), key=lambda x: complete_dict[x], reverse=True)
            sorted_sample = sorted(sample_dict.keys(), key=lambda x: sample_dict[x], reverse=True)
            print(len(set(sorted_complete[:100]).intersection(set(sorted_sample[:100]))))

            x_axis = range(10, 101)
            y_axis = []
            for k in x_axis:
                complete_rank = range(k)
                sample_rank = []
                for i in range(k):
                    if sorted_complete[i] in sorted_sample:
                        sample_rank.append(sorted_sample.index(sorted_complete[i]))
                    else:
                        sample_rank.append(500)
                y_axis.append(kendalltau(complete_rank, sample_rank)[0])

            axes[ax_idx].plot(x_axis, y_axis, lw=1.5, label=metric)

        axes[ax_idx].set_xlabel('top k', fontsize=16)
        axes[ax_idx].tick_params(axis='both', which='major', labelsize=16)
        axes[ax_idx].set_ylim([0, 1])

    axes[0].set_ylabel(r"kendall's $\tau$", fontsize=16)
    axes[1].legend(frameon=False, fontsize=16, ncol=2, fancybox=False, shadow=True, loc='lower right')
    axes[0].set_title('(a) user', fontsize=18)
    axes[1].set_title('(b) hashtag', fontsize=18)

    hide_spines(axes)

    plt.tight_layout()
    plt.savefig('../images/metrics_kendall.pdf', bbox_inches='tight')
    if not platform.system() == 'Linux':
        plt.show()


if __name__ == '__main__':
    main()
