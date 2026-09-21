#!/usr/bin/env python3
"""Lemmatize the Russian corpus with Stanza."""

# %%
# ============================================================================
# STEP 1: Installation (Run this cell first in Colab)
# ============================================================================

# Colab command: !pip install stanza

# %%
# ============================================================================
# STEP 2: Import Libraries
# ============================================================================

import stanza
import os
from pathlib import Path
from collections import defaultdict
import json

# %%
# ============================================================================
# STEP 3: Download and Initialize Stanza Pipeline for Kazakh
# ============================================================================

def initialize_stanza():
    print("Initializing Stanza pipeline for Kazakh...")
    try:
        stanza.download('ru', resources_version='1.6.0')
        # Initialize pipeline
        nlp = stanza.Pipeline('ru', processors='tokenize,pos,lemma')
        print("✓ Stanza pipeline initialized successfully")
        return nlp
    except Exception as e:
        print(f"Error initializing Stanza: {e}")
        raise

# %%
import re

# ============================================================================
# STEP 4: Lemmatization Functions
# ============================================================================

def lemmatize_text(text, nlp):
    try:
        cleaned_text = re.sub(r'[\d]|[^\w\s]', ' ', text, flags=re.UNICODE)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()

        doc = nlp(cleaned_text)
        lemmatized_data = []

        for sent in doc.sentences:
            for word in sent.words:
                lemmatized_data.append({
                    'word': word.text,
                    'lemma': word.lemma,
                    'pos': word.pos,
                    'upos': word.upos
                })

        return lemmatized_data
    except Exception as e:
        print(f"Error processing text: {e}")
        return []

def lemmatize_file(file_path, nlp):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

        lemmatized_data = lemmatize_text(text, nlp)

        return {
            'lemmatized': lemmatized_data,
        }
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return None

def process_corpus(corpus_dir, nlp, file_pattern="*.txt"):
    corpus_path = Path(corpus_dir)
    results = {}
    file_count = 0

    for file_path in sorted(corpus_path.rglob(file_pattern)):
        result = lemmatize_file(str(file_path), nlp)

        if result:
            results[file_path.name] = result
            file_count += 1

    print(f"\nProcessed {file_count} files successfully")
    return results

# %%
# ============================================================================
# STEP 5: Analysis and Export Functions
# ============================================================================

def get_lemma_frequency(results):
    """
    Calculate lemma frequency across corpus

    Args:
        results (dict): Lemmatization results

    Returns:
        dict: Lemma frequency counts
    """
    lemma_freq = defaultdict(int)

    for file_result in results.values():
        for item in file_result['lemmatized']:
            lemma_freq[item['lemma']] += 1

    # Sort by frequency
    return dict(sorted(lemma_freq.items(), key=lambda x: x[1], reverse=True))

def get_pos_distribution(results):
    """
    Get POS tag distribution across corpus

    Args:
        results (dict): Lemmatization results

    Returns:
        dict: POS tag frequency
    """
    pos_freq = defaultdict(int)

    for file_result in results.values():
        for item in file_result['lemmatized']:
            pos_freq[item['pos']] += 1

    return dict(sorted(pos_freq.items(), key=lambda x: x[1], reverse=True))

def save_results_to_json(results, output_file):
    """
    Save lemmatization results to JSON file

    Args:
        results (dict): Lemmatization results
        output_file (str): Output file path
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Results saved to {output_file}")

def export_lemmas_only(results, output_file):
    """
    Export only lemmas as a simple list (one lemma per line)

    Args:
        results (dict): Lemmatization results
        output_file (str): Output file path
    """
    lemmas = set()

    for file_result in results.values():
        for item in file_result['lemmatized']:
            lemmas.add(item['lemma'])

    with open(output_file, 'w', encoding='utf-8') as f:
        for lemma in sorted(lemmas):
            f.write(lemma + '\n')

    print(f"Unique lemmas ({len(lemmas)} total) exported to {output_file}")

# %%
# ============================================================================
# STEP 6: Main Execution
# ============================================================================

def main():
    """
    Main execution function
    """
    # Initialize Stanza pipeline
    nlp = initialize_stanza()

    # Configuration - Modify these paths for your setup
    CORPUS_DIR = Path("/content/drive/MyDrive/Russian_dataset/fairy_tales/solo_russo")
    OUTPUT_DIR = "/content/drive/MyDrive/everything_about_morphology_and_AI/LaTeLL ’2026/ru_lemmatization_results"

    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if CORPUS_DIR.exists():
        txt_files = list(CORPUS_DIR.rglob("*.txt"))
        print(f"Found {len(txt_files)} text files\n")

    # Process corpus
    results = process_corpus(CORPUS_DIR, nlp)

    if not results:
        print("No files were processed!")
        return

    # Export results
    print("Exporting results...")
    save_results_to_json(results, f"{OUTPUT_DIR}/lemmatization_results.json")
    export_lemmas_only(results, f"{OUTPUT_DIR}/unique_lemmas.txt")

    # Save lemma frequency
    lemma_freq = get_lemma_frequency(results)
    with open(f"{OUTPUT_DIR}/lemma_frequency.json", 'w', encoding='utf-8') as f:
        json.dump(lemma_freq, f, ensure_ascii=False, indent=2)
    print(f"Lemma frequency saved")

    print("\n✓ All processing complete!")



if __name__ == "__main__":
    main()

# %%
import pandas as pd


def main():
    """
    Main execution function
    """
    # Initialize Stanza pipeline
    nlp = initialize_stanza()

    # Configuration - Modify these paths for your setup
    EXCEL_FILE_PATH = Path("/content/drive/MyDrive/Russian_dataset/russian_dialogue/Russian_childes.xlsx")
    OUTPUT_DIR = "/content/drive/MyDrive/everything_about_morphology_and_AI/LaTeLL ’2026/ru_lemmatization_results"

    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("\nLoading Russian transcripts from Excel...")

    results = {}
    file_count = 0
    if EXCEL_FILE_PATH.exists():
        try:
            df = pd.read_excel(EXCEL_FILE_PATH)
            text_column = 'SENTENCES'
            if text_column in df.columns:
                for idx, row in df.iterrows():
                    text = row[text_column]
                    if pd.notna(text) and str(text).strip():
                        lemmatized_data = lemmatize_text(str(text), nlp)
                        if lemmatized_data:
                            # Using a unique identifier for each row/text in results
                            results[f"row_{idx}"] = {'lemmatized': lemmatized_data}
                            file_count += 1
                print(f"  ✓ Successfully processed {file_count} entries from column: {text_column}")
            else:
                print(f"  ✗ Error: Required column '{text_column}' not found in Excel file.")
        except Exception as e:
            print(f"  ✗ Error loading or processing Excel: {e}")
    else:
        print(f"  ⊘ File not found: {EXCEL_FILE_PATH}")

    if not results:
        print("No text entries were processed from the Excel file!")
        return

    # Export results
    print("Exporting results...")
    save_results_to_json(results, f"{OUTPUT_DIR}/lemmatization_results.json")
    export_lemmas_only(results, f"{OUTPUT_DIR}/unique_lemmas.txt")

    # Save lemma frequency
    lemma_freq = get_lemma_frequency(results)
    with open(f"{OUTPUT_DIR}/lemma_frequency.json", 'w', encoding='utf-8') as f:
        json.dump(lemma_freq, f, ensure_ascii=False, indent=2)
    print(f"Lemma frequency saved")

    print("\n✓ All processing complete!")



if __name__ == "__main__":
    main()
