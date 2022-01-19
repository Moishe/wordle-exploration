from os.path import exists
from collections import defaultdict
import hashlib
import json

memos = defaultdict(dict)

class RankMemoizer:
    def __init__(self, rank_descriptor):
        self.rank_descriptor = rank_descriptor

    def hash_guesses(self, guesses):
        m = hashlib.sha256()
        guesses = sorted(guesses)
        for guess in guesses:
            m.update(guess.encode())
        return m.hexdigest()

    def memoize(self, guesses, scores):
        global memos
        hash = self.hash_guesses(guesses)
        memos[self.rank_descriptor][hash] = scores

    def maybe_get_memo(self, guesses):
        global memos
        hash = self.hash_guesses(guesses)
        if self.rank_descriptor in memos and hash in memos[self.rank_descriptor]:
            return memos[self.rank_descriptor][hash]
        else:
            return None

    @staticmethod
    def save():
        global memos
        f = open('memos.json', 'w')
        json.dump(memos, f)

    @staticmethod
    def load():
        global memos
        if exists('memos.json'):
            f = open('memos.json')
            memos = json.load(f)
