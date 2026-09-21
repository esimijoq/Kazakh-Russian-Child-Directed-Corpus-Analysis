# Data inputs

The corpus is available from Hugging Face:

<https://huggingface.co/datasets/esimijoq/Kazakh-Russian-Child-Directed-Speech-Corpus>

Clone it into this ignored directory when a local copy is required:

```bash
git clone https://huggingface.co/datasets/esimijoq/Kazakh-Russian-Child-Directed-Speech-Corpus data/corpus
```

The Hugging Face repository preserves separate `Kazakh/` and `Russian/`
directories. Check its source documentation and source-specific redistribution
conditions before republishing texts elsewhere.

The scripts expect the following inputs:

- Kazakh corpus sources as UTF-8 `.txt` files;
- Russian corpus sources as UTF-8 `.txt` files;
- Russian dialogue data in an `.xlsx` workbook containing a `SENTENCES` column;
- Russian evaluation data with `Annotated` and `Stanza` columns (500 tokens in
  the paper experiment);
- Kazakh evaluation data with `Annotated` and `Stanza` columns (500 tokens in
  the paper experiment); and
- the nine source-level lemma files listed in the source-level lexical-diversity
  analysis script (four Russian and five Kazakh files).

All current paths point to the authors' Google Drive layout. Update the
configuration sections before running the scripts in another environment.
