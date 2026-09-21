# Reproducibility notes

## Environment

These scripts were originally developed in Google Colab and use Google Drive
paths. Historical output indicated that Stanza 1.12.0 was used for at least the
recorded preprocessing runs, but the complete package environment was not
captured. For an archival release, rerun the
workflow in a clean environment and freeze the resolved versions with
`python -m pip freeze`.

## Inputs and paths

- The public corpus is hosted at
  `esimijoq/Kazakh-Russian-Child-Directed-Speech-Corpus` on Hugging Face.
- The complete lexical-diversity rerun uses corpus revision
  `42607bda706c9ca06d00adefe0a2b993cee68346` and explicitly excludes
  `Kazakh/kazakh_all.txt` and `Russian/Names_ages_of_children.xlsx`.
- Input/output paths are hard-coded under `/content/drive/MyDrive/` or
  `/content/sample_data/`.
- `accuracy_stanza.py` expects `annotated_VS_stanza (2).xlsx` for Russian and
  `kazakh.xlsx` for Kazakh.
- The preprocessing scripts write generic filenames such as
  `lemmatization_results.json` and `lemma_frequency.json`. Use separate output
  directories per language and source so one run cannot overwrite another.

## Script-specific cautions

- `run_lexical_diversity.py` contains the implementations used by both pooled
  and source-level analysis. MTLD is bidirectional and includes partial final factors.
  The vocd-style D estimate uses sample sizes 35–50, 100 trials, three runs, and
  seed 42. It is not guaranteed to equal CLAN `vocd` output.
- Run `python scripts/lexical_diversity/run_lexical_diversity.py` to regenerate
  all six metrics: TTR, MATTR, corrected MTLD, HLR, Guiraud's Index, and
  corrected vocd-style D.
- The last conversion section in `stanza_kazakh.py` currently points to a
  Russian `ru_other_cultures` input/output location. Review or replace those
  paths before running that section.
- Some status messages in `stanza_russian.py` say “Kazakh” although the
  configured Stanza language is Russian (`ru`). This is a label issue in the
  script, not evidence that the Kazakh model was loaded.

## Evaluation

The evaluation script calculates exact-match accuracy, average Levenshtein
distance, and weighted precision, recall, and F1 over lemma labels. For a new
run, preserve the sampled token identifiers and the manual-annotation protocol
alongside the result tables so the 500-token samples can be audited.

The available Russian workbook has 500 populated pairs and reproduces the
reported 83.2% exact-match accuracy. The Kazakh workbook used to obtain the
reported 81.4% result is not present in this repository, so the Kazakh
evaluation cannot yet be independently rerun or verified.

## Recommended release checklist

1. Configure language- and source-specific input/output paths.
2. Record a fixed corpus release or checksum for every input.
3. Record package and Stanza model versions.
4. Run scripts from a clean runtime in documented order.
5. Save result tables and figures without redistributing restricted source text.
6. Add the final paper DOI, repository URL, and an agreed software license.
