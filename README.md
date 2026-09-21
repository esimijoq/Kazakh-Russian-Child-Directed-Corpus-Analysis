# LaTeLL Kazakh–Russian Corpus Analysis

Research code used for the paper **“A Kazakh–Russian Corpus of Child-Directed
Language for Low-Resource Languages.”** The scripts preprocess the Kazakh and
Russian corpora with Stanza, evaluate automatic lemmatization, and calculate
lexical-diversity statistics.

## Repository structure

```text
latell_stats/
├── scripts/
│   ├── preprocessing/       # Stanza lemmatization for each language
│   ├── evaluation/          # Comparison with manually annotated lemmas
│   └── lexical_diversity/   # Metrics plus corpus/source-level analyses
├── data/                    # Instructions only; corpus data is not committed
├── results/                 # Destination for generated tables and figures
├── docs/                    # Reproducibility and known-issue notes
├── CITATION.cff
└── requirements.txt
```

## Scripts

| Stage | Script | Purpose |
|---|---|---|
| 1 | `scripts/preprocessing/stanza_kazakh.py` | Lemmatize Kazakh `.txt` files with Stanza |
| 1 | `scripts/preprocessing/stanza_russian.py` | Lemmatize Russian `.txt` and `.xlsx` sources with Stanza |
| 2 | `scripts/evaluation/accuracy_stanza.py` | Evaluate predicted lemmas against 500 manually annotated tokens per language |
| 3 | `scripts/lexical_diversity/run_lexical_diversity.py` | Generate complete pooled and source-level metric tables |

The analysis runner directly contains the corrected bidirectional MTLD and
seeded vocd-style D implementations. The obsolete implementations have been
removed.

## Running the analysis

The scripts originated in Google Colab and currently use paths under
`/content/drive/MyDrive/`. To reproduce the workflow:

1. Obtain the corpus and annotation files described in [`data/README.md`](data/README.md).
2. Change the input and output path variables in each script to match your
   Drive layout.
3. Run the scripts in the order shown in the table above.
4. Copy generated JSON, CSV, and PNG artifacts into `results/` if they are to be
   archived with a release.

Run all six lexical-diversity metrics after downloading the corpus and creating
the lemma files:

```bash
python scripts/lexical_diversity/run_lexical_diversity.py
```

This command explicitly excludes `Kazakh/kazakh_all.txt` and
`Russian/Names_ages_of_children.xlsx`.

For a local Jupyter environment:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/preprocessing/stanza_kazakh.py
```

The Google Drive mounting section is Colab-specific and must be replaced or
skipped when running locally.

## Data and reproducibility

The scripts do not bundle the corpus, manually annotated evaluation files, or
Stanza model files. Rerun the workflow to regenerate the reported outputs.

The corpus is publicly hosted as the [Kazakh–Russian Child-Directed Language
Corpus](https://huggingface.co/datasets/esimijoq/Kazakh-Russian-Child-Directed-Speech-Corpus)
on Hugging Face. It is organized into separate `Kazakh/` and `Russian/`
directories and is currently marked with the repository-specific `other`
license category.

The small aggregate lexical-diversity CSVs and run metadata are versioned in
`results/lexical_diversity/`. Large token-level lemmatization outputs remain
ignored because they total approximately 445 MB, include derived corpus text,
and contain a file larger than GitHub's normal 100 MB limit.

See [`docs/reproducibility.md`](docs/reproducibility.md) before rerunning or
publishing results. In particular, several paths and output filenames need to
be configured for a new environment.

## Citation

Citation metadata for the accompanying paper is provided in
[`CITATION.cff`](CITATION.cff). Update it with the proceedings DOI and final URL
when those become available.

## License

No software license has been selected yet.
