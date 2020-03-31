
# Code and Data for Twitter Sampling Effects Study

We release the code and data for the following paper.
If you use the software, datasets, or refer to its results, please cite:
> [Siqi Wu](https://avalanchesiqi.github.io/), [Marian-Andrei Rizoiu](http://www.rizoiu.eu/), and [Lexing Xie](http://users.cecs.anu.edu.au/~xlx/). Variation across Scales: Measurement Fidelity under Twitter Data Sampling. *AAAI International Conference on Weblogs and Social Media (ICWSM)*, 2020. \[[paper](https://avalanchesiqi.github.io/files/icwsm2020sampling.pdf)\|[data](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/GW9GDM)\]

## Crawling software package: [Twitter-intact-stream](https://github.com/avalanchesiqi/twitter-intact-stream)
Twitter-intact-stream is a tool for collecting (nearly) complete Twitter filter stream.
It splits the filtering predicates into multiple subsets, and tracks each set with a distinct streaming client.

### Example: Collecting tweets related to the global pandemic COVID19
The posts over the Twittersphere are really boosted during the global pandemic.
Typically, the public/free Twitter filtered streaming API allows users to collect up to 4.32M per day, this is way below the volume of COVID19 related tweets.

In our collecting tool Twitter-intact-stream, we provide a pre-configured script to collect relevant tweets of COVID19.
It can retrieve about 26M tweets per day with an estimated 91% sampling rate.
The following image plots temporal tweet counts and sampling rates for a dataset collected from 2020-03-23 to 2020-03-31.
![Temporally tweet counts and sampling rates](analysis/tweet_volume.png)

## Data
We release 2 pairs of complete/sampled retweet cascades on Cyberbullying (sampling rate: 0.5272) and YouTube (sampling rate: 0.9153).
The data is hosted on [Dataverse](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/GW9GDM).

Each line is a cascades for a root tweet, in the format of "root_tweet_id-root_user_followers:retweet_id1-retweet_user_followers1,retweet_id2-retweet_user_followers2,...".
The tweet_id can be melt into timestamp_ms, check the [melt_snowflake](utils/helper.py) function.

```
1191867779877658625-33528:1191870307100807168-348,1191870705798914048-346381,1191871164546723841-702,1191871199242063872-152274,1191872016783216641-1420,1191872283041812480-342,1191872423513247744-543,1191876372949610498-153,1191879197108658176-403,1191882411291881473-547,1191892500786696202-19,1191893301877788672-119,1191900631176556545-525,1191919125179842560-523,1191932673574539266-247
```

Cyberbullying | complete | Sample
--- | --- | ---
#cascades | 3,008,572 | 1,168,896
avg. retweets per cascade | 15.63 | 10.97
#cascades (≥50 retweets) | 99,952 | 29,577

YouTube | complete | Sample
--- | --- | ---
#cascades | 2,022,718 | 1,803,024
avg. retweets per cascade | 13.10 | 11.87
#cascades (≥50 retweets) | 59,825 | 50,272


## Code usage
We provide a quickstart bash script:
[run_all_wrangling.sh](/wrangling/run_all_wrangling.sh)

This script can generate all the data files to run the experiments under the [data](/data), [entities](/entities), and [cascades](/cascades).

For network analysis, another quickstart bash script is provided for generating all the data files:
[run_network_analysis.sh](/networks/run_network_analysis.sh)

