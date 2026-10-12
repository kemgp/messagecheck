"""Versioned ASCII preprocessing shared by preparation/training and mirrored in JS."""
import re


def normalize_v3(text):
    text = text.lower()
    # Remove artifacts, and apply the same removal to real URLs and variable numbers.
    text = re.sub(r'<[^>]*>|\[[^\]]*\]', ' ', text)
    text = re.sub(r'(?:https?://|www\.)\S+|\b[^\s@]+@[^\s@]+\.[^\s@]+\b', ' ', text)
    text = re.sub(r'\b(?:[a-z0-9-]+\.)+(?:com|net|org|info|ph|gov|uk|co|io)\b\S*', ' ', text)
    return ' '.join(re.findall(r'[a-z]+', text))
