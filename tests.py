import unittest
from Matcher import Matcher

DEFAULT_GUESSES = ['wooer', 'about', 'other', 'which', 'their', 'there', 'first', 'would', 'these', 'click']

def get_top_n(n):
    # this list is already sorted, so we can optimize a bit!
    f = open('dictionary/norvig-corpus.txt')

    five_freq = []

    for l in f:
        (word, freq) = l.rstrip().split('\t')
        if len(word) == 5:
            five_freq.append(word)
            if len(five_freq) == n:
                return five_freq
                
class MatcherTests(unittest.TestCase):

  def setUp(self):
    self.matcher = Matcher(DEFAULT_GUESSES)

  def test_getresults(self):
    (match_at_loc, match_not_at_loc, unmatched_letters) = self.matcher.get_results('wooer', 'click')
    self.assertEqual(match_at_loc, [])
    self.assertEqual(match_not_at_loc, [])
    self.assertEqual(unmatched_letters, set([l for l in 'click']))

    (match_at_loc, match_not_at_loc, unmatched_letters) = self.matcher.get_results('wooer', 'efete')
    self.assertEqual(match_not_at_loc, [(0, 'e')])

    (match_at_loc, match_not_at_loc, unmatched_letters) = self.matcher.get_results('freer', 'efete')
    print(match_at_loc, match_not_at_loc, unmatched_letters)
    print('freer')
    print(Matcher.escaped_word('efete', match_at_loc, match_not_at_loc))

    (match_at_loc, match_not_at_loc, unmatched_letters) = self.matcher.get_results('filmy', 'billy')
    print(match_at_loc, match_not_at_loc, unmatched_letters)


if __name__ == '__main__':
    unittest.main()    