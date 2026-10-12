import { useState } from 'react';
import naiveBayes from '../models/naive_bayes.json';
import logistic from '../models/logistic_regression.json';
import validation from '../reports/validation-report.json';
import { predict } from './inference.js';

const models = [
  { name: 'Naive Bayes', id: 'naive_bayes', model: naiveBayes, note: 'Highest validation spam F1' },
  { name: 'Logistic regression', id: 'logistic_regression', model: logistic, note: 'Moderate spam-class weighting' },
];
const examples = [
  { label: 'Everyday message', text: 'Are we still meeting at the library after class?' },
  { label: 'Promotional message', text: 'Congratulations! Claim your FREE cash prize now. Call to collect your reward.' },
];
const percent = (n) => `${(n * 100).toFixed(2)}%`;

function Result({ entry, result }) {
  const insufficient = result.knownTerms === 0;
  return <article className="result-card">
    <div className="result-heading"><div><h3>{entry.name}</h3><p>{entry.note}</p></div><span className="model-mark" aria-hidden="true">{entry.id === 'naive_bayes' ? '01' : '02'}</span></div>
    <div className={`prediction ${insufficient ? 'unknown' : result.label}`}>
      <span className="status-dot" />{insufficient ? 'Not enough known words' : result.label === 'spam' ? 'Predicted spam' : 'Predicted non-spam'}
    </div>
    {result.borderline && <p className="review-notice"><strong>Borderline decision — review this message.</strong> The score is close to this model’s cutoff. The label above is a tentative model output, not a verified assessment.</p>}
    {insufficient ? <p className="empty-note">This message has no terms in the learned vocabulary. The model cannot offer a useful word-based assessment.</p> : <>
      <p className="term-label">WORDS INFLUENCING THIS RESULT</p>
      <div className="terms">{result.contributions.slice(0, 6).map((term) => <span key={term.term} className={term.contribution > 0 ? 'toward' : 'away'} title={`Score contribution: ${term.contribution.toFixed(4)}`}>
        {term.term} <span aria-label={term.contribution > 0 ? 'toward spam' : 'toward non-spam'}>{term.contribution > 0 ? '↑' : '↓'}</span>
      </span>)}</div>
      <p className="legend">↑ Toward spam <span>↓ Toward non-spam</span></p>
      <details><summary>How this score was calculated</summary><p>Each word’s TF-IDF value is multiplied by its learned weight. Their contributions plus the model’s starting score give the decision score. A positive score predicts spam.</p><dl><div><dt>Starting score</dt><dd>{result.offset.toFixed(4)}</dd></div><div><dt>Final decision score</dt><dd>{result.score.toFixed(4)}</dd></div><div><dt>Known unique terms</dt><dd>{result.knownTerms}</dd></div></dl><p>This explains the model’s arithmetic, not the sender’s intent. The score is not a confidence percentage.</p></details>
    </>}
  </article>;
}

export default function App() {
  const [text, setText] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState('');
  function edit(value) { setText(value); setAnalysis(null); setError(''); }
  function analyze(event) {
    event.preventDefault();
    if (!text.trim()) { setError('Enter a message or choose an example to get started.'); return; }
    const start = performance.now();
    const results = models.map((entry) => predict(text, entry.model));
    setAnalysis({ results, milliseconds: performance.now() - start });
    setError('');
  }
  return <>
    <header className="header"><a href="#" className="brand"><span className="brand-icon" aria-hidden="true">m<span>✓</span></span>MessageCheck</a><nav aria-label="Main navigation"><a href="#check">Check a message</a><a href="#evaluation">Evaluation</a><a href="#about">About</a></nav><span className="prototype">RESEARCH PROTOTYPE</span></header>
    <main>
      <section className="intro"><div><p className="eyebrow"><span /> SMALL MODELS. VISIBLE REASONING.</p><h1>A second look<br />at your messages.</h1><p className="lead">Check an SMS for spam patterns and explore the words behind two machine-learning models’ predictions.</p></div><aside className="privacy"><span className="privacy-icon" aria-hidden="true">↳</span><strong>Your message stays here.</strong><p>Predictions run in your browser. No account, message uploads, or saved history.</p><span className="privacy-foot">LOCAL PROCESSING</span></aside></section>
      <section id="check" className="workspace">
        <div className="section-line"><h2>Check a message</h2><span>01 / ANALYZE</span></div>
        <form onSubmit={analyze} className="input-card"><label htmlFor="message">SMS message</label><textarea id="message" value={text} onChange={(event) => edit(event.target.value)} maxLength={5000} placeholder="Paste a message you’d like to explore…" aria-describedby={error ? 'input-error input-help' : 'input-help'} aria-invalid={Boolean(error)} />
          <div className="input-meta"><span id="input-help">English text works best. Maximum 5,000 characters.</span><span>{text.length.toLocaleString()} / 5,000</span></div>
          <div className="form-actions"><div className="examples"><span>Try an example</span>{examples.map((example) => <button type="button" key={example.label} onClick={() => edit(example.text)}>{example.label}</button>)}</div><button className="analyze-button" type="submit">Analyze message <span aria-hidden="true">↗</span></button></div>
          {error && <p id="input-error" className="error" role="alert">{error}</p>}
        </form>
        <div aria-live="polite">{analysis ? <><div className="results-meta"><h2>Two models, one message</h2><span>{analysis.milliseconds.toFixed(1)} ms local computation</span></div>{analysis.results.every((r) => r.knownTerms > 0) && analysis.results[0].label !== analysis.results[1].label && <p className="review-notice disagreement"><strong>The models disagree. Manual review is needed.</strong> Neither prediction verifies the sender, a link, or whether a payment request is genuine.</p>}<div className="results-grid">{models.map((entry, i) => <Result key={entry.id} entry={entry} result={analysis.results[i]} />)}</div></> : <div className="empty-state"><span aria-hidden="true">↗</span><p>Your model comparison will appear here.<small>Enter a message above to see predictions and influential words.</small></p></div>}</div>
        <p className="caution">A non-spam prediction does not establish that a message is safe. These models identify patterns learned from an older SMS dataset.</p>
      </section>
      <section id="evaluation" className="evaluation"><div className="section-line"><h2>Measured, not assumed.</h2><span>02 / EVALUATION</span></div><div className="evaluation-intro"><p>Preliminary performance on <strong>774 validation messages</strong>. Revision 2 uses training cross-validation, reused validation data, and user diagnostics. The final test set has not been evaluated.</p><span className="validation-badge">VALIDATION ONLY</span></div><div className="table-scroll"><table><thead><tr><th scope="col">Model</th><th scope="col">Spam precision</th><th scope="col">Spam recall</th><th scope="col">Spam F1</th><th scope="col">False alarms</th><th scope="col">Missed spam</th></tr></thead><tbody>{[...models.map((m) => ({ name: m.name, metrics: validation.selected[m.id].metrics })), { name: 'Always predict non-spam', metrics: validation.majority_baseline }].map((row) => <tr key={row.name}><th scope="row">{row.name}</th>{['spam_precision', 'spam_recall', 'spam_f1'].map((key) => <td key={key}>{percent(row.metrics[key])}</td>)}<td>{row.metrics.confusion_matrix[0][1]}</td><td>{row.metrics.confusion_matrix[1][0]}</td></tr>)}</tbody></table></div><p className="table-note">Training: 3,612 messages · Validation: 678 non-spam + 96 spam · All binary predictions are counted, including borderline cases.</p><p className="table-note">Review notices flag model disagreement or a score within 0.5 of zero. This is an uncalibrated interface heuristic, not a confidence estimate or an accuracy improvement.</p></section>
      <section id="about" className="about"><div><p className="eyebrow">03 / UNDER THE HOOD</p><h2>Understand the prediction.</h2></div><div><p>TF-IDF represents each message using weighted word counts. Naive Bayes and logistic regression use those features to predict a label. The word contributions show how each model reached its numerical score.</p><p>Built using the <a href="https://archive.ics.uci.edu/dataset/228/sms%2Bspam%2Bcollection" target="_blank" rel="noreferrer">UCI SMS Spam Collection</a> by Almeida and Hidalgo (2011), with duplicate-aware dataset partitions. This study does not establish performance on current scams or Filipino-language messages.</p><p className="credit">React · JavaScript · Vite · scikit-learn</p></div></section>
    </main><footer><span>MessageCheck</span><span>A machine-learning case study. Built for understanding.</span></footer>
  </>;
}
