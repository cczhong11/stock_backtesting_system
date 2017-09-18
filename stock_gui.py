import matplotlib
import tkinter as Tk
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from jy_strategy import Strategy, SMA, MACD, Param, Kalman, HP, Linear_Model,new_Kalman
from matplotlib import pylab
from jy_center import Center_Param, Center
from pandastable import Table
from TestParam import Test_param
matplotlib.use('TkAgg')

from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler


from matplotlib.figure import Figure
class my_app(object):
    def __init__(self):
        self.root = Tk.Tk()
        self.root.wm_title("myapp")
        self.root.geometry('800x600+100+0')
        self.TT = Tk.Frame(self.root)
        self.Labels = []
        self.StringVars = []
        self.CheckVar = []
        self.Checkbox = []
        self.Ent=[]
        f = self.get_figure()
        f1 = pylab.figure()
        f2 = pylab.figure()
        self.set_figure(f,f,f,'')
        self.canvas.mpl_connect('key_press_event', self.on_key_event)
        self.init_menu()
        self.TT.pack()
        self.df = pd.read_csv("600005.XSHG.csv")
        self.filename = "600005.XSHG.csv"
        self.C_param = Center_Param()# 初始化参数
        self.C_param.start_date='2010-01-01'
        self.C_param.end_date = '2015-12-30'
        self.C = Center(self.C_param)   # 实例化交易中心变量
        self.strategy = None
        self.T = Test_param()
        
    def get_figure(self):
        f = Figure(figsize=(5, 4), dpi=100)
        a = f.add_subplot(111)
        t = arange(0.0, 3.0, 0.01)
        s = sin(2*pi*t)
        a.plot(t, s)
        return f
    def destory_all(self,frame0):
        '''destory all widget'''
        for widget in frame0.winfo_children():
            widget.destroy()
    
    def set_table(self,df):
        self.destory_all(self.TT)
        pt = Table(parent=self.TT,dataframe=df)
        pt.show()
        
    def set_table_figure(self,df,x):
        self.destory_all(self.TT)
        frame1 = Tk.Frame(self.TT)
        frame1.pack(fill=Tk.BOTH)
        frame2 = Tk.Frame(self.TT)
        frame2.pack(fill=Tk.BOTH)
        df1 = pd.DataFrame(df.describe())
        df2 = pd.DataFrame(['count','mean','std','min','25%','50%','75%','max'],index=['count','mean','std','min','25%','50%','75%','max'])
        dff = pd.concat([df2,df1],axis=1)
        pt = Table(parent=frame1,dataframe=dff)
        pt.show()
        f1 = pylab.figure()
        pylab.boxplot(df.values)
        pylab.xticks([i+1 for i in range(len(x))], x)
        self.canvas = FigureCanvasTkAgg(f1, master=frame2)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=Tk.LEFT)
    def set_figure(self,f1,f2,f3,s):
        #f = Figure(figsize=(5, 4), dpi=100)
        #a = f.add_subplot(111)
        #t = arange(0.0, 3.0, 0.01)
        #s = sin(2*pi*t)
        #a.plot(t, s)
        # a tk.DrawingArea
        
        self.destory_all(self.TT)
        frame1 = Tk.Frame(self.TT)
        frame1.pack(fill=Tk.BOTH)
        frame2 = Tk.Frame(self.TT)
        frame2.pack(fill=Tk.BOTH)
        frame3 = Tk.Frame(self.TT)
        frame3.pack(fill=Tk.BOTH)
        frame4 = Tk.Frame(self.TT)
        frame4.pack(fill=Tk.BOTH)
        self.canvas = FigureCanvasTkAgg(f1, master=frame1)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=Tk.LEFT)

        self.canvas2 = FigureCanvasTkAgg(f2, master=frame1)
        self.canvas2.show()
        self.canvas2.get_tk_widget().pack(side=Tk.LEFT)
        
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, frame2)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=Tk.LEFT)
        self.toolbar2 = NavigationToolbar2TkAgg(self.canvas2, frame2)
        self.toolbar2.update()
        self.canvas2._tkcanvas.pack(side=Tk.RIGHT)
        self.canvas3 = FigureCanvasTkAgg(f3, master=frame3)
        self.canvas3.show()
        self.canvas3.get_tk_widget().pack(side=Tk.LEFT)
        #self.canvas4 = FigureCanvasTkAgg(f4, master=frame2)
        #self.canvas4.show()
        #self.canvas4.get_tk_widget().pack(side=Tk.LEFT)
        txt = Tk.Text(frame3)
        txt.pack(fill=Tk.BOTH, expand=True,side=Tk.LEFT) 
        
        S = Tk.Scrollbar(frame3,command=txt.yview)
        S.pack(fill=Tk.BOTH, expand=True,side=Tk.LEFT)
        S.config(command=txt.yview)
        txt.config(yscrollcommand=S.set)        
        txt.insert(Tk.END , s)    
        self.toolbar3 = NavigationToolbar2TkAgg(self.canvas3, frame4)
        self.toolbar3.update()
        self.canvas3._tkcanvas.pack(side=Tk.LEFT)
        #button = Tk.Button(master=self.TT, text='Quit', command=self._quit)
        #button.pack(side=Tk.BOTTOM)

    def on_key_event(self,event):
        print('you pressed %s' % event.key)
        key_press_handler(event, self.canvas, self.toolbar)

    def donothing(self):
        '''do nothing'''
        filewin = Tk.Toplevel(self.TT)
        button = Tk.Button(filewin, text="Do nothing button")
        button.pack()
    
    def set_param(self,index):
        
        if index == 0:
            param = ['N','pcombo','ncombo']
        elif index == 1:
            param = ['N1','N2']
        elif index == 2:
            param = ['T','pk','nk']
        elif index == 3:
            param = ['initial_state_mean','initial_state_covariance','observation_covariance','transition_covariance']
        elif index == 4:
            param = ['w']
        elif index == 5:
            param = ['T']
        self.Labels.clear()
        self.StringVars.clear()
        self.Ent.clear()
        self.filewin2 = Tk.Toplevel(self.TT)
        self.filewin2.title("设置参数")
        b_refresh = Tk.Button(self.filewin2, text="OK", command=self.choose_param)    
        i = 0
        for task in param:
            self.StringVars.append(Tk.StringVar())
            self.Labels.append(Tk.Label(self.filewin2, textvariable=self.StringVars[i]))
            self.StringVars[i].set(str(i)+":"+task)
            self.Labels[i].grid(row=i, column=0)
            self.Ent.append(Tk.Entry(self.filewin2))
            self.Ent[i].grid(row=i, column=1)
            i += 1
        b_refresh.grid(row = i+1,column=0)
    def choose_t(self):
        self.Labels.clear()
        self.StringVars.clear()
        self.Ent.clear()
        self.filewin2 = Tk.Toplevel(self.TT)
        b_refresh = Tk.Button(self.filewin2, text="OK", command=self.set_time)    
        i = 0
        for task in ['start time','end time']:
            self.StringVars.append(Tk.StringVar())
            self.Labels.append(Tk.Label(self.filewin2, textvariable=self.StringVars[i]))
            self.StringVars[i].set(str(i)+":"+task)
            self.Labels[i].grid(row=i, column=0)
            self.Ent.append(Tk.Entry(self.filewin2))
            self.Ent[i].grid(row=i, column=1)
            i += 1
        b_refresh.grid(row = i+1,column=0)
    def set_time(self):
        self.st = self.Ent[0].get()
        self.et = self.Ent[1].get()
        self.C_param.start_date = self.st
        self.C_param.end_date = self.et
        self.C = Center(self.C_param)   # 实例化交易中心变量
        self.filewin2.destroy()
    def mom_init(self,jj):
        '''for mom strategy'''
        m5 = pd.read_csv("MOM_"+str(jj)+".csv")
        m5.shape
        m5.columns=['index','time','600004.XSHG.csv', '600005.XSHG.csv', '600006.XSHG.csv', '600007.XSHG.csv', '600008.XSHG.csv', '600009.XSHG.csv', '600010.XSHG.csv', '600011.XSHG.csv', '600012.XSHG.csv', '600015.XSHG.csv', '600016.XSHG.csv', '600017.XSHG.csv', '600018.XSHG.csv', '600019.XSHG.csv', '600020.XSHG.csv', '600021.XSHG.csv', '600022.XSHG.csv', '600026.XSHG.csv', '600027.XSHG.csv', '600028.XSHG.csv', '600029.XSHG.csv', '600030.XSHG.csv', '600031.XSHG.csv', '600033.XSHG.csv', '600035.XSHG.csv', '600036.XSHG.csv', '600037.XSHG.csv', '600038.XSHG.csv', '600039.XSHG.csv', '600048.XSHG.csv', '600050.XSHG.csv', '600051.XSHG.csv', '600052.XSHG.csv', '600053.XSHG.csv', '600054.XSHG.csv', '600055.XSHG.csv', '600056.XSHG.csv', '600057.XSHG.csv', '600058.XSHG.csv', '600059.XSHG.csv', '600060.XSHG.csv', '600061.XSHG.csv', '600062.XSHG.csv', '600063.XSHG.csv', '600064.XSHG.csv', '600066.XSHG.csv', '600067.XSHG.csv', '600068.XSHG.csv', '600069.XSHG.csv', '600070.XSHG.csv', '600071.XSHG.csv', '600072.XSHG.csv', '600073.XSHG.csv', '600074.XSHG.csv', '600075.XSHG.csv', '600076.XSHG.csv', '600077.XSHG.csv', '600078.XSHG.csv', '600079.XSHG.csv', '600080.XSHG.csv', '600081.XSHG.csv', '600082.XSHG.csv', '600083.XSHG.csv', '600084.XSHG.csv', '600085.XSHG.csv', '600086.XSHG.csv', '600088.XSHG.csv', '600089.XSHG.csv', '600090.XSHG.csv', '600091.XSHG.csv', '600093.XSHG.csv', '600095.XSHG.csv', '600096.XSHG.csv', '600097.XSHG.csv', '600098.XSHG.csv', '600099.XSHG.csv', '600100.XSHG.csv']
        mom75=pd.DataFrame(m5.time)
        m75=[]
        for i in m5.index:
            k=m5.ix[i,3:].values
            m75.append(np.percentile(k,75))
        mom75=pd.concat([mom75,pd.DataFrame(m75,columns=['m85'])],axis=1)
        return mom75
        

    def choose_param(self):
        '''for strategy'''
        index  = self.sindex
        if index == 0:
            param = Param([int(self.Ent[0].get())],int(self.Ent[1].get()),int(self.Ent[2].get()))
            self.strategy = SMA('SMA',self.df,param)
        elif index == 1:
            param = Param([int(self.Ent[0].get()),int(self.Ent[1].get())],0,0)
            self.strategy = MACD('MACD',self.df,param)
        elif index == 2:
            param = [int(self.Ent[0].get()),int(self.Ent[1].get()),int(self.Ent[2].get())]
            self.strategy = Linear_Model('LM',self.df,param)
        elif index == 3:
            param = [float(self.Ent[0].get()),float(self.Ent[1].get()),float(self.Ent[2].get()),float(self.Ent[3].get())]
            self.strategy = Kalman('Kalman',self.df,param)
        elif index == 4:
            param = int(self.Ent[0].get())
            self.strategy = HP('HP',self.df,param)
        elif index == 5:
            param = int(self.Ent[0].get())
            self.mom75 = self.mom_init(param)
            self.MOM = param
            cap = pd.read_csv("capitalization11.csv")            
                        
            self.strategy = new_Kalman("new k",self.df,self.filename,cap)
        self.filewin2.destroy()    
        self.filewin.destroy()
    def choose_strategy(self):  
        for index in range(len(self.strategys)):
            if self.CheckVar[index].get() == 1:
                self.set_param(index)
                self.sindex = index
                
                break
    def test_SMA(self):
        
        self.T.test_SMA([20,30,40])
        self.set_table(self.T.result)
    
    def test_MACD(self):
        k = [5,20,60]
        a=[]
        for i in k:    
            for j in k:
                if j>=i:
                    break
                s = [i,j]
                a.append(s)
        self.T.test_MACD(a) 
        self.set_table(self.T.result)
    def test_HP(self):        
        self.T.test_HP([10000,14400,5760000])
        self.set_table(self.T.result)
    def run_plot_m(self):
        self.T.test_MOM()
        self.set_table_figure(self.T.result,['1','5','10','15','20','25','30','60'])
    def run_plot_t(self):
        self.filewin = Tk.Toplevel(self.TT)
        self.CheckVar.clear()
        self.Checkbox.clear()        
        b_refresh = Tk.Button(self.filewin, text="Choose", command=self.run_mom_t)    
        i = 0
        self.strategys = ['2010-01-01~2015-12-30','2010-01-01~2011-01-01','2011-01-01~2014-01-01','2014-01-01~2015-12-30','2016-01-01~2016-12-30']
        #todaywin.geometry('800x600+0+0')
        for task in self.strategys:
            self.CheckVar.append(Tk.IntVar())
            self.Checkbox.append(Tk.Checkbutton(self.filewin, text=str(i)+":"+task, \
                variable=self.CheckVar[i], onvalue=1, offvalue=0, height=1, \
                 width=50))
            self.Checkbox[i].grid(row=i+1, column=0)            
            i += 1
        b_refresh.grid(row = i+1,column=0)
    def run_mom_t(self):
        for index in range(len(self.Checkbox)):
            if self.CheckVar[index].get() == 1:
                self.T.test_MOM_t(index)                
                self.set_table_figure(self.T.result,['1','5','10','15','20','25','30','60','30-5','60-20'])
                self.filewin.destroy()
    def init_menu(self):
        '''initialize Menu'''
        menubar = Tk.Menu(self.root)
        filemenu = Tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Choose Test Datasets", command=self.askopenfile)
        filemenu.add_command(label="Choose Strategy", command=self.choose_s)
        filemenu.add_command(label="Choose Time", command=self.choose_t)
        filemenu.add_command(label="Run", command=self.run_s)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.TT.quit)
        menubar.add_cascade(label="Run", menu=filemenu)

        bmenu = Tk.Menu(menubar, tearoff=0)
        bmenu.add_command(label="Test different param for SMA", command=self.test_SMA)
        bmenu.add_command(label="Test different param for MACD", command=self.test_MACD)
        bmenu.add_command(label="Test different param for HP", command=self.test_HP)
        bmenu.add_command(label="Test different MOM", command=self.run_plot_m)
        bmenu.add_command(label="Test different time period", command=self.run_plot_t)
        #bmenu.add_command(label="Run", command=self.run_s)
        menubar.add_cascade(label="Test Param", menu=bmenu)
        self.root.config(menu=menubar)

    def run_s(self):
        self.C.choose_strategy(self.strategy)
        if self.C.current_strategy.getname()!="new Kalman mom":
            self.C.run_test()
        else:
            self.C.run_test_new(self.mom75)
            self.C.current_strategy.MOM = self.MOM
        f1 = self.C.print_plot_filter()
        f2 = self.C.print_money()
        f3 = self.C.print_trade_log_pic()
        s = self.C.print_result()
        print("here")
        self.set_figure(f1,f2,f3,s)
    def askopenfile(self):
        """Returns an opened file in read mode."""
        self.filename = Tk.filedialog.askopenfilename(initialdir = "E:/Coding/python/my_bishe",title = "Select file",filetypes = (("csv files","*.csv"),("all files","*.*")))
        print(self.filename)
        self.df = pd.read_csv(filename)
    
    def choose_s(self):
        '''choose strategy'''
        self.filewin = Tk.Toplevel(self.TT)
        self.filewin.title("选择策略")
        self.CheckVar.clear()
        self.Checkbox.clear()        
        b_refresh = Tk.Button(self.filewin, text="Choose", command=self.choose_strategy)    
        i = 0
        self.strategys = ['SMA','MACD','Linear Model','Kalman','HP','MOM']
        #todaywin.geometry('800x600+0+0')
        for task in self.strategys:
            self.CheckVar.append(Tk.IntVar())
            self.Checkbox.append(Tk.Checkbutton(self.filewin, text=str(i)+":"+task, \
                variable=self.CheckVar[i], onvalue=1, offvalue=0, height=1, \
                 width=50))
            self.Checkbox[i].grid(row=i+1, column=0)            
            i += 1
        b_refresh.grid(row = i+1,column=0)
    
    def _quit(self):
        self.root.quit()     # stops mainloop
        self.root.destroy()  # this is necessary on Windows to prevent
            
    
myapp = my_app()

myapp.root.mainloop()
# If you put root.destroy() here, it will cause an error if
# the window is closed with the window manager.






