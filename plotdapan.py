import pandas as pd
from matplotlib import pylab
import numpy as np
bench = pd.read_csv('dapanprice.csv')
bench = bench.transpose()
bbb=bench.loc[:,0].values[1:]
ccc=bench.index[1:]
_, ax = pylab.subplots()
ax.plot(bbb)
ax.set_xticks(np.linspace(0,len(bbb),10))  
ticks = ax.get_xticks()
ticks = ticks[ticks<len(ccc)]   
ax.set_xticklabels([ccc[int(i)] for i in ticks]) # Label x-axis with dates
ax.set_xticklabels(ax.xaxis.get_majorticklabels(), rotation=45)
pylab.show()