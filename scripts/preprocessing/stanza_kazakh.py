#!/usr/bin/env python3
"""Lemmatize the Kazakh corpus with Stanza."""

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
    """
    Download and initialize the Kazakh language pipeline for Stanza
    """
    print("Initializing Stanza pipeline for Kazakh...")
    try:
        # Download Kazakh models if not already present
        stanza.download('kk', resources_version='1.6.0')
        # Initialize pipeline
        nlp = stanza.Pipeline('kk', processors='tokenize,pos,lemma')
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
    """
    Lemmatize Kazakh text using Stanza pipeline, after cleaning symbols.

    Args:
        text (str): Input text in Kazakh
        nlp: Stanza pipeline

    Returns:
        list: List of dictionaries with word, lemma, and POS tag
    """
    try:
        # Replace non-word and non-space characters with a space, then normalize spaces
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
    """
    Lemmatize text from a single file

    Args:
        file_path (str): Path to text file
        nlp: Stanza pipeline

    Returns:
        dict: Results with filename, original text, and lemmatized data
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

        lemmatized_data = lemmatize_text(text, nlp)

        return {
            'filename': os.path.basename(file_path),
            'text': text, # Original text
            'lemmatized': lemmatized_data,
            'word_count': len(text.split()) # Word count of original text
        }
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return None

def process_corpus(corpus_dir, nlp, file_pattern="*.txt"):
    """
    Process entire corpus directory

    Args:
        corpus_dir (str): Path to corpus directory
        nlp: Stanza pipeline
        file_pattern (str): File pattern to match (default: *.txt)

    Returns:
        dict: Results for all files
    """
    corpus_path = Path(corpus_dir)
    results = {}
    file_count = 0

    for file_path in sorted(corpus_path.rglob(file_pattern)): # Changed glob to rglob
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
    CORPUS_DIR = Path("/content/drive/MyDrive/Kazakh_dataset/books")
    OUTPUT_DIR = "/content/drive/MyDrive/everything_about_morphology_and_AI/LaTeLL ’2026/lemmatization_results"

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
import json
import sys

input_file = '/content/drive/MyDrive/everything_about_morphology_and_AI/LaTeLL ’2026/ru_other_cultures/lemmatization_results.json'
output_file = '/content/drive/MyDrive/everything_about_morphology_and_AI/LaTeLL ’2026/ru_other_cultures/ru_other_cultures_lemmas.txt'

def extract_lemmas_from_json(input_file, output_file):
    try:
        # Read the JSON file
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        lemmas = []

        # Handle different JSON structures
        if isinstance(data, list):
            # If JSON is a list of objects
            for item in data:
                if isinstance(item, dict) and 'lemma' in item:
                    lemmas.append(item['lemma'])
        elif isinstance(data, dict):
            # If JSON is a single object, search recursively for 'lemma' keys
            def find_lemmas(obj):
                if isinstance(obj, dict):
                    if 'lemma' in obj:
                        lemmas.append(obj['lemma'])
                    for value in obj.values():
                        find_lemmas(value)
                elif isinstance(obj, list):
                    for item in obj:
                        find_lemmas(item)

            find_lemmas(data)

        # Save lemmas to text file
        with open(output_file, 'w', encoding='utf-8') as f:
            for lemma in lemmas:
                f.write(str(lemma) + '\n')

        print(f"Successfully extracted {len(lemmas)} lemmas")
        print(f"Saved to: {output_file}")

    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in '{input_file}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

# Call the function directly with the predefined file paths
extract_lemmas_from_json(input_file, output_file)
