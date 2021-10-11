from textprocessor.pipe import Pipe


class WordReplacer(Pipe):

    def __init__(self):
        Pipe.__init__(self)
        self.replacements = {}
        self.load_dict()
        self.add_func(self.replace_words)

    def load_dict(self):
        with open("./resources/repl.csv") as f:
            for line in f:
                key, val = line.split(':')
                self.replacements[key] = val.strip()

    def replace_words(self, data):
        if type(data) is not list:
            raise Exception("Word replacer expects tokenized list")

        for idx, word in enumerate(data):
            if word in self.replacements:
                data[idx] = self.replacements[word]

        return data