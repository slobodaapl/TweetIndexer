from textblob import Word
from textprocessor.pipe import Pipe


class SpellingFixer(Pipe): #Lion

    def __init__(self):
        Pipe.__init__(self)
        self.add_func(self.spellcheck)

    @staticmethod
    def spellcheck(data):
        if type(data) is not list:
            raise Exception("SpellingFixer expects tokenized list")

        for idx, word in enumerate(data):
            w = Word(word)
            suggestion, prob = w.spellcheck()[0]
            if prob >= 0.6:
                data[idx] = suggestion

        return data
