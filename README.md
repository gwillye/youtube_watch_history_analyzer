# YouTube Watch-History Analyzer

This is a personal data-science project I built around my own YouTube history. I exported it through Google Takeout and wrote a pipeline that classifies more than 35,000 watched videos by channel and topic. The headline result: a channel-based reclassification that shrank the "Unknown" bucket from 67.9% down to 19.5% of all videos, a 71% reduction, just by mapping channels to topics.

## What it does

The pipeline ingests a YouTube watch-history export from Google Takeout and de-duplicates it down to unique videos. Each video then gets classified into a topic taxonomy (Music, Memes/Humor, Movies/Series/Anime, Games, Education, Programming, Career/Finance, Data Science/AI, and so on) using a channel-to-topic mapping plus some heuristics.

From there it aggregates the data two ways: by channel (a ranking) and by topic (a distribution). It also folds in new Takeout exports incrementally, so you can keep updating it over time without reprocessing everything from scratch.

## Key result

Reclassifying by channel cut the "Outros / Unknown" bucket from 67.9% to 19.5% of 35,676 videos, removing about 71% of that bucket. The full topic distribution lives in [`results/category_distribution.txt`](results/category_distribution.txt), and the top channels are in [`results/top20_channels.csv`](results/top20_channels.csv).

## How the pipeline works

The code under `src/` is split into three steps:

- `classificar_canais.py` handles the channel-to-topic classification (taxonomy plus heuristics).
- `agg_canais.py` does the per-channel aggregation (ranking, counts, dominant topic).
- `incorporar_takeout.py` incrementally merges a new Takeout export, deduping by video id.

The taxonomy and category rules are documented in [`docs/taxonomy.md`](docs/taxonomy.md).

## Data and privacy

The raw watch history is not included in this repo, since video titles are personal. What's published here is the code (the methodology) and the aggregate results: the topic distribution and the channel ranking, both without any titles. To reproduce it, you drop your own Takeout `watch-history` export into the pipeline and run it.

## A note on CSV

Video titles can start with characters like `@`, `-`, or `=`, which some tools quarantine as CSV formula-injection. To avoid that, the pipeline uses TSV for any data that carries titles.

## Stack

Python, pandas, CSV / TSV.
