import unicodedata
from textprocessor.pipe import Pipe


class AccentRemover(Pipe):

    def __init__(self):
        Pipe.__init__(self)
        self.add_func(self.remove_accents)

    @staticmethod
    def remove_accents(data):  # á to a
        return unicodedata.normalize('NFKD', data).encode('ascii', 'ignore').decode('utf-8', 'ignore')
