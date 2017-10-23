# -*- coding: utf-8 -*-
"""
Created on Sun Apr 30 10:52:29 2017

@author: tanyz
"""

import scipy as sp
from matplotlib.pyplot import *
from scipy import linalg as la
from scipy import sparse
import pandas as pd

def hp_filter(y,w):
    # make sure the inputs are the right shape
    m,n  = y.shape
    if m < n:
        y = y.T
        m = n

    a    = sp.array([w, -4*w, ((6*w+1)/2.)])
    d    = sp.tile(a, (m,1))

    d[0,1]   = -2.*w
    d[m-2,1] = -2.*w
    d[0,2]   = (1+w)/2.
    d[m-1,2] = (1+w)/2.
    d[1,2]   = (5*w+1)/2.
    d[m-2,2] = (5*w+1)/2.

    B = sparse.spdiags(d.T, [-2,-1,0], m, m)
    B = B+B.T

    # report the filtered series, s
    s = sp.dot(la.inv(B.todense()),y)
    return s


def testhp():
    # read in and assign variables
    df = pd.read_csv("600005.XSHG.csv")
    data = df['close']
    
    data = sp.log(data)
    y    = sp.atleast_2d(data)
    s    = hp_filter(y,1600)
    devs = y.T - s

    # plot the data, the filtered series, and abs. deviation
    subplot(211)
    plot(data, 'k')
    plot(s,'r-')
    title("Data and HP filter")
    ylabel("log of investment")
    
    subplot(212)
    plot(devs,'k')
    title("Stationary series")
    ylabel("log of investment")
    xlabel("Quarters from 1947Q1-2011Q4")
    show()

testhp()