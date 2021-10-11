class Pipeline:

    def __init__(self, line: list):
        self.list = line

    def transform(self, data):
        for pipe in self.list:
            data = pipe.transform(data)
        return data

    def add(self, pipe, pos=None):
        if pos is None:
            self.list.append(pipe)
        else:
            self.list.insert(pos, pipe)