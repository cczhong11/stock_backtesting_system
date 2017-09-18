'''strategy file'''
import numpy as np
import pandas as pd
from jy_event import BS_Event
from stock import Stock
from hurst import hurst_rs
from pykalman import KalmanFilter,UnscentedKalmanFilter
import scipy as sp
from scipy import linalg as la
from scipy import sparse
from matplotlib import pylab
from statsmodels import regression
class Param(object):
    def __init__(self,N,p,n):
        self.N = N
        self.pcombo=p
        self.ncombo=n


class Strategy(object):
    '''class for all strategy'''
    def __init__(self, name,df, param=None):
        self.name = name
        self.his_ts = []#pd.DataFrame()           # for history data
        self.param = param
        self.c_stock = Stock('')# current stock
        self.df = df
        self.lastdecisionSignal=0
        self.first_B = 0
        self.filter = [0]
        self.trend = []
        self.his_time=[]
        self.MOM = 1

    def get_index_s(self, date):
        ll = self.df[self.df.x==date].index.tolist()
        if len(ll)==1:
            ii = ll[0]
        else:
            date = datetime.strptime(date,"%Y-%M-%d")-timedelta(days=1)   
            date = date.strftime('%Y-%m-%d')  
            ll = self.df[self.df.x==date].index.tolist()
            while len(ll)==0:
                date = datetime.strptime(date,"%Y-%M-%d")-timedelta(days=1)
                date = date.strftime('%Y-%m-%d')  
                ll = self.df[self.df.x==date].index.tolist()
            ii = ll[0]
            print("real date:"+date)
        return ii,date

    def get_history(self, index, start_time, end_time,N=5):    
        # need add index search for stock
        a,_ = self.get_index_s(start_time)
        b,_ = self.get_index_s(end_time)
        if(a>b):
            tmp = a
            a = b
            b = tmp
        tmp = self.df.loc[int(a):int(b)]
        [self.his_ts.append(tmp.loc[b-(i-a),'close']) for i in tmp.index]
        [self.his_time.append(tmp.loc[b-(i-a),'x']) for i in tmp.index]
        self.c_stock.name = index

    def get_new(self,time):
        a = self.df.loc[self.df.x==time]
        self.u_filter(a.iloc[0,1])
        self.his_ts.append(a.iloc[0,1])
        self.his_time.append(a.iloc[0,0])
        self.c_stock.time = time
        self.c_stock.price = float(a['close'])
        
        self.trend.append(self.get_trend())
    
    def u_filter(self, newdata):
        self.filter.append(self.MA_filter(newdata))

    def MA_filter(self,newdata,N = 5):
        '''filter for MA when new data came'''
        if len(self.trend)!=0:
            l = sum(self.his_ts[-N+1:])+newdata
            MA5 = l/N
            
        else:
            MA5 = sum(self.his_ts[-N:])/N        
        return MA5

    def get_trend(self):
        if self.MOM< len(self.filter):
            t = self.filter[-1]-self.filter[-1-self.MOM]
        else:
            t = 0
        return t


    def make_decision(self):
        decision = BS_Event(self.c_stock)        
        this_Signal = self.make_a_decision(decision)
        #decision.print_decision()
        if self.lastdecisionSignal == this_Signal:
            decision.Signal = 0
        else:
            decision.Signal = this_Signal
            self.lastdecisionSignal = this_Signal
        return decision

    def make_a_decision(self,decision):
        
        if decision.stock.price > self.his_ts[-5]:
            this_Signal =1
            if self.first_B==0:
                self.first_B = 1
        elif self.first_B!=0:
            this_Signal = -1
        else:
            this_Signal=0
        return this_Signal
    
    def getname(self):
        return "COMMON"

class SMA(Strategy):
    def __init__(self,name,df, param=None):
        super(SMA,self).__init__(name,df,param)
        self.N = param.N[0]
        self.mpcombo=param.pcombo
        self.mncombo=param.ncombo
        self.pcombo=0
        self.ncombo=0
    def get_history(self, index, start_time, end_time,N=5):    
        # need add index search for stock
        a = self.df[self.df.x==start_time].index.tolist()[0]
        b = self.df[self.df.x==end_time].index.tolist()[0]
        if(a>b):
            tmp = a
            a = b
            b = tmp
        tmp = self.df.loc[int(a):int(b)]
        [self.his_ts.append(tmp.loc[b-(i-a),'close']) for i in tmp.index]
        [self.his_time.append(tmp.loc[b-(i-a),'x']) for i in tmp.index]
        for i in range(len(self.his_ts)-self.N):
            self.u_filter(self.his_ts[i+self.N])
            self.trend.append(self.get_trend())
        self.c_stock.name = index
        
    def u_filter(self, newdata):
        #print(self.MA_filter(newdata, self.param))
        self.filter.append(self.MA_filter(newdata, self.N))

    
    
    def make_a_decision(self):        
        this_Signal=0
        
        if self.trend[-1]>0:
            self.pcombo=self.pcombo+1
        else:
            self.ncombo=self.ncombo+1
        if self.pcombo==self.mpcombo:#param
            this_Signal =1
            self.pcombo=0            
            if self.first_B==0:
                self.first_B = 1
                
        elif self.first_B!=0:
            if self.ncombo >= self.mncombo:
                this_Signal = -1
                self.ncombo = 0 
        
        return this_Signal
        
    def make_decision(self):
        
        decision = BS_Event(self.c_stock)        
        this_Signal = self.make_a_decision()
        #decision.print_decision()
        if self.lastdecisionSignal == this_Signal:
            decision.Signal = 0
        else:
            decision.Signal = this_Signal
            self.lastdecisionSignal = this_Signal
        return decision
    
    def getname(self):
        return "SMA"

class MACD(Strategy):
    def __init__(self,name,df, param=None):
        super(MACD,self).__init__(name,df,param)
        self.N1 = param.N[0]# N1 should be greater than N2
        self.N2 = param.N[1]
        self.filter2 = []
        
    def u_filter(self, newdata):
        self.filter.append(self.MA_filter(newdata,self.N1))
        self.filter2.append(self.MA_filter(newdata,self.N2))
    
    def get_trend(self):
        t = 2/(self.N1-self.N2)*(self.filter2[-1]-self.filter[-1])        
        return t
    def make_decision(self):
        
        decision = BS_Event(self.c_stock)        
        this_Signal = self.make_a_decision()
        #decision.print_decision()
        if self.lastdecisionSignal == this_Signal:
            decision.Signal = 0
        else:
            decision.Signal = this_Signal
            self.lastdecisionSignal = this_Signal
        return decision
        
    def make_a_decision(self):
        if self.trend[-1]>0:
            this_Signal =1
            if self.first_B==0:
                self.first_B = 1
        elif self.first_B!=0:
            this_Signal = -1
        else:
            this_Signal=0
        return this_Signal
    
    def getname(self):
        return "MACD"


class Kalman(Strategy):
    def __init__(self,name,df, param=None):
        super(Kalman,self).__init__(name,df,param)
        self.state_means = np.zeros((df.shape[0], 1))
        self.state_covariances = np.zeros((df.shape[0], 1, 1))
        self.t = 0
        if param==None:
            self.kf = KalmanFilter(transition_matrices = [1],
                  observation_matrices = [1],
                  initial_state_mean = 0,
                  initial_state_covariance = 1,
                  observation_covariance=1,
                  transition_covariance=.01)
        else:
            self.kf = KalmanFilter(transition_matrices = [1],
                  observation_matrices = [1],
                  initial_state_mean = param[0],
                  initial_state_covariance = param[1],
                  observation_covariance=param[2],
                  transition_covariance=param[3])

    
    def get_history(self, index, start_time, end_time):
        # need add index search for stock
        a = self.df[self.df.x==start_time].index.tolist()[0]
        b = self.df[self.df.x==end_time].index.tolist()[0]
        if(a>b):
            tmp = a
            a = b
            b = tmp
        tmp = self.df.loc[int(a):int(b)]
        [self.his_ts.append(tmp.loc[b-(i-a),'close']) for i in tmp.index]
        [self.his_time.append(tmp.loc[b-(i-a),'x']) for i in tmp.index]
        #state_means, state_cov = self.kf.filter(self.his_ts)
        for t in range(len(self.his_ts)-1):
            if t == 0:
                self.state_means[t] = self.his_ts[0]
                self.state_covariances[t] = 1
            self.state_means[t + 1], self.state_covariances[t + 1] = (
                self.kf.filter_update(
                    self.state_means[t],
                    self.state_covariances[t],
                    self.his_ts[t + 1],                    
            )
        )
        self.t = t+1
        self.filter=[i[0] for i in self.state_means if i[0]!=0]
        print(self.state_means)            
        self.c_stock.name = index


    def u_filter(self, newdata):
        self.state_means[self.t], self.state_covariances[self.t] = (
                self.kf.filter_update(
                    self.state_means[self.t-1],
                    self.state_covariances[self.t-1],
                    newdata,              
            ))
        self.filter.append(self.state_means[self.t][0])
        self.t = self.t+1 
        

    
    def make_a_decision(self):
        if self.trend[-1]>0:
            this_Signal =1
            if self.first_B==0:
                self.first_B = 1
        elif self.first_B!=0:
            this_Signal = -1
        else:
            this_Signal=0
        return this_Signal

    def make_decision(self):
        
        decision = BS_Event(self.c_stock)        
        this_Signal = self.make_a_decision()
        #decision.print_decision()
        if self.lastdecisionSignal == this_Signal:
            decision.Signal = 0
        else:
            decision.Signal = this_Signal
            self.lastdecisionSignal = this_Signal
        return decision
        
    def getname(self):
        return "Kalman"

class HP(Strategy):
    def __init__(self,name,df, param=None):
        super(HP,self).__init__(name,df,param)
        self.w = 100000
        if param!=None:
            self.w = param
    def hp_filter(self,y,w):
        # make sure the inputs are the right shape
        m =  len(y)
        n = 1
        a    = sp.array([w, -4*w, ((6*w+1)/2.)])
        d    = sp.tile(a, (m,1))
    
        d[0,1]   = -2.*w
        d[m-2,1] = -2.*w
        d[0,2]   = (1+w)/2.
        d[m-1,2] = (1+w)/2.
        d[1,2]   = (5*w+1)/2.
        d[m-2,2] = (5*w+1)/2.
    
        B = sparse.spdiags(d.T, [-2,-1,0], m, m)
        #print(B)
        B = B+B.T
        #print(B)
        # report the filtered series, s
        s = sp.dot(la.inv(B.todense()),y)
        return s
    
    def get_new(self,time):
        a = self.df.loc[self.df.x==time]
        
        self.his_ts.append(a.iloc[0,1])
        self.his_time.append(a.iloc[0,0])
        self.u_filter()
        self.c_stock.time = time
        self.c_stock.price = float(a['close'])
        self.trend.append(self.get_trend())
    
    def u_filter(self):
        self.filter = self.hp_filter(self.his_ts,self.w)
        
    def getname(self):
        return "HP"
    
    def make_a_decision(self):
        if self.trend[-1]>0:
            this_Signal =1
            if self.first_B==0:
                self.first_B = 1
        elif self.first_B!=0:
            this_Signal = -1
        else:
            this_Signal=0
        return this_Signal

    def make_decision(self):
        
        decision = BS_Event(self.c_stock)        
        this_Signal = self.make_a_decision()
        #decision.print_decision()
        if self.lastdecisionSignal == this_Signal:
            decision.Signal = 0
        else:
            decision.Signal = this_Signal
            self.lastdecisionSignal = this_Signal
        return decision
    '''    
    def print_plot_filter(self,index):
        result = 'E:/tmp1/'+str(index)
        pylab.figure()
        tmp = len(self.his_ts)-len(self.filter)
        x1 = np.arange(len(self.his_ts))
        x2 = np.arange(len(self.filter))+tmp
        pylab.plot(x1,self.his_ts)
        pylab.plot(x2,self.filter)
        pylab.legend(['his_ts','filter'])
        pylab.savefig(result+'filter.png')
        pylab.close()
'''
class Linear_Model(Strategy):
    def __init__(self,name,df, param=None):
        super(Linear_Model,self).__init__(name,df,param)
        self.intercepte = []
        self.T = param[0]
        self.TL = [i for i in range(self.T)]
        self.N = self.T
        self.pt = param[1]
        self.nt = param[2]
    def u_filter(self, newdata):
        if len(self.his_ts)<self.T:
            tmp = len(self.his_ts)-1
            TL = [i for i in range(tmp)]
        else:
            tmp = self.T
            TL = self.TL
        model = np.polyfit(TL,self.his_ts[-tmp:],1)#?
        a = model[0] # Get coefficients of line
        b = model[1]
        self.trend.append(a)
        self.intercepte.append(b)
    
    def get_new(self,time):
        a = self.df.loc[self.df.x==time]
        self.u_filter(a.iloc[0,1])
        self.his_ts.append(a.iloc[0,1])
        self.his_time.append(a.iloc[0,0])
        self.c_stock.time = time
        self.c_stock.price = float(a['close'])
        
    
    def make_decision(self):        
        decision = BS_Event(self.c_stock)        
        this_Signal = self.make_a_decision()
        #decision.print_decision()
        if self.lastdecisionSignal == this_Signal:
            decision.Signal = 0
        else:
            decision.Signal = this_Signal
            self.lastdecisionSignal = this_Signal
        return decision
        
    def make_a_decision(self):
        if self.trend[-1]>self.pt:
            this_Signal =1
            if self.first_B==0:
                self.first_B = 1
        elif self.first_B!=0 and self.trend[-1]<self.nt:
            this_Signal = -1
        else:
            this_Signal=0
        return this_Signal
    
    def getname(self):
        return "LM"
 
class new_Kalman(Strategy):
    def __init__(self,name,df,sname,cap ,param=None):
        super(new_Kalman,self).__init__(name,df,param)
        self.state_means = np.zeros((df.shape[0], 1))
        self.state_covariances = np.zeros((df.shape[0], 1, 1))
        self.t = 0
        self.volume = pd.read_csv("newv/"+sname)
        self.cap = float(cap[cap.code==sname[:-4]].iloc[0,2])#pd.read_csv("capitalization11.csv")
        self.hh = 0
        self.mom = []
        self.gtime=[]
        if param==None:
            self.kf = KalmanFilter(transition_matrices = [1],
                  observation_matrices = [1],
                  initial_state_mean = 0,
                  initial_state_covariance = 1,
                  observation_covariance=1,
                  transition_covariance=.001)
        else:
            self.kf = KalmanFilter(transition_matrices = [1],
                  observation_matrices = [1],
                  initial_state_mean = param[0],
                  initial_state_covariance = param[1],
                  observation_covariance=param[2],
                  transition_covariance=param[3])

    
    def get_history(self, index, start_time, end_time):
        # need add index search for stock
        a = self.df[self.df.x==start_time].index.tolist()[0]
        b = self.df[self.df.x==end_time].index.tolist()[0]
        if(a>b):
            tmp = a
            a = b
            b = tmp
        tmp = self.df.loc[int(a):int(b)]
        [self.his_ts.append(tmp.loc[b-(i-a),'close']) for i in tmp.index]
        [self.his_time.append(tmp.loc[b-(i-a),'x']) for i in tmp.index]
        #state_means, state_cov = self.kf.filter(self.his_ts)
        for t in range(len(self.his_ts)-1):
            if t == 0:
                self.state_means[t] = self.his_ts[0]
                self.state_covariances[t] = 1
            self.state_means[t + 1], self.state_covariances[t + 1] = (
                self.kf.filter_update(
                    self.state_means[t],
                    self.state_covariances[t],
                    self.his_ts[t + 1],
            )
        )
        self.t = t+1
        self.filter=[i[0] for i in self.state_means if i[0]!=0]
        #print(self.state_means)
        self.c_stock.name = index


    def u_filter(self, newdata):
        self.state_means[self.t], self.state_covariances[self.t] = (
                self.kf.filter_update(
                    self.state_means[self.t-1],
                    self.state_covariances[self.t-1],
                    newdata,              
            ))
        self.filter.append(self.state_means[self.t][0])
        self.t = self.t+1 
    
    def get_new(self,time):
        a = self.df.loc[self.df.x==time]
        self.u_filter(a.iloc[0,1])
        self.his_ts.append(a.iloc[0,1])
        self.his_time.append(a.iloc[0,0])
        self.c_stock.time = time
        self.c_stock.price = float(a['close'])
        
        self.trend.append(self.get_trend())
        self.mom.append(self.get_mom(time))
        self.gtime.append(time)
    def get_mom(self,time):
        a = self.df.loc[self.df.x==time]
        v = a.iloc[0,1]
        m = v/self.cap*self.trend[-1]
        return m
    
    def make_a_decision(self,hh):
        if self.trend[-1]>hh and self.trend[-1]>0:
            this_Signal =1
            if self.first_B==0:
                self.first_B = 1
        elif self.first_B!=0 and self.trend[-1]<0:
            this_Signal = -1
        else:
            this_Signal=0
        return this_Signal

    def make_decision(self,hh):
        
        decision = BS_Event(self.c_stock)        
        this_Signal = self.make_a_decision(hh)
        #decision.print_decision()
        if self.lastdecisionSignal == this_Signal:
            decision.Signal = 0
        else:
            decision.Signal = this_Signal
            self.lastdecisionSignal = this_Signal
        return decision
        
    def getname(self):
        return "new Kalman mom"
class new_Kalman_0(Strategy):
    def __init__(self,name,df,sname,cap ,param=None):
        super(new_Kalman_0,self).__init__(name,df,param)
        self.state_means = np.zeros((df.shape[0], 1))
        self.state_covariances = np.zeros((df.shape[0], 1, 1))
        self.t = 0
        self.volume = pd.read_csv("newv/"+sname)
        self.cap = float(cap[cap.code==sname[:-4]].iloc[0,2])#pd.read_csv("capitalization11.csv")
        self.hh = 0
        self.mom = []
        self.gtime=[]
        if param==None:
            self.kf = KalmanFilter(transition_matrices = [1],
                  observation_matrices = [1],
                  initial_state_mean = 0,
                  initial_state_covariance = 1,
                  observation_covariance=1,
                  transition_covariance=.001)
        else:
            self.kf = KalmanFilter(transition_matrices = [1],
                  observation_matrices = [1],
                  initial_state_mean = param[0],
                  initial_state_covariance = param[1],
                  observation_covariance=param[2],
                  transition_covariance=param[3])

    
    def get_history(self, index, start_time, end_time):
        # need add index search for stock
        a = self.df[self.df.x==start_time].index.tolist()[0]
        b = self.df[self.df.x==end_time].index.tolist()[0]
        if(a>b):
            tmp = a
            a = b
            b = tmp
        tmp = self.df.loc[int(a):int(b)]
        [self.his_ts.append(tmp.loc[b-(i-a),'close']) for i in tmp.index]
        [self.his_time.append(tmp.loc[b-(i-a),'x']) for i in tmp.index]
        #state_means, state_cov = self.kf.filter(self.his_ts)
        for t in range(len(self.his_ts)-1):
            if t == 0:
                self.state_means[t] = self.his_ts[0]
                self.state_covariances[t] = 1
            self.state_means[t + 1], self.state_covariances[t + 1] = (
                self.kf.filter_update(
                    self.state_means[t],
                    self.state_covariances[t],
                    self.his_ts[t + 1],                    
            )
        )
        self.t = t+1
        self.filter=[i[0] for i in self.state_means if i[0]!=0]
        #print(self.state_means)            
        self.c_stock.name = index


    def u_filter(self, newdata):
        self.state_means[self.t], self.state_covariances[self.t] = (
                self.kf.filter_update(
                    self.state_means[self.t-1],
                    self.state_covariances[self.t-1],
                    newdata,              
            ))
        self.filter.append(self.state_means[self.t][0])
        self.t = self.t+1 
    
    def get_new(self,time):
        a = self.df.loc[self.df.x==time]
        self.u_filter(a.iloc[0,1])
        self.his_ts.append(a.iloc[0,1])
        self.his_time.append(a.iloc[0,0])
        self.c_stock.time = time
        self.c_stock.price = float(a['close'])
        
        self.trend.append(self.get_trend())
        self.mom.append(self.get_mom(time))
        self.gtime.append(time)
    def get_mom(self,time):
        a = self.df.loc[self.df.x==time]
        v = a.iloc[0,1]
        m = v/self.cap*self.trend[-1]
        return m
    
    def make_a_decision(self):
        if self.trend[-1]>0:
            this_Signal =1
            if self.first_B==0:
                self.first_B = 1
        elif self.first_B!=0 and self.trend[-1]<0:
            this_Signal = -1
        else:
            this_Signal=0
        return this_Signal

    def make_decision(self):
        
        decision = BS_Event(self.c_stock)        
        this_Signal = self.make_a_decision()
        #decision.print_decision()
        if self.lastdecisionSignal == this_Signal:
            decision.Signal = 0
        else:
            decision.Signal = this_Signal
            self.lastdecisionSignal = this_Signal
        return decision
        
    def getname(self):
        return "new Kalman"

class UKF(Strategy):
    def __init__(self,name,df,sname,cap ,param=None):
        super(UKF,self).__init__(name,df,param)
        self.state_means = np.zeros((df.shape[0], 1))
        self.state_covariances = np.zeros((df.shape[0], 1, 1))
        self.t = 0
        self.volume = pd.read_csv("newv/"+sname)
        self.cap = float(cap[cap.code==sname[:-4]].iloc[0,2])#pd.read_csv("capitalization11.csv")
        self.hh = 0
        self.mom = []
        self.gtime=[]
        if param==None:
            self.kf = UnscentedKalmanFilter(
                  observation_covariance=1,
                  transition_covariance=.001)
        else:
            self.kf = UnscentedKalmanFilter(
                  observation_covariance=param[0],
                  transition_covariance=param[1])

    
    def get_history(self, index, start_time, end_time):
        # need add index search for stock
        a = self.df[self.df.x==start_time].index.tolist()[0]
        b = self.df[self.df.x==end_time].index.tolist()[0]
        if(a>b):
            tmp = a
            a = b
            b = tmp
        tmp = self.df.loc[int(a):int(b)]
        [self.his_ts.append(tmp.loc[b-(i-a),'close']) for i in tmp.index]
        [self.his_time.append(tmp.loc[b-(i-a),'x']) for i in tmp.index]
        #state_means, state_cov = self.kf.filter(self.his_ts)
        for t in range(len(self.his_ts)-1):
            if t == 0:
                self.state_means[t] = self.his_ts[0]
                self.state_covariances[t] = 1
            self.state_means[t + 1], self.state_covariances[t + 1] = (
                self.kf.filter_update(
                    self.state_means[t],
                    self.state_covariances[t],
                    self.his_ts[t + 1],                    
            )
        )
        self.t = t+1
        self.filter=[i[0] for i in self.state_means if i[0]!=0]
        #print(self.state_means)            
        self.c_stock.name = index


    def u_filter(self, newdata):
        self.state_means[self.t], self.state_covariances[self.t] = (
                self.kf.filter_update(
                    self.state_means[self.t-1],
                    self.state_covariances[self.t-1],
                    newdata,              
            ))
        self.filter.append(self.state_means[self.t][0])
        self.t = self.t+1 
    
    def get_new(self,time):
        a = self.df.loc[self.df.x==time]
        self.u_filter(a.iloc[0,1])
        self.his_ts.append(a.iloc[0,1])
        self.his_time.append(a.iloc[0,0])
        self.c_stock.time = time
        self.c_stock.price = float(a['close'])
        
        self.trend.append(self.get_trend())
        self.mom.append(self.get_mom(time))
        self.gtime.append(time)
    def get_mom(self,time):
        a = self.df.loc[self.df.x==time]
        v = a.iloc[0,1]
        m = v/self.cap*self.trend[-1]
        return m
    
    def make_a_decision(self):
        if self.trend[-1]>0:
            this_Signal =1
            if self.first_B==0:
                self.first_B = 1
        elif self.first_B!=0 and self.trend[-1]<0:
            this_Signal = -1
        else:
            this_Signal=0
        return this_Signal

    def make_decision(self):
        
        decision = BS_Event(self.c_stock)        
        this_Signal = self.make_a_decision()
        #decision.print_decision()
        if self.lastdecisionSignal == this_Signal:
            decision.Signal = 0
        else:
            decision.Signal = this_Signal
            self.lastdecisionSignal = this_Signal
        return decision
        
    def getname(self):
        return "new UKF "

def test():  
    df = pd.read_csv("600005.XSHG.csv")
    print(hurst_rs(df['close'].values))
    s = Strategy("a",df)
    s.get_history('ss','2009-02-10','2013-02-18')
    print(hurst_rs(s.his_ts))
    s.get_new('2015-02-25')
    s.make_decision()

def test2():
    df = pd.read_csv("600005.XSHG.csv")
    s = MACD("SMA",df,[15,10])
    s.get_history('ss','2009-02-10','2013-02-18')
    
def test3():
    df = pd.read_csv("600005.XSHG.csv")
    s = Kalman("SMA",df)
    s.get_history('ss','2009-02-10','2009-02-12')

def test4():
    df = pd.read_csv("600005.XSHG.csv")
    s = HP("HP",df)
    s.get_history('ss','2009-02-10','2009-02-12')
    endi = df[df['x']=='2009-02-12'].index[0]
    for i in range(endi-1,endi-5,-1):
        s.get_new(df.loc[i]['x'])
        #s.print_plot_filter(endi-i)
        s.make_a_decision()
        
def test5():
    df = pd.read_csv("600005.XSHG.csv")
    s = Linear_Model("Linear Model",df,20)
    s.get_history('ss','2009-02-10','2009-02-12')
    s.get_new("2009-02-13")
def test6():
    df = pd.read_csv("600005.XSHG.csv")
    cap = pd.read_csv("capitalization11.csv")
    s = new_Kalman("new k",df,"600005.XSHG.csv",cap)
    s.get_history('ss','2009-02-10','2009-02-12')
    s.get_new("2009-02-13")
    return s
def test6():
    df = pd.read_csv("600005.XSHG.csv")
    cap = pd.read_csv("capitalization11.csv")
    s = UKF("new k",df,"600005.XSHG.csv",cap)
    s.get_history('ss','2009-02-10','2009-02-12')
    s.get_new("2009-02-13")
    return s