import re
from textprocessor.pipe import Pipe


class LinkRemover(Pipe):

    def __init__(self):
        Pipe.__init__(self)
        self.add_func(self.remove_links)

    @staticmethod
    def remove_links(data):  # removes links
        if type(data) is not str:
            raise Exception("Link remover expects non-tokenized text, text is " + str(type(data)))

        pattern = r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)'
        return re.sub(pattern, '', data)
