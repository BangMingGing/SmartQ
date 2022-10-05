class Task():
    def __init__(self):
        self.num1 = 1
        self.num2 = 2

    def add(self, n1, n2):
        return n1 + n2

    def work(self):
        self.add(self.num1, self.num2)