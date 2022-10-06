class Task():
    def __init__(self):
        self.num1 = 1
        self.num2 = 1
        
    def add(self, n1, n2):
        return n1 + n2

    def work(self):
        return {'add_result' : self.add(self.num1, self.num2)}
    
    def wtw(self):
        return 'add 1, 1'
        
