export function normalizeV3(text) {
  return (text.toLowerCase()
    .replace(/<[^>]*>|\[[^\]]*\]/g, ' ')
    .replace(/(?:https?:\/\/|www\.)\S+|(?<![\p{L}\p{N}_])[^\s@]+@[^\s@]+\.[^\s@]+(?![\p{L}\p{N}_])/gu, ' ')
    .replace(/(?<![\p{L}\p{N}_])(?:[a-z0-9-]+\.)+(?:com|net|org|info|ph|gov|uk|co|io)(?![\p{L}\p{N}_])\S*/gu, ' ')
    .match(/[a-z]+/g) || []).join(' ');
}

export function vectorize(text, config) {
  const counts = new Map();
  const normalized = config.preprocessing === 'ascii-artifact-removal-v3' ? normalizeV3(text) : text.toLowerCase();
  const units = config.analyzer === 'char' ? [...normalized] : (normalized.match(/[a-z0-9]+/g) || []);
  const [minN, maxN] = config.ngram_range || [1, 1];
  for (let n = minN; n <= maxN; n++) {
    for (let i = 0; i <= units.length - n; i++) {
      const token = units.slice(i, i + n).join(config.analyzer === 'char' ? '' : ' ');
      if (Object.hasOwn(config.vocabulary, token)) counts.set(token, (counts.get(token) || 0) + 1);
    }
  }
  const features = [...counts].map(([term, count]) => {
    const index = config.vocabulary[term];
    return { term, index, value: (config.sublinear_tf ? 1 + Math.log(count) : count) * config.idf[index] };
  });
  const norm = Math.sqrt(features.reduce((sum, f) => sum + f.value ** 2, 0));
  for (const feature of features) feature.value /= norm || 1;
  return features;
}

export function predict(text, model) {
  const features = vectorize(text, model.vectorizer);
  const logistic = model.family === 'logistic_regression';
  const offset = logistic ? model.intercept : model.class_log_prior[1] - model.class_log_prior[0];
  const contributions = features.map((feature) => ({
    ...feature,
    contribution: feature.value * (logistic ? model.coefficients[feature.index]
      : model.feature_log_prob[1][feature.index] - model.feature_log_prob[0][feature.index]),
  }));
  const score = contributions.reduce((sum, f) => sum + f.contribution, offset);
  return {
    label: score > 0 ? 'spam' : 'ham', score, offset, knownTerms: features.length,
    borderline: features.length > 0 && Math.abs(score) < 0.5,
    contributions: contributions.sort((a, b) => Math.abs(b.contribution) - Math.abs(a.contribution)),
  };
}
