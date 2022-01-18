import json

f = []
f.append(open('results/densities-3k-guesses.json'))
f.append(open('results/densities-no-letter-filter.json'))

words = []
for fn in f:
  scores = json.load(fn)
  words.append([item[0] for item in scores[1]])

for (idx, word) in enumerate(words[0]):
  print("%d -> %d %s" % (idx, words[1].index(word), word))
