# -*- coding: utf-8 -*-

from hurst import hurst_rs
import pandas as pd
import os
for file in os.walk('aaa'):
    for ff in file[2]:
        df = pd.read_csv("aaa/"+ff)
        print(hurst_rs(df['close'].values))