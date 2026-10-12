"""Cross-language checks for all supported v3 feature representations."""
import json
import subprocess
import tempfile
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from text_v3 import normalize_v3

ROOT = Path(__file__).resolve().parents[1]

texts = ['', ' ', '!!!', 'Pay pay PAY within 12 hours!', 'you have been hacked',
         'Pay at <URL> within <DATE_TIME> [REDACTED]', 'Pay at https://example.com within 12',
         'mail me name@example.com; visit portal.lto.gov.ph today',
         'éexample.com résumé@test.com 你好example.com', 'Résumé İSTANBUL 中文',
         'hi 😃 friend', 'Hello\nworld\tHELLO', 'a a a a a',
         '[https://example.com](https://example.com) <url> <email>']
fixtures = []
for analyzer, grams in [('word', (1, 1)), ('word', (1, 2)), ('char', (3, 5))]:
    v = TfidfVectorizer(preprocessor=normalize_v3, lowercase=False, analyzer=analyzer,
                        token_pattern=r'[a-z]+' if analyzer == 'word' else None,
                        ngram_range=grams, sublinear_tf=True)
    features = v.fit_transform(texts)
    config = {'preprocessing': 'ascii-artifact-removal-v3', 'analyzer': analyzer,
              'ngram_range': grams, 'sublinear_tf': True,
              'vocabulary': {k: int(i) for k, i in v.vocabulary_.items()}, 'idf': v.idf_.tolist()}
    for i, text in enumerate(texts):
        row = features.getrow(i)
        fixtures.append({'text': text, 'normalized': normalize_v3(text), 'config': config,
                         'features': {str(k): float(value) for k, value in zip(row.indices, row.data)}})
with tempfile.TemporaryDirectory(prefix='messagecheck-features-') as directory:
    path = Path(directory) / 'features.json'
    path.write_text(json.dumps(fixtures))
    code = """
import fs from 'node:fs';
import assert from 'node:assert/strict';
import { vectorize, normalizeV3 } from './src/inference.js';
const cases = JSON.parse(fs.readFileSync(process.argv[1], 'utf8'));
for (const c of cases) {
  assert.equal(normalizeV3(c.text), c.normalized);
  const got = vectorize(c.text, c.config);
  assert.equal(got.length, Object.keys(c.features).length);
  for (const f of got) assert.ok(Math.abs(f.value - c.features[f.index]) < 1e-10);
}
console.log(`${cases.length} Python/JavaScript normalization and unigram/bigram/character feature cases passed.`);
"""
    subprocess.run(['node', '--input-type=module', '-e', code, str(path)], cwd=ROOT, check=True)
