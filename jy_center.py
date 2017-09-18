'''file for jiaoyi data log'''
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from jy_strategy import Strategy, SMA, MACD, Param, Kalman, HP, Linear_Model,new_Kalman
from matplotlib import pylab

class Center_Param(object):
    '''class for center param'''
    def __init__(self):
        self.money=1000000
        self.dataorder = 1 #if dataorder is 1 means data from nearest to oldest
        self.start_date='2010-01-01'
        self.end_date = '2015-12-30'    

class Center(object):
    '''get jy event and log trade data'''
    def __init__(self, c_param):
        self.Money_0 = c_param.money
        self.Money = c_param.money
        self.param = c_param
        self.cangwei=0
        self.tick = 0 #交易笔数
        self.trade_log = pd.DataFrame(columns=('name', 'time', 'price','tick', 'Signal','his_ts_index','trend'))
        self.current_strategy = None
        self.trade_day = 0
        self.daily_profit=[]
        self.money_on = []
        self.daily_bench_profit=[]
        self.bench = pd.read_csv('dapanprice.csv')
        self.last_stock_price = 0
        self.drawdown = 0
        self.all_money = self.Money
        self.maxM = self.Money

    def choose_strategy(self,name):
        '''choose one as strategy'''
        self.current_strategy = name

    def init(self):
        self.Money_0 = self.param.money
        self.Money = self.param.money        
        self.cangwei=0
        self.tick = 0 #交易笔数
        self.trade_log = pd.DataFrame(columns=('name', 'time', 'price','tick', 'Signal','his_ts_index','trend'))
        self.trade_day = 0
        self.daily_profit=[]
        self.money_on = []
        self.daily_bench_profit=[]
        self.last_stock_price = 0
        self.drawdown = 0
        self.all_money = self.Money
        self.maxM = self.Money

    def insert_log(self,decision):
        '''insert decision to trade log'''
        if pd.isnull(self.trade_log.index.max()):
            iii = -1
        else:
            iii = self.trade_log.index.max()
        l = decision.log_decision()
        l.append(len(self.current_strategy.his_ts)-1)
        l.append(self.current_strategy.trend[-1])
        self.trade_log.loc[iii + 1]= (l)
    
    def run_buy_and_hold(self):
        '''for test and buy'''
        length = self.current_strategy.df.shape[0]
        s_d,real_time = self.get_index(self.param.start_date)
        his_t2 = self.current_strategy.df.loc[s_d-30]['x']
        self.current_strategy.get_history("ss",real_time,his_t2)
        bench_hs=[]
        his_t1 = real_time
        if(real_time>his_t2):
            tmp = real_time
            his_t1 = his_t2
            his_t2 = tmp
        tmp = self.bench.loc[0,his_t1:his_t2]
        [bench_hs.append(tmp.loc[i]) for i in tmp.index]
        start_bench = bench_hs[len(bench_hs)-1]
        self.hislength=len(tmp)
        tick = self.Money // self.current_strategy.his_ts[-1]
        self.cangwei = tick
        
        self.Money = self.Money-tick*self.current_strategy.his_ts[-1]
        #s_d = self.get_index(self.param.start_date)
        e_d,real_end = self.get_index(self.param.end_date)
        for i in range(s_d-30,e_d,-1):
            
            self.current_strategy.get_new(self.current_strategy.df.loc[i]['x'])
            bench_hs.append(self.bench.loc[0,self.current_strategy.df.loc[i]['x']])
            #print(self.bench.loc[0,])            
            self.trade_day = self.trade_day+1
            price = self.current_strategy.his_ts[-1]
            self.all_money = self.Money+self.cangwei*price
            self.money_on.append(self.all_money)
            if self.all_money > self.maxM:
                self.maxM = self.all_money
            self.drawdown = max(self.drawdown, (self.maxM-(self.all_money))/self.maxM) 
            self.daily_profit.append(self.calculate_roi())
            self.daily_bench_profit.append((bench_hs[-1]-start_bench)/start_bench)



    def run_test(self):
        '''for test and buy'''
        self.init()
        tt = 30
        length = self.current_strategy.df.shape[0]
        if self.current_strategy.getname()=="MACD":
            tt = self.current_strategy.param.N[0]
            tt = int(tt)
            print(tt)
        s_d, real_time = self.get_index(self.param.start_date)
        
        his_t2 = self.current_strategy.df.loc[s_d-tt]['x']
        self.current_strategy.get_history("ss",real_time,his_t2)
        bench_hs=[]
        df = self.current_strategy.df
        his_t1 = real_time
        if(real_time>his_t2):
            tmp = real_time
            his_t1 = his_t2
            his_t2 = tmp
        tmp = self.bench.loc[0,his_t1:his_t2]
        [bench_hs.append(tmp.loc[i]) for i in tmp.index]
        start_bench = bench_hs[len(bench_hs)-1]
        self.hislength=len(tmp)
        #s_d = self.get_index(self.param.start_date)
        e_d,real_end = self.get_index(self.param.end_date)
        for i in range(s_d-tt,e_d,-1):            
            self.current_strategy.get_new(df.loc[i]['x'])
            bench_hs.append(self.bench.loc[0,df.loc[i]['x']])
            #print(self.bench.loc[0,])
            d = self.current_strategy.make_decision()
            self.trade_day = self.trade_day+1
            self.all_money = self.Money+self.cangwei*d.stock.price
            self.money_on.append(self.all_money)
            if self.all_money > self.maxM:
                self.maxM = self.all_money
            self.drawdown = max(self.drawdown, (self.maxM-(self.all_money))/self.maxM)
                
            if d.Signal!=0:                
                if d.Signal == 1:
                    d.stock.tick = int(self.Money/d.stock.price)
                    if self.could_buy(d) and d.stock.tick > 0:
                        self.Money = self.Money - d.stock.price*d.stock.tick
                        self.cangwei = self.cangwei+d.stock.tick
                        self.insert_log(d)
                        self.tick = self.tick+1
                    else:
                        d.Signal = 0
                        self.current_strategy.lastdecisionSignal = 0
                if d.Signal == -1:
                    d.stock.tick=self.cangwei
                    if self.cangwei>=d.stock.tick and d.stock.tick>0:
                        self.Money = self.Money + d.stock.price*d.stock.tick
                        self.cangwei = self.cangwei-d.stock.tick
                        self.insert_log(d)
                        self.tick = self.tick+1
                    else:
                        d.Signal = 0
                        self.current_strategy.lastdecisionSignal = 0
             
            self.daily_profit.append(self.calculate_roi())
            self.daily_bench_profit.append((bench_hs[-1]-start_bench)/start_bench)
        #self.last_stock_price = d.stock.price
    
    def run_test_new(self,mom75):
        '''for test and buy'''
        self.init()
        tt = 30
        length = self.current_strategy.df.shape[0]
        if self.current_strategy.getname()=="MACD":
            tt = self.current_strategy.param.N[0]
            tt = int(tt)
            print(tt)
        s_d, real_time = self.get_index(self.param.start_date)
        
        his_t2 = self.current_strategy.df.loc[s_d-tt]['x']
        self.current_strategy.get_history("ss",real_time,his_t2)
        bench_hs=[]
        df = self.current_strategy.df
        his_t1 = real_time
        if(real_time>his_t2):
            tmp = real_time
            his_t1 = his_t2
            his_t2 = tmp
        tmp = self.bench.loc[0,his_t1:his_t2]
        [bench_hs.append(tmp.loc[i]) for i in tmp.index]
        start_bench = bench_hs[len(bench_hs)-1]
        self.hislength=len(tmp)
        #s_d = self.get_index(self.param.start_date)
        e_d,real_end = self.get_index(self.param.end_date)
        for i in range(s_d-tt,e_d,-1):            
            self.current_strategy.get_new(df.loc[i]['x'])
            bench_hs.append(self.bench.loc[0,df.loc[i]['x']])
            #print(self.bench.loc[0,])
            try:
                ddp = mom75[df.loc[i]['x']].m75[0]
            except:
                ddp = 0
            d = self.current_strategy.make_decision(ddp)
            self.trade_day = self.trade_day+1
            self.all_money = self.Money+self.cangwei*d.stock.price
            self.money_on.append(self.all_money)
            if self.all_money > self.maxM:
                self.maxM = self.all_money
            self.drawdown = max(self.drawdown, (self.maxM-(self.all_money))/self.maxM)
                
            if d.Signal!=0:                
                if d.Signal == 1:
                    d.stock.tick = int(self.Money/d.stock.price)
                    if self.could_buy(d) and d.stock.tick > 0:
                        self.Money = self.Money - d.stock.price*d.stock.tick
                        self.cangwei = self.cangwei+d.stock.tick
                        self.insert_log(d)
                        self.tick = self.tick+1
                    else:
                        d.Signal = 0
                        self.current_strategy.lastdecisionSignal = 0
                if d.Signal == -1:
                    d.stock.tick=self.cangwei
                    if self.cangwei>=d.stock.tick and d.stock.tick>0:
                        self.Money = self.Money + d.stock.price*d.stock.tick
                        self.cangwei = self.cangwei-d.stock.tick
                        self.insert_log(d)
                        self.tick = self.tick+1
                    else:
                        d.Signal = 0
                        self.current_strategy.lastdecisionSignal = 0
             
            self.daily_profit.append(self.calculate_roi())
            self.daily_bench_profit.append((bench_hs[-1]-start_bench)/start_bench)
        #self.last_stock_price = d.stock.price


    def get_index(self,date):    
        ll = self.current_strategy.df[self.current_strategy.df.x==date].index.tolist()
        if len(ll)==1:
            ii = ll[0]
        else:
            date = datetime.strptime(date,"%Y-%M-%d")-timedelta(days=1)   
            date = date.strftime('%Y-%m-%d')  
            ll = self.current_strategy.df[self.current_strategy.df.x==date].index.tolist()
            while len(ll)==0:
                date = datetime.strptime(date,"%Y-%M-%d")-timedelta(days=1)
                date = date.strftime('%Y-%m-%d')  
                ll = self.current_strategy.df[self.current_strategy.df.x==date].index.tolist()
            ii = ll[0]
            print("real date:"+date)
        return ii,date
    def could_buy(self,d):
        '''calculate whether could i buy it'''
        if self.Money - d.stock.price*d.stock.tick>0:
            return True
        else:
            return False

    def calculate_roi(self):
        '''calucate roi'''
        result = (self.all_money-self.Money_0)/(self.Money_0)
        return result

    def calculate_beta(self):
        '''calcualte beta'''
        tmp = np.cov(self.daily_profit, self.daily_bench_profit)[0][1]
        return tmp/np.var(self.daily_bench_profit)
        
    def calcualte_max_drawdown(self):
        return self.drawdown
        
    
    def calculate_alpha(self):
        '''calculate alpha'''
        N = 250/len(self.daily_profit)
        if self.daily_profit[-1]+1>0:
            Rp = (abs(1+self.daily_profit[-1]))**(N)
        else:
            Rp = -(abs(1+self.daily_profit[-1]))**(N)
        Rm = (1+self.daily_bench_profit[-1])**(N)
        beta = self.calculate_beta()
        alpha = Rp-(0.04+beta*(Rm-0.04))
        return alpha
        
    def calcualte_volatility(self,aob):
        if aob == 1:# for algorithem
            data = self.daily_profit
        else:
            data = self.daily_bench_profit
        return np.sqrt(250*np.var(data))
    
    def calcualte_sharpe(self):
        N = 250/len(self.daily_profit)
        if self.daily_profit[-1]+1<0:
            Rp = (abs(1+self.daily_profit[-1]))**(N)
        else:
            Rp = -(abs(1+self.daily_profit[-1]))**(N)
        Rp = (1+self.daily_profit[-1])**(N)
        
        return (Rp-0.04)/self.calcualte_volatility(1)

    def calcualte_win(self):
        sum0 = 0
        for i in range(len(self.daily_profit)):
            if self.daily_profit[i]>0:
                sum0 = sum0+1
        return sum0/len(self.daily_profit)
    
    def get_result_file(self):
        fp = 'result/'
        sp = self.current_strategy.getname()
        if self.current_strategy.param == None:
            result = fp+sp
        elif sp=="LM":
            pp = '_'+str(self.current_strategy.param[0])
            result = fp+sp+pp
        elif sp=="Kalman":
            pp = '_'+str(self.current_strategy.param[3])
            result = fp+sp+pp
        elif sp=="HP":
            pp = '_'+str(self.current_strategy.w)
            result = fp+sp+pp
        elif len(self.current_strategy.param.N)==1:
            pp = '_'+str(self.current_strategy.param.N[0])+'_'+str(self.current_strategy.param.pcombo)+\
            '_'+str(self.current_strategy.param.ncombo)
            result = fp+sp+pp
        else:
            ll = ''
            for i in self.current_strategy.param.N:
                ll = ll+'_'+str(i)+'_'
            result = fp+sp+ll
        return result
        
    def print_plot_profit(self):
        result = self.get_result_file()
        pylab.figure()
        pylab.plot(self.daily_bench_profit)
        pylab.plot(self.daily_profit)
        pylab.legend(['bench','profit'])       
        pylab.savefig(result+'profit.png')
    
    def print_his_plot(self):
        _, ax = pylab.subplots()
        ax.plot(self.current_strategy.his_ts)
        ticks = ax.get_xticks()
        ticks = ticks[ticks<len(self.current_strategy.his_ts)]   
        ax.set_xticklabels([self.current_strategy.his_time[int(i)] for i in ticks]) # Label x-axis with dates
        ax.set_xticklabels(ax.xaxis.get_majorticklabels(), rotation=45)

    def print_trade_log_pic(self,offset=0,offset2=None):
        result = self.get_result_file()
        try:
            if self.current_strategy.getname()=="SMA" or self.current_strategy.getname()=="MACD":
                self.current_strategy.filter.remove(0)
        except:
            a = 1
        f, ax = pylab.subplots()
        ax.plot(self.current_strategy.his_ts[offset:offset2])
        ticks = ax.get_xticks()           
        ticks = ticks[ticks<len(self.current_strategy.his_ts[offset:offset2])]             
        ax.set_xticklabels([self.current_strategy.his_time[int(i)] for i in ticks]) # Label x-axis with dates
        ax.set_xticklabels(ax.xaxis.get_majorticklabels(), rotation=45)
        ss = self.trade_log[self.trade_log.Signal==-1]
        cc = self.trade_log[self.trade_log.Signal==1]
        sa = [80]*len(ss)
        cs = [40]*len(cc)
        pylab.scatter(cc.his_ts_index,cc.price,color='red')
        pylab.scatter(ss.his_ts_index,ss.price,color='green')
        tmp = len(self.current_strategy.his_ts)-len(self.current_strategy.filter)
        x1 = np.arange(len(self.current_strategy.his_ts))
        x2 = np.arange(len(self.current_strategy.filter))+tmp
        if self.current_strategy.getname()!="LM":
            pylab.plot(x2,self.current_strategy.filter,color='r')
            if self.current_strategy.getname()=="MACD":
                pylab.plot(x2,self.current_strategy.filter2,color='g')
        return f      
        pylab.savefig(result+'trade_log.png')

    def print_money(self):
        f, ax = pylab.subplots()
        ax.plot(self.money_on)
        ticks = ax.get_xticks()
        ticks = ticks[ticks<len(self.current_strategy.his_ts)] 
        ax.set_xticklabels([self.current_strategy.his_time[int(i)] for i in ticks[:]]) # Label x-axis with dates   
        ax.set_xticklabels(ax.xaxis.get_majorticklabels(), rotation=45)
        return f
    def print_plot_filter(self):
        if self.current_strategy.getname()=="SMA" or self.current_strategy.getname()=="MACD":
            self.current_strategy.filter.remove(0)
        if self.current_strategy.getname()=="MACD":
            result = self.get_result_file()
            f = pylab.figure()
            
            tmp = len(self.current_strategy.his_ts)-len(self.current_strategy.filter)
            tmp2 = len(self.current_strategy.his_ts)-len(self.current_strategy.filter2)
            x1 = np.arange(len(self.current_strategy.his_ts))
            x2 = np.arange(len(self.current_strategy.filter))+tmp
            x3 = np.arange(len(self.current_strategy.filter2))+tmp2
            pylab.plot(x1,self.current_strategy.his_ts)
            pylab.plot(x2,self.current_strategy.filter)
            pylab.plot(x3,self.current_strategy.filter2)
            pylab.legend(['his_ts','filter','filter2'])        
            
            pylab.savefig(result+'filter.png')
            return f
        result = self.get_result_file()
        f = pylab.figure()
        tmp = len(self.current_strategy.his_ts)-len(self.current_strategy.filter)
        x1 = np.arange(len(self.current_strategy.his_ts))
        x2 = np.arange(len(self.current_strategy.filter))+tmp
        pylab.plot(x1,self.current_strategy.his_ts)
        pylab.plot(x2,self.current_strategy.filter,color='r')
        pylab.legend(['his_ts','filter'])        
        pylab.savefig(result+'filter.png')
        return f
  
    def print_result(self):
        s = ''
        print("money:"+str(self.Money))
        print("cangwei:"+str(self.cangwei))
        print("roi:"+str(self.calculate_roi()))
        print("alpha:"+str(self.calculate_alpha()))
        print("beta:"+str(self.calculate_beta()))
        print("algorithem volatility: "+str(self.calcualte_volatility(1)))
        print("bench volatility: "+str(self.calcualte_volatility(2)))
        print("sharpe ratio: "+str(self.calcualte_sharpe()))
        print("max drawdown: "+str(self.calcualte_max_drawdown()))
        print("win ratio:"+str(self.calcualte_win()))
        print("transfer times:"+str(self.tick))
        s=s+"money:"+str(self.Money)+'\n'
        s=s+"cangwei:"+str(self.cangwei)+'\n'
        s=s+"roi:"+str(self.calculate_roi())+'\n'
        s=s+"alpha:"+str(self.calculate_alpha())+'\n'
        s=s+"beta:"+str(self.calculate_beta())+'\n'
        s=s+"algorithem volatility: "+str(self.calcualte_volatility(1))+'\n'
        s=s+"bench volatility: "+str(self.calcualte_volatility(2))+'\n'
        s=s+"sharpe ratio: "+str(self.calcualte_sharpe())+'\n'
        s=s+"max drawdown: "+str(self.calcualte_max_drawdown())+'\n'
        s=s+"win ratio:"+str(self.calcualte_win())+'\n'
        s=s+"transfer times:"+str(self.tick)+'\n'
        return s
    def write_to_csv(self):
        '''write result in a txt file with name. Also write some result data in csv for future plot'''
        result = self.get_result_file()
        sp = self.current_strategy.getname()
        self.trade_log.to_csv(result+'tradelog.csv')
        # add more stock name in the future
        # add max drawback
        f = open(result+'result.txt','w+')
        f.write("money:"+str(self.Money)+'\n')
        f.write("cangwei:"+str(self.cangwei)+'\n')
        f.write("roi:"+str(self.calculate_roi())+'\n')
        f.write("alpha:"+str(self.calculate_alpha())+'\n')
        f.write("algorithem volatility: "+str(self.calcualte_volatility(1))+'\n')
        f.write("bench volatility: "+str(self.calcualte_volatility(2))+'\n')
        f.write("sharpe ratio: "+str(self.calcualte_sharpe())+'\n')
        f.write("win ratio:"+str(self.calcualte_win())+'\n')
        f.write("max drawdown:"+str(self.calcualte_max_drawdown())+'\n')
        f.write("trend:\n")
        f.write(str(self.current_strategy.trend)+"\n")
        f.write("filter:\n")
        f.write(str(self.current_strategy.filter)+"\n")
        if sp=="MACD":
            f.write("filter2:\n")
            f.write(str(self.current_strategy.filter2))
        f.close()


def test():
    df = pd.read_csv("600005.XSHG.csv")
    C = Center(Center_Param())
    C.choose_strategy(Linear_Model("a", df,20))
    C.run_test()
    pylab.plot(C.money_on)
    #C.current_strategy.get_new('2016/2/19')
    #C.insert_log(C.current_strategy.make_decision())
    print(C.trade_log)
    print("money:"+str(C.Money))
    print("cangwei:"+str(C.cangwei))
    print("roi:"+str(C.calculate_roi()))
    print("alpha:"+str(C.calculate_alpha()))
    print("algorithem volatility: "+str(C.calcualte_volatility(1)))
    print("bench volatility: "+str(C.calcualte_volatility(2)))
    print("sharpe ratio: "+str(C.calcualte_sharpe()))
    print("max drawdown: "+str(C.calcualte_max_drawdown()))
    print("win ratio:"+str(C.calcualte_win()))
    #C.write_to_csv()
    #C.print_plot_filter()
    #C.print_plot_profit()
    C.print_trade_log_pic()
    pylab.show()

def test2():
    df = pd.read_csv("600006.XSHG.csv")
    C = Center(Center_Param())
    cap = pd.read_csv("capitalization11.csv")
    C.choose_strategy(new_Kalman("new k",df,"600006.XSHG.csv",cap))
    C.current_strategy.MOM = 10
    C.run_test()
    pylab.hist(C.current_strategy.mom)
    return C