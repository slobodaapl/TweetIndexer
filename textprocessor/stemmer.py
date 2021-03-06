import enchant
from textprocessor.pipe import Pipe


class Stemmer(Pipe):

    def __init__(self):
        Pipe.__init__(self)
        self.dict = enchant.Dict("en_US")
        self.add_func(self.stem)

    def stem(self, data):
        if type(data) is not list:
            raise Exception("Stemmer expects tokenized list")

        for idx, word in enumerate(data):
            if word[-1:] == "s" and len(word) >= 2 and self.dict.check(word[:-1]):
                data[idx] = word[:-1]
            elif word[-1:] == "d" and len(word) >= 2 and self.dict.check(word[:-1]):
                data[idx] = word[:-1]
            elif word[-2:] == "ed" and len(word) >= 3 and self.dict.check(word[:-2]):
                data[idx] = word[:-2]
            elif word[-2:] == "es" and len(word) >= 3 and self.dict.check(word[:-2]):
                data[idx] = word[:-2]
            elif word[-3:] == "ing" and len(word) >= 4 and self.dict.check(word[:-3]):
                data[idx] = word[:-3]
            elif word[-3:] == "ing" and len(word) >= 4 and self.dict.check(word[:-3] + "e"):
                data[idx] = word[:-3] + "e"
            elif word[-4:] == "ning" and len(word) >= 5 and self.dict.check(word[:-4]):
                data[idx] = word[:-4]

        return data
