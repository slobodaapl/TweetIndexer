from statistics import mean
from textprocessor.transformer import DataTransformer
from flair.models import TextClassifier # for evaluation
from flair.data import Sentence
from jsonpickle import decode
from json import load
from time import time
import random


class Search:

    def __init__(self):
        print("Loading index, please wait...")
        self.index, self.frequency_index, self.time_index, self.file_index, self.sentiment_index = self.load_dicts()
        self.n_docs = self.load_n_docs()
        print("Done. Opening data...")
        self.tweets_file = open('data/hydrated_tweets.csv', 'r', encoding='utf-8')
        print("Done. Setting up text pipeline and sentiment evaluator...")
        self.sentiment_model = TextClassifier.load('en-sentiment')
        self.tf = DataTransformer()
        print("Done.\n")

        try:
            self.init()
        except KeyboardInterrupt:
            print("User quit via Keyboard Interrupt")

    def init(self):
        while (instr := input("\nQUERY: ")) != "":
            t0 = time()
            groups = []

            if "freq" in instr:
                self.parse_freq(instr)
                continue
            if "sentiment" in instr:
                self.parse_sentiment(instr)
                continue
            if 'user:' in instr:
                groups.append(set(self.parse_user(instr)))
            if 'text:' in instr:
                for ls in self.parse_text(instr):
                    groups.append(set(ls))

            if len(groups) >= 2:
                primegrp = groups[0]
                for grp in groups[1:]:
                    primegrp &= grp
            elif len(groups) == 1:
                primegrp = groups[0]
            else:
                print("\nNo matching tweets found, or invalid Query")
                continue

            self.get_tweets(primegrp, instr)
            t1 = time()
            print("\n Time elapsed: {}".format(t1-t0))

    def parse_sentiment(self, instr):
        _, user, word = instr.split(":")
        grps = self.parse_user("user:" + user)
        for grp in self.parse_text("text:\"{}\"".format(word)):
            grps.append(grp)

        if len(grps) == 0:
            print("No results")
            return

        primegrp = grps[0]
        for grp in grps[1:]:
            primegrp &= grp

        if len(primegrp) == 0:
            print("User does not exist or user never mentions word")
            return

        sentiments = [0 for _ in range(len(primegrp))]
        real_sentiments = [0 for _ in range(len(primegrp))]

        for idx, grp in enumerate(primegrp):
            self.tweets_file.seek(self.file_index[grp])
            line = self.tweets_file.readline().strip().split("\t")[1]
            tfline = self.tf(line)

            for word in tfline:
                sentiments[idx] += self.sentiment_index[word]

            sent = Sentence(line)
            self.sentiment_model.predict(sent)
            score = sent.labels[0]
            real_sentiments[idx] = score.score * (-1 if score.value == "NEGATIVE" else 1)

        sentiment = mean(sentiments)
        real_sentiment = mean(real_sentiments)

        print("Sentiment using dictionary: {}".format(sentiment))
        print("Sentiment using AI for evaluation: {}".format(real_sentiment))

    def parse_freq(self, instr):
        if instr == "freq":
            bidx = 0
            eidx = len(self.frequency_index)
        else:
            instr = instr[5:-1]
            bidx, eidx = instr.split(',')
        sorteddict = {k: v for k, v in sorted(self.frequency_index.items(), key=lambda item: item[1])}
        keys = reversed(list(sorteddict.keys())[-bidx:-eidx])

        for key in keys:
            print("{}: {}".format(key, self.frequency_index[key]))

    def parse_user(self, instr):
        idx = instr.find('user:')
        idx += 5

        end_idx = None
        for iidx, letter in enumerate(instr[idx:]):
            if letter == ' ':
                end_idx = idx + iidx + 1

        if end_idx is None:
            user = instr[idx:]
        else:
            user = instr[idx:end_idx]

        if user in self.index['user']:
            return self.index['user'][user]
        else:
            return None

    def parse_text(self, instr):
        idx = instr.find('text:')
        idx += 6

        end_idx = None
        for iidx, letter in enumerate(instr[idx + 1:]):
            if letter == "\"":
                end_idx = idx + iidx + 1
                break

        text = instr[idx:end_idx]
        text = self.tf(text)

        ls = []
        for word in text:
            if word in self.index['text']:
                ls.append(set(self.index['text'][word].keys()))

        return ls

    def get_tweets(self, primegrp, instr):
        tweets = []
        limit = None

        for elem in primegrp:
            self.tweets_file.seek(self.file_index[int(elem)])
            tweets.append(self.tweets_file.readline())

        if "-l" in instr:
            idx = instr.find('-l')
            idx += 2
            endidx = idx+1

            if endidx >= len(instr):
                limit = int(instr[idx])
            else:
                for iidx, letter in enumerate(instr[endidx:]):
                    if iidx == ' ':
                        break
                    endidx += 1
                limit = int(instr[idx:endidx])

        if limit is not None:
            tweets = random.sample(tweets, limit)

        if "-o" in instr:
            with open('output.csv', 'w') as file:
                file.writelines(tweets)
        else:
            print("Results:\n")
            for tweet in tweets:
                print(tweet)

    @staticmethod
    def load_n_docs():
        with open('./resources/indexcheckpoint.dat', 'r') as file:
            return [int(x) for x in file.readline().strip().split(',')][1]

    @staticmethod
    def load_dicts():
        with open('./resources/frequency.dat', 'r', encoding='utf-8') as freqfile, \
                open('./resources/index.dat', 'r', encoding='utf-8') as indexfile, \
                open('./resources/timeindex.dat', 'r', encoding='utf-8') as timeindexfile, \
                open('./resources/fileindex.dat', 'r', encoding='utf-8') as fileindexfile, \
                open('./resources/sentimentdict.dat', 'r', encoding='utf-8') as sentiindexfile:

            return decode(load(indexfile)), decode(load(freqfile)), \
                   decode(load(timeindexfile)), decode(load(fileindexfile)), decode(load(sentiindexfile))


def primitive_search(text):
    print("Results: \n")
    t0 = time()
    with open('scraped.csv', 'r') as file:
        for line in file:
            if text in line:
                print(line)
    t1 = time()
    print("Time elapsed: {}".format(t1 - t0))


# text:"togetherness mandated by our collective"
if __name__ == "__main__":
    s = Search()
    print("Searching via primitive method for \"togetherness mandated by our collective\"")
    primitive_search("togetherness mandated by our collective")

