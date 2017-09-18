import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from jy_strategy import Strategy, SMA, MACD, Param, Kalman, HP, Linear_Model
from matplotlib import pylab

for i in os.listdir("aaa"):
    df = pd.read_csv("aaa/"+i)
    s = HP("HP",df)
    s.filter = s.hp_filter(df.close.values, 100000)
    print(i)
    ofile = open("huice/new_"+i+".txt",'w')
    for k in range(len(s.filter)):
        ofile.write(str(s.filter[-k-1])+" ")
    ofile.close()