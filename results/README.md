# Generated results

```text
results/
├── lexical_diversity/       # Small aggregate CSVs (tracked by Git)
├── evaluation/              # Manual Stanza evaluation workbooks
└── lemmatization/
    ├── kazakh/              # Five source categories
    └── russian/             # Four source categories
```

## Lexical-diversity results

| File | Contents |
|---|---|
| `lexical_diversity/all_lexical_diversity_metrics.csv` | Current complete rerun: pooled and source-level results |
| `lexical_diversity/pooled_all_metrics.csv` | Current pooled word-form results |
| `lexical_diversity/source_level_all_metrics.csv` | Current results for four Russian and five Kazakh lemma groups |
| `lexical_diversity/run_metadata.json` | Corpus revision, exclusions, and metric parameters |

The current tables include TTR, MATTR, corrected MTLD, HLR, Guiraud's Index,
and corrected vocd-style D. The token and type counts in the source-level table
were checked against all nine `*_lemmas.txt` files and matched exactly.

### Source-level lexical diversity

These values were calculated from the Stanza-lemmatized source files. They are
therefore separate from the pooled comparison, which uses original word forms.

| Language | Source | Tokens | Types | TTR | MATTR | MTLD | HLR | Guiraud | vocd-D |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Russian | Ages 0–11 | 213,584 | 15,591 | 0.0730 | 0.8179 | 89.6599 | 0.4357 | 33.7357 | 191.3099 |
| Russian | Dialogue | 294,738 | 20,279 | 0.0688 | 0.6290 | 18.0410 | 0.5412 | 37.3533 | 149.2031 |
| Russian | Folk tales | 171,647 | 12,219 | 0.0712 | 0.8035 | 78.5849 | 0.4265 | 29.4929 | 194.3043 |
| Russian | Other cultures | 1,589,179 | 35,846 | 0.0226 | 0.8186 | 93.8826 | 0.3518 | 28.4351 | 182.6887 |
| Kazakh | Fairy tales | 78,665 | 6,938 | 0.0882 | 0.7870 | 70.1526 | 0.4720 | 24.7368 | 205.7136 |
| Kazakh | Subtitles | 142,354 | 13,957 | 0.0980 | 0.8259 | 92.7256 | 0.5347 | 36.9920 | 231.9627 |
| Kazakh | Journals | 220,358 | 17,716 | 0.0804 | 0.8280 | 113.2343 | 0.4822 | 37.7399 | 404.0425 |
| Kazakh | Books | 167,482 | 15,824 | 0.0945 | 0.8864 | 199.2064 | 0.4891 | 38.6663 | 378.0521 |
| Kazakh | Educational | 442,617 | 27,905 | 0.0630 | 0.8330 | 104.5179 | 0.4964 | 41.9438 | 302.8577 |

The current pooled rerun uses Hugging Face revision
`42607bda706c9ca06d00adefe0a2b993cee68346`, excluding
`Kazakh/kazakh_all.txt` and `Russian/Names_ages_of_children.xlsx`. Compared with
the earlier pooled CSV, the current release has 15 fewer Russian tokens and 423
more Kazakh tokens. Use the new complete files for analysis of the current
dataset release.

## Lemmatization outputs

Each source directory can contain:

- `lemmatization_results.json`: token-level Stanza output, sometimes including
  original corpus text;
- `lemma_frequency.json`: lemma frequency counts;
- `*_lemmas.txt`: the complete lemma sequence; and
- `unique_lemmas.txt`: the exported unique-lemma list.

The five Kazakh groups are `kazakh_books`, `kazakh_educational`,
`kazakh_fairytale`, `kazakh_journal`, and `kazakh_subtitles`. The four Russian
groups are `by_ages_from_0-11`, `ru_dialogue`, `ru_folk_tales`, and
`ru_other_cultures`.

## Evaluation outputs

`evaluation/annotated_VS_stanza.xlsx` contains the Russian manual evaluation:
500 nonempty Stanza/gold pairs, of which 416 are exact matches (83.2%). The
Kazakh evaluation workbook is not currently present.
