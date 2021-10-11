from textprocessor.pipe import Pipe
import contractions
import re


class ContractionExpander(Pipe):

    def __init__(self):
        Pipe.__init__(self)
        self.add_func(self.expand_contractions)

    @staticmethod
    def expand_contractions(data):  # it's -> it is
        return contractions.fix(data)
