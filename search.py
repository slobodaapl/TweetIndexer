from statistics import mean
from textprocessor.transformer import DataTransformer
from flair.models import TextClassifier # for evaluation
from flair.data import Sentence
from jsonpickle import decode
import numpy as np
from json import load
from time import time
import random


class Search:

    def __init__(self):
        print("Loading index, please wait...")
        self.index, self.frequency_index, self.time_index, self.file_index, self.sentiment_index, self.term_counts = self.load_dicts()
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
            txt_groups = []
            user_grp = None

            if "freq" in instr:
                self.parse_freq(instr)
                continue
            if "sentiment" in instr:
                self.parse_sentiment(instr)
                continue
            if 'user:' in instr:
                user_grp = set(self.parse_user(instr))
            if 'text:' in instr:
                for ls in self.parse_text(instr):
                    txt_groups.append(set(ls))

            groups = set().union(*txt_groups)
            if user_grp is not None:
                if len(groups) != 0:
                    groups = groups.intersection(user_grp)
                else:
                    groups = user_grp

            if len(groups) < 1:
                print("\nNo matching tweets found, or invalid Query")
                continue

            self.get_tweets(groups, instr)
            t1 = time()
            print("\n Time elapsed: {}".format(t1-t0))

    def parse_sentiment(self, instr):
        _, user, word = instr.split(":")
        user_grp = set(self.parse_user("user:" + user))
        text_grp = []
        for grp in self.parse_text("text:\"{}\"".format(word)):
            text_grp.append(set([int(x) for x in grp]))

        if len(user_grp) == 0:
            print("No results")
            return

        primegrp = set().union(*text_grp)
        primegrp = user_grp.intersection(primegrp)

        if len(primegrp) == 0:
            print("User never mentions word in query")
            return

        sentiments = [0 for _ in range(len(primegrp))]
        real_sentiments = [0 for _ in range(len(primegrp))]

        for idx, grp in enumerate(primegrp):
            self.tweets_file.seek(self.file_index[grp])
            line = self.tweets_file.readline().strip().split("\t")[1]
            tfline = self.tf(line)

            for word in tfline:
                if word in self.sentiment_index:
                    sentiments[idx] += self.sentiment_index[word]
                else:
                    if word.lower() == '#coronavirus':
                        sentiments[idx] += self.sentiment_index['coronavirus']
                    else:
                        sentiments[idx] += 0

            sentiments[idx] /= len(tfline)

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
                end_idx = idx + iidx
                break

        if end_idx is None:
            user = instr[idx:]
        else:
            user = instr[idx:end_idx]

        if user in self.index['user']:
            return self.index['user'][user]
        else:
            return None

    def parse_text(self, instr):
        text = self.get_text(instr)

        ls = []
        for word in text:
            if word in self.index['text']:
                ls.append(set(self.index['text'][word].keys()))

        return ls

    def get_text(self, instr):
        idx = instr.find('text:')
        idx += 6

        end_idx = None
        for iidx, letter in enumerate(instr[idx + 1:]):
            if letter == "\"":
                end_idx = idx + iidx + 1
                break

        text = instr[idx:end_idx]
        return self.tf(text)

    @staticmethod
    def cosine_similarity(word_props, grp):
        query = []
        doc = []

        for word in word_props:
            query.append(word_props[word]['tf_query_norm'] * word_props[word]['idf'])
            doc.append(word_props[word]['tf_document_norm'][grp] * word_props[word]['idf'])

        if np.sum(query) == 0 or np.sum(doc) == 0:
            return 0

        res = np.dot(query, doc) / (np.linalg.norm(query) * np.linalg.norm(doc))
        if np.isnan(res):
            return 0
        else:
            return res

    def get_tweets(self, primegrp, instr):
        word_props = None
        tweets = []
        debug = {}
        limit = None

        for idx, elem in enumerate(primegrp):
            debug[elem] = idx
            self.tweets_file.seek(self.file_index[int(elem)])
            tweets.append(self.tweets_file.readline())

        if 'text' in instr:
            text = self.get_text(instr)
            word_props = {}

            for word in text:
                word_props[word] = {}
                word_props[word]['tf_query_norm'] = text.count(word)/len(text)
                word_props[word]['tf_document_norm'] = {}

                for grp in primegrp:
                    if word not in self.index['text'] or grp not in self.index['text'][word]:
                        word_props[word]['tf_document_norm'][grp] = 0
                        continue

                    word_props[word]['tf_document_norm'][grp] = self.index['text'][word][grp]/self.term_counts[grp]

                if word in self.index['text']:
                    word_props[word]['idf'] = 1 + np.log((self.n_docs+1) / (len(self.index['text'][word])+1))
                else:
                    word_props[word]['idf'] = 1

        if word_props is not None:
            for idx, (grp, tweet) in enumerate(zip(primegrp, tweets)):
                tweets[idx] = (tweet, "{}%".format(100 * round(self.cosine_similarity(word_props, grp), 3)))
            tweets = list(reversed(sorted(tweets, key=lambda x: x[1])))

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
            limit = min(limit, len(tweets))
            tweets = tweets[:limit]

        if "-o" in instr:
            with open('output.csv', 'w') as file:
                file.writelines(tweets)
        elif "-c" in instr:
            print("Found {} tweets".format(len(tweets)))
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
                open('./resources/sentimentdict.dat', 'r', encoding='utf-8') as sentimentindexfile, \
                open('./resources/termcounts.dat', 'r', encoding='utf-8') as termcountsfile, \
                open('./resources/fileindex.dat', 'r', encoding='utf-8') as fileindexfile:

            return decode(load(indexfile)), decode(load(freqfile)), \
                   decode(load(timeindexfile)), decode(load(fileindexfile)), \
                   decode(load(sentimentindexfile)), decode(load(termcountsfile))


def primitive_search(text):
    print("Results: \n")
    t0 = time()
    with open('data/hydrated_tweets.csv', 'r') as file:
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

