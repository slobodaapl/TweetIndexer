class Pipe:

    def __init__(self):
        self.tf_func = []

    def transform(self, data):
        for func in self.tf_func:
            data = func(data)
        return data

    def add_func(self, func):
        self.tf_func.append(func)

    def set_func(self, funcs: list):
        self.tf_func = funcs