import nltk
from textprocessor.pipe import Pipe


class StopwordRemover(Pipe):

    def __init__(self):
        Pipe.__init__(self)
        self.stopword_dict = nltk.corpus.stopwords.words('english')
        self.stopword_dict.remove('not')  # I want to keep not for sentiment analysis
        self.add_func(self.stop_remove)

    def stop_remove(self, data):
        if type(data) is not list:
            raise Exception("Stopword remover expects tokenized list")

        return [word for word in data if word not in self.stopword_dict]
