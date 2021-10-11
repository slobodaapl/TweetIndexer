from textblob import Word
from textprocessor.pipe import Pipe


class Lemmatizer(Pipe):

    def __init__(self):
        Pipe.__init__(self)
        self.add_func(self.lemmatize)

    def lemmatize(self, data):
        if type(data) is list:
            for idx, word in enumerate(data):
                if len(word) >= 3:
                    data[idx] = Word(word).lemmatize()
        else:
            raise Exception("Data must be tokenized for lemmatization")

        return data
