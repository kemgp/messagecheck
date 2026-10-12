export function vectorize(text, config) {
  const counts = new Map();
  for (const token of text.toLowerCase().match(/[a-z0-9]+/g) || []) {
    if (Object.hasOwn(config.vocabulary, token)) counts.set(token, (counts.get(token) || 0) + 1);
  }
  const features = [...counts].map(([term, count]) => {
    const index = config.vocabulary[term];
    return { term, index, value: count * config.idf[index] };
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
