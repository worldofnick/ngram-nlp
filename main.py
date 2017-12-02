import sys
from collections import Counter
import math

def readFile(file_name):
    arr = []
    for line in open(file_name):
        arr.append(line.lower())
    return arr

# Bigrams
def buildBigrams(lines):
    frequenices = Counter()

    for line in lines:
        tokens = line.lower().strip().split()
        prev = 'phi'

        for token in tokens:
            frequenices[prev + ' ' + token] += 1
            prev = token

    return frequenices

# Unigrams
def buildUnigrams(lines):
    frequenices = Counter()
    for line in lines:
        for token in line.strip().split():
            frequenices[token] += 1

    return frequenices

def unigramFrequency(word, frequenices):
    return frequenices[word] / float(sum(frequenices.values()))


def estimateUnigramSentence(sentence, frequencies):
    prob = 0.0
    for word in sentence.split():
        if prob == 0.0:
            prob = unigramFrequency(word, frequencies)
        else:
            prob *= unigramFrequency(word, frequencies)

    return math.log(prob, 2)

def estimateBigramSentence(sentence, unigrams, bigrams, phiCount, smooth):
    prob = 0.0
    prev = 'phi'

    for word in sentence.split():
        if bigrams[prev + ' ' + word] == 0 and not smooth:
            return -1
        if prob == 0.0:
            prob = bigramFrequency(prev, word, unigrams, bigrams, phiCount, smooth)
        else:
            prob *= bigramFrequency(prev, word, unigrams, bigrams, phiCount, smooth)

        prev = word

    return math.log(prob, 2)

def bigramFrequency(B, A, unigrams, bigrams, phiCount, smooth):

    if smooth:
        return bigramFrequencySmoothed(B, A, unigrams, bigrams)

    # A = current
    # B = prev
    num = float(bigrams[B + ' ' + A])
    denom = unigrams[B]

    if B == 'phi':
        denom = phiCount

    return float(num) / float(denom)


def bigramFrequencySmoothed(B, A, unigrams, bigrams):

    bigram = B + ' ' + A
    if bigram not in bigrams:
        bigram_freq = 1
    else:
        bigram_freq = bigrams[bigram] + 1

    b_freq = 0
    for key in bigrams:
        if key.split()[0] == B:
            b_freq += bigrams[key]

    V = len(unigrams)

    return float(bigram_freq) / (b_freq + V + 1)

def train(training):
    unigrams = buildUnigrams(training)
    bigrams = buildBigrams(training)
    return unigrams, bigrams


def evaluate(unigrams, bigrams, sentence, phiCount):
    print 'S = ' + sentence
    sentence = sentence.lower()

    unigramProb = estimateUnigramSentence(sentence, unigrams)
    bigramProb = estimateBigramSentence(sentence, unigrams, bigrams, phiCount, False)
    biggramSmoothedProb = estimateBigramSentence(sentence, unigrams, bigrams, phiCount, True)

    print 'Unsmoothed Unigrams, logprob(S) = %.4f' % (unigramProb)

    if bigramProb == -1:
        print 'Unsmoothed Bigrams, logprob(S) = undefined'
    else:
        print 'Unsmoothed Bigrams, logprob(S) = %.4f' % (bigramProb)

    print 'Smoothed Bigrams, logprob(S) = %.4f\n' % (biggramSmoothedProb)

# Command line arguments
training_file = sys.argv[1]
flag = sys.argv[2]
testing_file = sys.argv[3]

# # Read text from a text file
training = readFile(training_file)
testing = readFile(testing_file)
unigrams, bigrams = train(training)

for sentence in testing:
    evaluate(unigrams, bigrams, sentence, len(training))
