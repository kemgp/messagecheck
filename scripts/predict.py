"""Classify an SMS locally using the saved models. Reads input without saving it."""
from pathlib import Path
import json
import joblib

ROOT = Path(__file__).resolve().parents[1]


def main():
    message = input('Paste an SMS message: ')
    if not message.strip():
        print('Please enter a nonempty message.')
        return
    for family in ('naive_bayes', 'logistic_regression'):
        # Load only these locally generated artifacts, never untrusted joblib files.
        model = joblib.load(ROOT / 'models' / f'{family}.joblib')
        features = model['tfidf'].transform([message])
        print(json.dumps({
            'model': family, 'prediction': str(model.predict([message])[0]),
            'known_terms': features.nnz,
            'note': 'Insufficient known terms; prediction is driven by model bias/prior.' if features.nnz == 0 else 'Non-spam does not mean safe.',
        }))


if __name__ == '__main__':
    main()
