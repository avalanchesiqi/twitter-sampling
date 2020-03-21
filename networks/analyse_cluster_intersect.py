import pickle


def main():
    app_name = 'cyberbullying'
    n_cluster = 6

    complete_clusters = []
    for i in range(n_cluster):
        with open('{0}_cluster{1}.txt'.format('complete', i), 'r') as fin:
            complete_nodes = set(fin.readline().split(','))
            complete_clusters.append(complete_nodes)
            print('{0} users, {1} hashtags in complete cluster {2}'.format(len([x for x in complete_nodes if x.startswith('u')]),
                                                                         len([x for x in complete_nodes if x.startswith('h')]), i))

    for i in range(n_cluster):
        with open('{0}_cluster{1}.txt'.format('sample', i), 'r') as fin:
            sample_nodes = set(fin.readline().split(','))
            print('{0} users, {1} hashtags in sample cluster {2}'.format(len([x for x in sample_nodes if x.startswith('u')]),
                                                                         len([x for x in sample_nodes if x.startswith('h')]), i))
            for j in range(n_cluster):
                print('similarity between sample cluster {0} and complete cluster {1} against complete'.format(i, j),
                      100 * len(sample_nodes.intersection(complete_clusters[j]))/len(complete_clusters[j]))
                print('similarity between sample cluster {0} and complete cluster {1} against sample'.format(i, j),
                      100 * len(sample_nodes.intersection(complete_clusters[j]))/len(sample_nodes))


if __name__ == '__main__':
    main()
