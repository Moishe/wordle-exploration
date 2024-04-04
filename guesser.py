from collections import defaultdict
import heapq
import math
from typing import Tuple

from Corpus import Corpus


NO_MATCH = 0
MATCH = 1
MATCH_NOT_AT_LOC = 2

class EntropyCalculator:

    def __init__(self, possibilities, corpus):
        self.corpus = corpus
        self.words_without_letters = defaultdict(set)
        self.words_with_letters = defaultdict(set)
        self.words_with_letters_at_location = defaultdict(set)
        self.memoized = {}

        self.possibilities = possibilities

        self.preprocess(possibilities)

    def preprocess(self, words):
        # build the sets of words which do and do not have letters in the given positions
        for j in range(ord('a'), ord('z') + 1):
            c = chr(j)
            for word in words:
                if c in word:
                    self.words_with_letters[c].add(word)
                    self.words_with_letters_at_location[(c, word.index(c))].add(word)
                else:
                    self.words_without_letters[c].add(word)

    def get_results(self, guess, answer):
        result = []
        for gi, c in enumerate(guess):
            if c in answer:
                if gi == answer.index(c):
                    result.append((c, MATCH))
                else:
                    result.append((c, MATCH_NOT_AT_LOC))
                answer = answer.replace(c, '_', 1)
            else:
                result.append((c, NO_MATCH))

        return tuple(result)

    def get_possibilities(self, words, state):
        wordset = set(words)
        for idx, (c, result) in enumerate(state):
            if result == NO_MATCH:
                wordset = wordset.intersection(self.words_without_letters[c])
            elif result == MATCH:
                wordset = wordset.intersection(self.words_with_letters_at_location[(c, idx)])
            elif result == MATCH_NOT_AT_LOC:
                wordset = wordset.intersection(self.words_with_letters[c])

        return list(wordset)

    def eliminates(self):
        # so you have a word like "slate"
        # and a list like ["paste", "junky", "chant"]
        # and you want to determine which of the words in the list
        # you'd eliminate by guessing "slate" and getting information
        # back from it

        # for each guess x solution combination:
        scores = []
        for guess in self.corpus:
            score = 0
            pattern_histogram = defaultdict(int)
            pattern_information = {}

            for solution in self.possibilities:
                # get the state of the guess and the solution
                state = self.get_results(guess, solution)
                pattern_histogram[state] += 1

                if state not in pattern_information:
                    possibilities = self.get_possibilities(self.possibilities, state)
                    if not len(possibilities):
                        pattern_information[state] = 0
                    else:
                        pattern_information[state] = math.log2(len(self.possibilities) / len(possibilities))

            score = sum([pattern_histogram[p] / len(self.possibilities) * pattern_information[p] for p in pattern_histogram])
            heapq.heappush(scores, (score, guess))

        print(heapq.nlargest(10, scores))

        """
        for p in self.possibilities:
            for s in scores:
                if s[1] == p:
                    print(p, s[0])
        """

if __name__=="__main__":
    corpus = Corpus.get_real_solutions()
    ec = EntropyCalculator(corpus, corpus)
    ec.eliminates()
