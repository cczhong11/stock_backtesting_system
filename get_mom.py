import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from jy_strategy import Strategy, SMA, MACD, Param, Kalman, HP, Linear_Model,new_Kalman,new_Kalman_0
from matplotlib import pylab
from jy_center import Center_Param, Center
flist=['600004.XSHG.csv', '600005.XSHG.csv', '600006.XSHG.csv', '600007.XSHG.csv', '600008.XSHG.csv', '600009.XSHG.csv', '600010.XSHG.csv', '600011.XSHG.csv', '600012.XSHG.csv', '600015.XSHG.csv', '600016.XSHG.csv', '600017.XSHG.csv', '600018.XSHG.csv', '600019.XSHG.csv', '600020.XSHG.csv', '600021.XSHG.csv', '600022.XSHG.csv', '600026.XSHG.csv', '600027.XSHG.csv', '600028.XSHG.csv', '600029.XSHG.csv', '600030.XSHG.csv', '600031.XSHG.csv', '600033.XSHG.csv', '600035.XSHG.csv', '600036.XSHG.csv', '600037.XSHG.csv', '600038.XSHG.csv', '600039.XSHG.csv', '600048.XSHG.csv', '600050.XSHG.csv', '600051.XSHG.csv', '600052.XSHG.csv', '600053.XSHG.csv', '600054.XSHG.csv', '600055.XSHG.csv', '600056.XSHG.csv', '600057.XSHG.csv', '600058.XSHG.csv', '600059.XSHG.csv', '600060.XSHG.csv', '600061.XSHG.csv', '600062.XSHG.csv', '600063.XSHG.csv', '600064.XSHG.csv', '600066.XSHG.csv', '600067.XSHG.csv', '600068.XSHG.csv', '600069.XSHG.csv', '600070.XSHG.csv', '600071.XSHG.csv', '600072.XSHG.csv', '600073.XSHG.csv', '600074.XSHG.csv', '600075.XSHG.csv', '600076.XSHG.csv', '600077.XSHG.csv', '600078.XSHG.csv', '600079.XSHG.csv', '600080.XSHG.csv', '600081.XSHG.csv', '600082.XSHG.csv', '600083.XSHG.csv', '600084.XSHG.csv', '600085.XSHG.csv', '600086.XSHG.csv', '600088.XSHG.csv', '600089.XSHG.csv', '600090.XSHG.csv', '600091.XSHG.csv', '600093.XSHG.csv', '600095.XSHG.csv', '600096.XSHG.csv', '600097.XSHG.csv', '600098.XSHG.csv', '600099.XSHG.csv', '600100.XSHG.csv']
#mom_log = pd.DataFrame()
i = 0
for k in [1,5,10,15,20,25,30,60]:
    i = 0
    for f in flist:
        df = pd.read_csv("new/"+f)
        C_param = Center_Param()# 初始化参数
        C_param.start_date='2016-01-04'
        C_param.end_date = '2016-12-30'
        C = Center(C_param)
        cap = pd.read_csv("capitalization11.csv")
        C.choose_strategy(new_Kalman_0("new k",df,f,cap))
        C.current_strategy.MOM = k
        C.run_test()
        if i ==0:
            mom_log=pd.DataFrame(C.current_strategy.gtime)
            mom_log=pd.concat([mom_log,pd.DataFrame(C.current_strategy.mom)],axis=1)
        else:
            mom_log=pd.concat([mom_log,pd.DataFrame(C.current_strategy.mom)],axis=1)
        i = i+1
        print(i)
    mom_log.to_csv("TEST_MOM_"+str(k)+".csv")