from textprocessor.pipe import Pipe


class Tokenizer(Pipe):

    def __init__(self):
        Pipe.__init__(self)
        self.add_func(self.tokenize)

    @staticmethod
    def tokenize(data):
        return data.split(" ")
