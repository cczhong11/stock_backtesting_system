'''class for stock'''
from datetime import datetime

class Stock(object):
    def __init__(self,name,time='',price=0):
        self.name = name
        self.time = time
        self.price = price
        self.tick = 1000