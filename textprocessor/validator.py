import re
from textprocessor.pipe import Pipe


class Validator(Pipe):

    def __init__(self):
        Pipe.__init__(self)
        self.add_func(self.validate)

    @staticmethod
    def match_string(word):
        filterlist = [r'-+$', r'_+$', r'#+$', r'@+$', r'\*+$', r'\.+$']
        matches = []

        for pat in filterlist:
            matches.append(bool(re.match(pat, word)))

        return not any(matches)

    def validate(self, data):
        if type(data) is not list:
            raise Exception("Validator expects tokenized list")

        data = [word for word in data if self.match_string(word)]
        return [x for x in data if len(x) >= 1]
