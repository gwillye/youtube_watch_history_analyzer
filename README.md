# YouTube Watch-History Analyzer

> **Real-world context.** A personal **data-science** project: I exported my own YouTube history (Google Takeout) and built a pipeline to **classify 35,000+ watched videos by channel and topic**. Headline result — a channel-based reclassification that **shrank the "Unknown" bucket from 67.9% to 19.5%** (a 71% reduction) by mapping channels to topics.

## 🎯 What it does
- Ingests YouTube **watch-history** (Google Takeout) and de-duplicates to unique videos.
- Classifies each video into a **topic taxonomy** (Music, Memes/Humor, Movies/Series/Anime, Games, Education, Programming, Career/Finance, Data Science/AI, …) via channel→topic mapping + heuristics.
- Aggregates by **channel** (ranking) and by **topic** (distribution), and folds in new Takeout exports incrementally.

## 📈 Key result
Reclassifying by channel cut the **"Outros / Unknown"** bucket from **67.9% → 19.5%** of 35,676 videos (−71% of that bucket). Full topic distribution: [`results/category_distribution.txt`](results/category_distribution.txt); top channels: [`results/top20_channels.csv`](results/top20_channels.csv).

## 🧩 Pipeline (`src/`)
- `classificar_canais.py` — channel → topic classification (taxonomy + heuristics).
- `agg_canais.py` — per-channel aggregation (ranking, counts, dominant topic).
- `incorporar_takeout.py` — incrementally merge a new Takeout export (dedupe by video id).

Taxonomy / category rules: [`docs/taxonomy.md`](docs/taxonomy.md).

## 🔒 Data & privacy
The **raw watch history is not included** — video titles are personal. Only the **code (methodology)** and **aggregate results** (topic distribution + channel ranking without titles) are published. To reproduce, drop your own Takeout `watch-history` export in and run the pipeline.

## ⚙️ Note on CSV
Video titles can start with `@ - =`, which some tools quarantine as CSV formula-injection — so the pipeline uses **TSV** for title-bearing data.

## 🛠️ Stack
Python · pandas · CSV / TSV
