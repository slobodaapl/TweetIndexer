import re
from textprocessor.pipe import Pipe


class UnicodeCleaner(Pipe):

    def __init__(self):
        Pipe.__init__(self)
        self.add_func(self.remove_unicode)

    @staticmethod
    def remove_unicode(data):  # remove non-basic characters and punctuation, but keep hashtags, dashes and underscores
        pat = r'[^a-zA-z#@_\-\s]'
        return re.sub(pat, '', data)
