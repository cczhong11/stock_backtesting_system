'''jiaoyi event file'''
from stock import Stock

class BS_Event(object):
    '''class for all strategy'''
    def __init__(self, stock):

        self.Signal = 1 #1 for buy -1 for sell 0 for hold
        self.stock = stock
        
        
    def print_decision(self):
        if self.Signal==1:
            print(str(self.stock.name)+" BUY "+self.stock.time+"  price:"+str(self.stock.price)+"  tick:"+str(self.stock.tick))
        elif self.Signal == -1 :           
            print(str(self.stock.name)+" SELL "+self.stock.time+"  price:"+str(self.stock.price)+"  tick:"+str(self.stock.tick))
        elif self.Signal == 0 :           
            print(str(self.stock.name)+" HOLD "+self.stock.time+"  price:"+str(self.stock.price)+"  tick:"+str(self.stock.tick))


    def log_decision(self):
        '''log to '''
        return [self.stock.name, self.stock.time, self.stock.price, self.stock.tick,self.Signal]
