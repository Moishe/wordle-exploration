import codecs

if __name__ == "__main__":
    known_words = set()
    f = open('dictionary/canonical_list.txt')
    for l in f:
      known_words.add(codecs.decode(l.rstrip(), 'rot_13'))

    f = open('dictionary/norvig-corpus.txt')
    c = 0
    for l in f:
      (word, freq) = l.rstrip().split('\t')
      if len(word) == 5:
        c += 1
        known_words.discard(word)

        if len(known_words) == 0:
          print(c, word)
          break

print(known_words)