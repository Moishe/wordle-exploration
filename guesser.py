from collections import defaultdict
from email.policy import default
import math
from tkinter import NO
from typing import Tuple
from attr import dataclass

from Corpus import Corpus


NO_MATCH = 0
MATCH = 1
MATCH_NOT_AT_LOC = 2

words_without_letters = defaultdict(set)
words_with_letters = defaultdict(set)
words_with_letters_at_location = defaultdict(set)

def preprocess(words):
    # build the sets of words which do and do not have letters in the given positions
    for j in range(ord('a'), ord('z') + 1):
        c = chr(j)
        for word in words:
            if c in word:
                words_with_letters[c].add(word)
                words_with_letters_at_location[(c, word.index(c))].add(word)
            else:
                words_without_letters[c].add(word)

def get_results(guess, answer):
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


def find_all_matches(word, c):
    matches = []
    for i in range(len(word)):
        if word[i] == c:
            matches.append(i)
    return matches


memoized = {}
def is_possible(word: str, state: Tuple):
    global memoized
    if (word, state) in memoized:
        #print('.', end='')
        return memoized[(word, state)]

    for idx, (c, result) in enumerate(state):
        if result == NO_MATCH and c in word:
            memoized[(word, state)] = False
            return False
        if result == MATCH and c != word[idx]:
            memoized[(word, state)] = False
            return False
        if result == MATCH_NOT_AT_LOC:
            if c == word[idx] or c not in word:
                memoized[(word, state)] = False
                return False

    memoized[(word, state)] = True
    return True


def get_possibilities(words, state):
    solutions = words

    possibilities = []
    for potential in solutions:
        if is_possible(potential, state):
            possibilities.append(potential)

    return possibilities


def eliminates():
    # so you have a word like "slate"
    # and a list like ["paste", "junky", "chant"]
    # and you want to determine which of the words in the list
    # you'd eliminate by guessing "slate" and getting information
    # back from it
    words = Corpus.get_real_solutions()
    # for each guess x solution combination:
    scores = defaultdict(float)
    for guess in words:
        total_left = 0
        for solution in words:
            if solution == guess:
                continue
            # get the state of the guess and the solution
            state = get_results(guess, solution)

            # get the possibilities that would be possible
            possibilities = get_possibilities(words, state)

            total_left += len(possibilities)
        scores[guess] = total_left / len(words)
        print(guess, total_left / len(words))

    print(sorted(scores.items(), key=lambda x: x[1])[:10])

if __name__=="__main__":
    eliminates()
