from textprocessor.pipe import Pipe
import re


class WhitespaceCleaner(Pipe):

    def __init__(self):
        Pipe.__init__(self)
        self.add_func(self.remove_whitespace)

    @staticmethod
    def remove_whitespace(data):  # "hello   world " -> "hello world"
        pattern = r'^\s*|\s\s*'
        if type(data) is list:
            for idx, word in enumerate(data):
                data[idx] = re.sub(pattern, ' ', word).strip()
        else:
            data = re.sub(pattern, ' ', data).strip()

        return data
