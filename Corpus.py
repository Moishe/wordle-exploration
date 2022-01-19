import codecs

class Corpus:
    @staticmethod
    def get_top_n(n):
        # this list is already sorted, so we can optimize a bit!
        f = open('dictionary/norvig-corpus.txt')

        five_freq = []

        for l in f:
            (word, freq) = l.rstrip().split('\t')
            if len(word) == 5:
                five_freq.append(word)
                if len(five_freq) == n:
                    f.close()
                    return five_freq

    @staticmethod
    def get_real_solutions():
        words = []

        f = open('dictionary/canonical_list.txt')
        for l in f:
            words.append(codecs.decode(l.rstrip(), 'rot_13'))

        f.close()
        return words