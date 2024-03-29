#!/usr/bin/env python

import sys
import re
import math
import random
import logging
from optparse import OptionParser

"""
M-94 Cipher device simulator.

See:
    http://maritime.org/tech/csp488.htm
    http://maritime.org/tech/csp488man.htm
"""

wheels = ['ABCEIGDJFVUYMHTQKZOLRXSPWN',
          'ACDEHFIJKTLMOUVYGZNPQXRWSB',
          'ADKOMJUBGEPHSCZINXFYQRTVWL',
          'AEDCBIFGJHLKMRUOQVPTNWYXZS',
          'AFNQUKDOPITJBRHCYSLWEMZVXG',
          'AGPOCIXLURNDYZHWBJSQFKVMET',
          'AHXJEZBNIKPVROGSYDULCFMQTW',
          'AIHPJOBWKCVFZLQERYNSUMGTDX',
          'AJDSKQOIVTZEFHGYUNLPMBXWCR',
          'AKELBDFJGHONMTPRQSVZUXYWIC',
          'ALTMSXVQPNOHUWDIZYCGKRFBEJ',
          'AMNFLHQGCUJTBYPZKXISRDVEWO',
          'ANCJILDHBMKGXUZTSWQYVORPFE',
          'AODWPKJVIUQHZCTXBLEGNYRSMF',
          'APBVHIYKSGUENTCXOWFQDRLJZM',
          'AQJNUBTGIMWZRVLXCSHDEOKFPY',
          'ARMYOFTHEUSZJXDPCWGQIBKLNV',
          'ASDMCNEQBOZPLGVJRKYTFUIWXH',
          'ATOJYLFXNGWHVCMIRBSEKUPDZQ',
          'AUTRZXQLYIOVBPESNHJWMDGFCK',
          'AVNKHRGOXEYBFSJMUDQCLZWTIP',
          'AWVSFDLIEBHKNRJQZGMXPUCOTY',
          'AXKWREVDTUFOYHMLSIQNJCPGBZ',
          'AYJPXMVKBQWUGLOSTECHNZFRID',
          'AZDNBUHYFWJLVGRCQMPSOEXTKI',
          ]

# Bigram frequencies for English - count per 10,000 characters.
# See http://homepages.math.uic.edu/~leon/mcs425-s08/handouts/char_freq2.pdf
# bigrams[0][1] (20) is frequency for pair 'AB', for example.
# We convert these into conditional probabilites P(XY | X)
bigrams = [
    [1, 20, 33, 52, 0, 12, 18, 5, 39, 1, 12, 57, 26,
     181, 1, 20, 1, 75, 95, 104, 9, 20, 13, 1, 26, 1],
    [11, 1, 0, 0, 47, 0, 0, 0, 6, 1, 0, 17, 0,
     0, 19, 0, 0, 11, 2, 1, 21, 0, 0, 0, 11, 0],
    [31, 0, 4, 0, 38, 0, 0, 38, 10, 0, 18, 9, 0,
     0, 45, 0, 1, 11, 1, 15, 7, 0, 0, 0, 1, 0],
    [48, 20, 9, 13, 57, 11, 7, 25, 50, 3, 1, 11, 14,
     16, 41, 6, 0, 14, 35, 56, 10, 2, 19, 0, 10, 0],
    [110, 23, 45, 126, 48, 30, 15, 33, 41, 3, 5, 55, 47,
     111, 33, 28, 2, 169, 115, 83, 6, 24, 50, 9, 26, 0],
    [25, 2, 3, 2, 20, 11, 1, 8, 23, 1, 0, 8, 5,
     1, 40, 2, 0, 16, 5, 37, 8, 0, 3, 0, 2, 0],
    [24, 3, 2, 2, 28, 3, 4, 35, 18, 1, 0, 7, 3,
     4, 23, 1, 0, 12, 9, 16, 7, 0, 5, 0, 1, 0],
    [114, 2, 2, 1, 302, 2, 1, 6, 97, 0, 0, 2, 3,
     1, 49, 1, 0, 8, 5, 32, 8, 0, 4, 0, 4, 0],
    [10, 5, 32, 33, 23, 17, 25, 6, 1, 1, 8, 37, 37,
     179, 24, 6, 0, 27, 86, 93, 1, 14, 7, 2, 0, 2],
    [2, 0, 0, 0, 2, 0, 0, 0, 3, 0, 0, 0, 0,
     0, 3, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0],
    [6, 1, 1, 1, 29, 1, 0, 2, 14, 0, 0, 2, 1,
     9, 4, 0, 0, 0, 5, 4, 1, 0, 2, 0, 2, 0],
    [40, 3, 2, 36, 64, 10, 1, 4, 47, 0, 3, 56, 4,
     2, 41, 3, 0, 2, 11, 15, 8, 3, 5, 0, 31, 0],
    [44, 7, 1, 1, 68, 2, 1, 3, 25, 0, 0, 1, 5,
     2, 29, 11, 0, 3, 10, 9, 8, 0, 4, 0, 18, 0],
    [40, 7, 25, 146, 66, 8, 92, 16, 33, 2, 8, 9, 7,
     8, 60, 4, 1, 3, 33, 106, 6, 2, 12, 0, 11, 0],
    [16, 12, 13, 18, 5, 80, 7, 11, 12, 1, 13, 26, 48,
     106, 36, 15, 0, 84, 28, 57, 115, 12, 46, 0, 5, 1],
    [23, 1, 0, 0, 30, 1, 0, 3, 12, 0, 0, 15, 1,
     0, 21, 10, 0, 18, 5, 11, 6, 0, 1, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0],
    [50, 7, 10, 20, 133, 8, 10, 12, 50, 1, 8, 10, 14,
     16, 55, 6, 0, 14, 37, 42, 12, 4, 11, 0, 21, 0],
    [67, 11, 17, 7, 74, 11, 4, 50, 49, 2, 6, 13, 12,
     10, 57, 20, 2, 4, 43, 109, 20, 2, 24, 0, 4, 0],
    [59, 10, 11, 7, 75, 9, 3, 330, 76, 1, 2, 17, 11,
     7, 115, 4, 0, 28, 34, 56, 17, 1, 31, 0, 16, 0],
    [7, 5, 12, 7, 7, 2, 14, 2, 8, 0, 1, 34, 8,
     36, 1, 16, 0, 44, 35, 48, 0, 0, 2, 0, 1, 0],
    [5, 0, 0, 0, 65, 0, 0, 0, 11, 0, 0, 0, 0,
     0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    [66, 1, 1, 2, 39, 1, 0, 44, 39, 0, 0, 2, 1,
     12, 29, 0, 0, 3, 4, 4, 1, 0, 2, 0, 1, 0],
    [1, 0, 2, 0, 1, 0, 0, 0, 2, 0, 0, 0, 0,
     0, 0, 3, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0],
    [18, 7, 6, 6, 14, 7, 3, 10, 11, 1, 1, 4, 6,
     3, 36, 4, 0, 3, 19, 20, 1, 1, 12, 0, 2, 0],
    [1, 0, 0, 0, 3, 0, 0, 0, 1, 0, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]


# Convert to bits per bigram based on conditional probability.
log2 = math.log(2)
never_bits = math.log(9981) / log2
for x in range(26):
    t = sum([bigrams[x][y] for y in range(26)])
    for y in range(26):
        f = bigrams[x][y]
        if f > 0:
            bigrams[x][y] = -math.log(float(f) / t) / log2
        else:
            bigrams[x][y] = never_bits


def main():
    parser = OptionParser(usage="usage: %prog [options] key [message]")
    parser.add_option('-d', '--decode', action='store_true', dest='decode',
                     help="Decode the given message (else encode)")
    (options, args) = parser.parse_args()

    if len(args) > 2:
        raise TypeError("Too many arguments.")

    if len(args) < 1:
        key = raw_input("Key pass-phrase: ")
    else:
        key = args[0]

    m = M94(key)

    if len(args) == 2:
        message = args[1]
    else:
        message = sys.stdin.read()

    if options.decode:
        print m.decode(message)
    else:
        print m.encode(message)


class M94(object):
    """ Simulate am M94 cipher machine.

    >>> M94.group_letters('thisisrunontext')
    'thisi sruno ntext'
    >>> m = M94('general electric company')
    >>> m.translate_line('HELLOTHERE', 0)
    'HELLOTHERE'
    >>> m.translate_line('HELLOTHERE', 2)
    'WAVFYKCYJH'
    >>> m.decode('WAVFY KCYJH')
    'HELLO THERE'
    >>> x = m.encode("now is the time for all good men")
    >>> m.decode(x)
    'NOWIS THETI MEFOR ALLGO ODMEN'
    >>> m.decode(m.encode('xxxxxxx'))
    'QUPEU PL'
    >>> m = M94('John Quincy Adams')
    >>> M94.prepare_input(m.decode("TSFSJ QEPXY UGVBD DERUB UBKSP QWBUA AJQCV KFCEP SPRFL XLTKM FDIOW"))
    ['LANDEDONBEACHNOSIXATZEROF', 'IVEONEZEROWITHOUTCASUALTI', 'OGREM']
    >>> m = M94('Naval District Cipher')
    >>> m.decode("HVSPM FPDSF XOIWB EWXQY KUGCR")
    'REQUE STBOA TFORC ASUAL TIESV'
    >>> x = m.encode("i need the 411")
    >>> m.decode(x)
    'INEED THEFO URONE ONE'
    """
    re_non_alpha = re.compile(r"[^A-Z]")
    digit_strings = ['ZERO', 'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE',
                     'SIX', 'SEVEN', 'EIGHT', 'NINE']

    def __init__(self, phrase):
        self.order = self.order_from_phrase(phrase)

    def encode(self, message):
        results = []
        for line in self.prepare_input(message):
            # Should not send the current line, or the one directly above or below.
            offset = random.randint(2, 24)
            results.append(self.translate_line(line, offset))

        return '\n'.join([self.group_letters(line) for line in results])

    def decode(self, message):
        results = []
        for line in self.prepare_input(message):
            options = [self.translate_line(line, offset) for offset in range(0, 26)]
            best_e = None
            for option in options:
                e = bits(option)
                if best_e is None or e < best_e:
                    best_e = e
                    best_option = option
            results.append(best_option)

        return '\n'.join([self.group_letters(line) for line in results])

    def translate_line(self, line, offset):
        result = ''
        for i in range(len(line)):
            wheel = wheels[self.order[i] - 1]
            j = (wheel.find(line[i]) + offset) % 26
            result += wheel[j]
        return result

    @staticmethod
    def order_from_phrase(phrase):
        """ Follow instructions in section 2 for calculating the number disk
        order from a pass-phrase.

        >>> M94.order_from_phrase("general electric company")
        [11, 6, 17, 7, 22, 1, 14, 8, 15, 9, 3, 24, 23, 13, 4, 5, 20, 16, 21, 2, 18, 25, 12, 10, 19]
        """
        phrase = M94.prepare_input(phrase)[0]
        if len(phrase) < 15:
            raise ValueError("Key too short - should be at least 15 characters (not %d)." %
                             len(phrase))

        if len(phrase) < 25:
            phrase = phrase + phrase
            phrase = phrase[:25]

        order = [0] * 25

        n = 1
        for i in range(26):
            ch = chr(ord('A') + i)
            s = 0
            while s != -1:
                s = phrase.find(ch, s)
                if s != -1:
                    order[s] = n
                    n += 1
                    s += 1

        return order

    @staticmethod
    def prepare_input(s):
        """ Convert string into array of 25-character lines for encoding.

        >>> M94.prepare_input("this is an input string")
        ['THISISANINPUTSTRING']
        >>> M94.prepare_input("meet me at 10 or 9")
        ['MEETMEATONEZEROORNINE']
        """
        s = s.upper()
        for digit in range(10):
            s = s.replace(chr(ord('0') + digit), M94.digit_strings[digit])
        s = M94.re_non_alpha.sub('', s)
        return [s[i:i + 25] for i in range(0, len(s), 25)]

    @staticmethod
    def group_letters(letters):
        return ' '.join([letters[i:i + 5] for i in range(0, len(letters), 5)])


def bits(s):
    """ Calculate the information content (in bits) of the string, w.r.t. English
    bigram frequencies.

    Note that information is -log(p), where p is the probability of the bigram
    occuring.

        p = f/10000
        bits = sum(-log(p))
        bits = sum(log(10000) - log(f)) = N * log(10000) - sum(log(f)

    >>> bits('A')
    0.0
    >>> bits('AB')
    5.362820525534263
    >>> bits('ALONGSTRINGOFENGLISH')
    64.17225113188248
    >>> bits('TWYXPQZYRKLBDG')
    111.95065836232418
    """
    b = 0.0
    for i in range(len(s) - 1):
        (x, y) = [ord(c) - ord('A') for c in s[i:i + 2]]
        b +=  bigrams[x][y]
    return b


if __name__ == '__main__':
    try:
        main()
    except Exception, e:
        print e.message
