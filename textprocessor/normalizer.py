from textprocessor.pipe import Pipe


class Normalizer(Pipe):

    def __init__(self):
        Pipe.__init__(self)
        self.add_func(self.lowcap)

    @staticmethod
    def lowcap(data):  # A -> a
        if type(data) is list:
            for idx, word in enumerate(data):
                if not word.isupper() or word[0] == '#' or len(word) == 1:
                    data[idx] = word.lower()
        else:
            return data.lower()

        return data
