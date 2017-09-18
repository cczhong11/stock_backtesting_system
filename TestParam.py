'''file for loop test param'''
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from jy_strategy import Strategy, SMA, MACD, Param, Kalman, HP, Linear_Model
from matplotlib import pylab
from jy_center import *

class Test_param(object):
    '''loop test'''
    def __init__(self):
        self.C = Center(Center_Param())
        self.df = pd.read_csv("600005.XSHG.csv")
        self.result = pd.DataFrame(columns=('name', 'param', 'money','cangwei','roi','alpha','beta','algorithem_volatility','bench_volatility','sharpe_ratio','max_drawdown','win_ratio','transfer_times'))

    def init_t(self):
        self.result = pd.DataFrame(columns=('name', 'param', 'money','cangwei','roi','alpha','beta','algorithem_volatility','bench_volatility','sharpe_ratio','max_drawdown','win_ratio','transfer_times'))

    def get_log(self,p):
        t = (self.C.current_strategy.getname(),p,self.C.Money,self.C.cangwei,self.C.calculate_roi(),self.C.calculate_alpha(),self.C.calculate_beta(),self.C.calcualte_volatility(1),self.C.calcualte_volatility(2),self.C.calcualte_sharpe(),self.C.calcualte_max_drawdown(),self.C.calcualte_win(),self.C.tick,)
        return t

    def insert_log(self,p):
        if pd.isnull(self.result.index.max()):
            iii = -1
        else:
            iii = self.result.index.max()
        l = self.get_log(p)        
        self.result.loc[iii + 1]= l

    def test_LM(self,p):
        #p = 10+range(60)
        #p = [10,20]
        self.init_t()
        for i in p:
            self.C.choose_strategy(Linear_Model('LM',self.df,[i,0.001,-0.001]))   
            self.C.run_test()
            self.insert_log(i)

    def test_SMA(self,p):
        #p = 10+range(60)
        #p = [10,20]
        self.init_t()
        for i in p:
            self.C.choose_strategy(SMA('SMA',self.df,Param([i],i/2,i/2)))   
            self.C.run_test()
            self.insert_log(i)
    def test_MACD(self,p):
        #p = 10+range(60)
        #p = [10,20]
        self.init_t()
        for i in p:
            self.C.choose_strategy(MACD('MACD',self.df,Param(i,0,0)))   
            self.C.run_test()
            self.insert_log(i)
    def test_Kalman(self,p):
        #p = 10+range(60)
        #p = [10,20]
        self.init_t()
        for i in p:
            self.C.choose_strategy(Kalman('Kalman',self.df,[0,1,1,i]))   
            self.C.run_test()
            self.insert_log(i)
    
    def test_HP(self,p):
        #p = 10+range(60)
        #p = [10,20]
        self.init_t()
        for i in p:
            self.C.choose_strategy(HP('HP',self.df,i))   
            self.C.run_test()
            self.insert_log(i)
    def test_MOM(self):
        m1roi = pd.read_csv('m1roi.csv',index_col=0)
        m5roi = pd.read_csv('m5roi.csv',index_col=0)
        m10roi = pd.read_csv('m10roi.csv',index_col=0)
        m15roi = pd.read_csv('m15roi.csv',index_col=0)
        m20roi = pd.read_csv('m20roi.csv',index_col=0)
        m25roi = pd.read_csv('m25roi.csv',index_col=0)
        m30roi = pd.read_csv('m30roi.csv',index_col=0)
        m60roi = pd.read_csv('m60roi.csv',index_col=0)      
        result = pd.concat([m1roi,m5roi ,m10roi,m15roi,m20roi,m25roi,m30roi,m60roi],axis=1,)
        result.columns=['1','5','10','15','20','25','30','60']
        self.result = result

    def test_MOM_t(self,index):
        if index==0:
            m1roi = pd.read_csv('m1roi.csv',index_col=0)
            m5roi = pd.read_csv('m5roi.csv',index_col=0)
            m10roi = pd.read_csv('m10roi.csv',index_col=0)
            m15roi = pd.read_csv('m15roi.csv',index_col=0)
            m20roi = pd.read_csv('m20roi.csv',index_col=0)
            m25roi = pd.read_csv('m25roi.csv',index_col=0)
            m30roi = pd.read_csv('m30roi.csv',index_col=0)
            m60roi = pd.read_csv('m60roi.csv',index_col=0)
            m11roi = pd.read_csv('MACD_30_5_roi_training.csv',index_col=0)
            m55roi = pd.read_csv('MACD_60_20_roi_training.csv',index_col=0)      
            result = pd.concat([m1roi,m5roi ,m10roi,m15roi,m20roi,m25roi,m30roi,m60roi,m11roi,m55roi],axis=1,)
            result.columns=['1','5','10','15','20','25','30','60','30-5','60-20']
        elif index == 1:
            tm1roi =  pd.read_csv('newtestmom/m1roi_2010-01-01_2011-01-01.csv',index_col=0)
            tm5roi =  pd.read_csv('newtestmom/m5roi_2010-01-01_2011-01-01.csv',index_col=0)
            tm10roi = pd.read_csv('newtestmom/m10roi_2010-01-01_2011-01-01.csv',index_col=0)
            tm15roi = pd.read_csv('newtestmom/m15roi_2010-01-01_2011-01-01.csv',index_col=0)
            tm20roi = pd.read_csv('newtestmom/m20roi_2010-01-01_2011-01-01.csv',index_col=0)
            tm25roi = pd.read_csv('newtestmom/m25roi_2010-01-01_2011-01-01.csv',index_col=0)
            tm30roi = pd.read_csv('newtestmom/m30roi_2010-01-01_2011-01-01.csv',index_col=0)
            tm60roi = pd.read_csv('newtestmom/m60roi_2010-01-01_2011-01-01.csv',index_col=0)
            tm11roi =  pd.read_csv('newtestmom/MACD_60_20_roi2010-01-01_2011-01-01.csv',index_col=0)
            tm55roi =  pd.read_csv('newtestmom/MACD_20_5_roi2010-01-01_2011-01-01.csv',index_col=0)
            result = pd.concat([tm1roi,tm5roi ,tm10roi,tm15roi,tm20roi,tm25roi,tm30roi,tm60roi,tm11roi,tm55roi],axis=1,)
            result.columns=['1','5','10','15','20','25','30','60','60-20','20-5']
        elif index == 2:
            tm1roi =  pd.read_csv('newtestmom/m1roi_2011-01-01_2014-01-01.csv',index_col=0)
            tm5roi =  pd.read_csv('newtestmom/m5roi_2011-01-01_2014-01-01.csv',index_col=0)
            tm10roi = pd.read_csv('newtestmom/m10roi_2011-01-01_2014-01-01.csv',index_col=0)
            tm15roi = pd.read_csv('newtestmom/m15roi_2011-01-01_2014-01-01.csv',index_col=0)
            tm20roi = pd.read_csv('newtestmom/m20roi_2011-01-01_2014-01-01.csv',index_col=0)
            tm25roi = pd.read_csv('newtestmom/m25roi_2011-01-01_2014-01-01.csv',index_col=0)
            tm30roi = pd.read_csv('newtestmom/m30roi_2011-01-01_2014-01-01.csv',index_col=0)
            tm60roi = pd.read_csv('newtestmom/m60roi_2011-01-01_2014-01-01.csv',index_col=0)
            tm11roi =  pd.read_csv('newtestmom/MACD_60_20_roi2011-01-01_2014-01-01.csv',index_col=0)
            tm55roi =  pd.read_csv('newtestmom/MACD_20_5_roi2011-01-01_2014-01-01.csv',index_col=0)
            result = pd.concat([tm1roi,tm5roi ,tm10roi,tm15roi,tm20roi,tm25roi,tm30roi,tm60roi,tm11roi,tm55roi],axis=1,)
            result.columns=['1','5','10','15','20','25','30','60','60-20','20-5']
        elif index == 3:
            tm1roi =  pd.read_csv('newtestmom/m1roi_2014-01-01_2015-12-30.csv',index_col=0)
            tm5roi =  pd.read_csv('newtestmom/m5roi_2014-01-01_2015-12-30.csv',index_col=0)
            tm10roi = pd.read_csv('newtestmom/m10roi_2014-01-01_2015-12-30.csv',index_col=0)
            tm15roi = pd.read_csv('newtestmom/m15roi_2014-01-01_2015-12-30.csv',index_col=0)
            tm20roi = pd.read_csv('newtestmom/m20roi_2014-01-01_2015-12-30.csv',index_col=0)
            tm25roi = pd.read_csv('newtestmom/m25roi_2014-01-01_2015-12-30.csv',index_col=0)
            tm30roi = pd.read_csv('newtestmom/m30roi_2014-01-01_2015-12-30.csv',index_col=0)
            tm60roi = pd.read_csv('newtestmom/m60roi_2014-01-01_2015-12-30.csv',index_col=0)
            tm11roi =  pd.read_csv('newtestmom/MACD_60_20_roi2014-01-01_2015-12-30.csv',index_col=0)
            tm55roi =  pd.read_csv('newtestmom/MACD_20_5_roi2014-01-01_2015-12-30.csv',index_col=0)
            result = pd.concat([tm1roi,tm5roi ,tm10roi,tm15roi,tm20roi,tm25roi,tm30roi,tm60roi,tm11roi,tm55roi],axis=1,)
            result.columns=['1','5','10','15','20','25','30','60','60-20','20-5']
        elif index == 4:
            tm1roi =  pd.read_csv('tm1roi.csv',index_col=0)
            tm5roi =  pd.read_csv('tm5roi.csv',index_col=0)
            tm10roi = pd.read_csv('tm10roi.csv',index_col=0)
            tm15roi = pd.read_csv('tm15roi.csv',index_col=0)
            tm20roi = pd.read_csv('tm20roi.csv',index_col=0)
            tm25roi = pd.read_csv('tm25roi.csv',index_col=0)
            tm30roi = pd.read_csv('tm30roi.csv',index_col=0)
            tm60roi = pd.read_csv('tm60roi.csv',index_col=0)
            tm11roi =  pd.read_csv('newtestmom/MACD_60_20_roi2016-01-04_2016-12-30.csv',index_col=0)
            tm55roi =  pd.read_csv('newtestmom/MACD_20_5_roi2016-01-04_2016-12-30.csv',index_col=0)
            result = pd.concat([tm1roi,tm5roi ,tm10roi,tm15roi,tm20roi,tm25roi,tm30roi,tm60roi,tm11roi,tm55roi],axis=1,)
            result.columns=['1','5','10','15','20','25','30','60','60-20','20-5']
        self.result = result