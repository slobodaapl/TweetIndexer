import re
from textprocessor.pipe import Pipe
import enchant


class Validator(Pipe):

    def __init__(self):
        Pipe.__init__(self)
        self.add_func(self.validate)
        self.dict = enchant.Dict("en_US")

    @staticmethod
    def match_string(word):
        filterlist = [r'-+$', r'_+$', r'#+$', r'@+$', r'\*+$', r'\.+$']
        matches = []

        for pat in filterlist:
            matches.append(bool(re.match(pat, word)))

        return not any(matches)

    @staticmethod
    def remove_extra_uni(word):
        if word[0] not in ('#', '@'):
            pat = r'[^a-zA-z]'
            return re.sub(pat, '', word)
        else:
            return word

    def validate(self, data):
        if type(data) is not list:
            raise Exception("Validator expects tokenized list")

        data = [word for word in data if self.match_string(word)]
        data = [x for x in data if len(x) >= 1]
        data = [self.remove_extra_uni(x) for x in data]
        return [x for x in data if len(x) >= 1]
