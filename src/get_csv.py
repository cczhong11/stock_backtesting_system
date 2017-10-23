import pandas as pd
import csv
f = pd.read_csv("newvolumeprice.csv")
#print(list(f.index.values))
for i in list(f.index.values):
    name = 'newv/'+str(f.loc[i][0])+'.csv'
    a = f.loc[i]
    
    a.iloc[0]='volume'    
    with open(name,'w') as f2:
        f2.write('x,volume\n')
    with open(name,'a') as f2:
#f.loc[1][2:][::-1].to_csv()
        
        a[1:2191][::-1].to_csv(name,mode='a')
#print(a)