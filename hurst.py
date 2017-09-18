# -*- coding: utf-8 -*-

import numpy as np
from numpy.random import randn
import pandas as pd
import nolds
def rs(data, n):
  """
  Calculates an individual R/S value in the rescaled range approach for
  a given n.
  Note: This is just a helper function for hurs_rs and should not be called
  directly.
  Args:
    data (array of float):
      time series
    n (float):
      size of the subseries in which data should be split
  Returns:
    float:
      (R/S)_n
  """
  total_N = len(data)
  # cut values at the end of data to make the array divisible by n
  data = data[:total_N - (total_N % n)]
  # split remaining data into subsequences of length n
  seqs = np.reshape(data, (total_N // n, n))
  # calculate means of subsequences
  means = np.mean(seqs, axis=1)
  # normalize subsequences by substracting mean
  y = seqs - means.reshape((total_N // n, 1))
  # build cumulative sum of subsequences
  y = np.cumsum(y, axis=1)
  # find ranges
  r = np.max(y, axis=1) - np.min(y, axis=1)
  # find standard deviation
  s = np.std(seqs, axis=1)
  # some ranges may be zero and have to be excluded from the analysis
  idx = np.where(r != 0)
  r = r[idx]
  s = s[idx]
  # it may happen that all ranges are zero (if all values in data are equal)
  if len(r) == 0:
    return np.nan
  else:
    # return mean of r/s along subsequence index
    return np.mean(r / s)

def binary_n(total_N, min_n=50):
  """
  Creates a list of values by successively halving the total length total_N
  until the resulting value is less than min_n.
  Non-integer results are rounded down.
  Args:
    total_N (int):
      total length
  Kwargs:
    min_n (int):
      minimal length after division
  Returns:
    list of integers:
      total_N/2, total_N/4, total_N/8, ... until total_N/2^i < min_n
  """
  #max_exp = np.log2(1.0 * total_N / min_n)
  #max_exp = int(np.floor(max_exp))
  #np.floor(1.0 * total_N / (2**i))
  s = int(total_N/2)
  return [int(i) for i in range(min_n, s)]#max_exp + 1)]


def logarithmic_n(min_n, max_n, factor):
  """
  Creates a list of values by successively multiplying a minimum value min_n by
  a factor > 1 until a maximum value max_n is reached.
  Non-integer results are rounded down.
  Args:
    min_n (float):
      minimum value (must be < max_n)
    max_n (float):
      maximum value (must be > min_n)
    factor (float):
      factor used to increase min_n (must be > 1)
  Returns:
    list of integers:
      min_n, min_n * factor, min_n * factor^2, ... min_n * factor^i < max_n
      without duplicates
  """
  assert max_n > min_n
  assert factor > 1
  # stop condition: min * f^x = max
  # => f^x = max/min
  # => x = log(max/min) / log(f)
  max_i = int(np.floor(np.log10(1.0 * max_n / min_n) / np.log10(factor)))
  ns = [min_n]
  for i in range(max_i + 1):
    n = int(np.floor(min_n * (factor ** i)))
    if n > ns[-1]:
      ns.append(n)
  return ns


def hurst_rs(data, nvals=None, fit="RANSAC", debug_plot=False,
             plot_file=None):
  """
  Calculates the Hurst exponent by a standard rescaled range (R/S) approach.
  Explanation of Hurst exponent:
    The Hurst exponent is a measure for the "long-term memory" of a
    time series, meaning the long statistical dependencies in the data that do
    not originate from cycles.
    It originates from H.E. Hursts observations of the problem of long-term
    storage in water reservoirs. If x_i is the discharge of a river in year i
    and we observe this discharge for N years, we can calculate the storage
    capacity that would be required to keep the discharge steady at its mean
    value.
    To do so, we first substract the mean over all x_i from the individual
    x_i to obtain the departures x'_i from the mean for each year i. As the
    excess or deficit in discharge always carrys over from year i to year i+1,
    we need to examine the cumulative sum of x'_i, denoted by y_i. This
    cumulative sum represents the filling of our hypothetical storage. If the
    sum is above 0, we are storing excess discharge from the river, if it is
    below zero we have compensated a deficit in discharge by releasing
    water from the storage. The range (maximum - minimum) R of y_i therefore
    represents the total capacity required for the storage.
    Hurst showed that this value follows a steady trend for varying N if it
    is normalized by the standard deviation sigma over the x_i. Namely he
    obtained the following formula:
    R/sigma = (N/2)^K
    In this equation, K is called the Hurst exponent. Its value is 0.5 for a
    purely brownian motion, but becomes greater for time series that exhibit
    a bias in one direction.
  Explanation of the algorithm:
    The rescaled range (R/S) approach is directly derived from Hurst's
    definition. The time series of length N is split into non-overlapping
    subseries of length n. Then, R and S (S = sigma) are calculated for each
    subseries and the mean is taken over all subseries yielding (R/S)_n. This
    process is repeated for several lengths n. Finally, the exponent K is
    obtained by fitting a straight line to the plot of log((R/S)_n) vs log(n).
    There seems to be no consensus how to chose the subseries lenghts n.
    This function therefore leaves the choice to the user. The module provides
    some utility functions for "typical" values:
      * binary_n: N/2, N/4, N/8, ...
      * logarithmic_n: min_n, min_n * f, min_n * f^2, ...
  References:
    .. [h-1] H. E. Hurst, “The problem of long-term storage in reservoirs,”
       International Association of Scientific Hydrology. Bulletin, vol. 1,
       no. 3, pp. 13–27, 1956.
    .. [h-2] H. E. Hurst, “A suggested statistical model of some time series
       which occur in nature,” Nature, vol. 180, p. 494, 1957.
    .. [h-3] R. Weron, “Estimating long-range dependence: finite sample
       properties and confidence intervals,” Physica A: Statistical Mechanics
       and its Applications, vol. 312, no. 1, pp. 285–299, 2002.
  Reference Code:
    .. [h-a] "hurst" function in R-package "pracma",
             url: https://cran.r-project.org/web/packages/pracma/pracma.pdf
    .. [h-b] Rafael Weron, "HURST: MATLAB function to compute the Hurst
             exponent using R/S Analysis",
             url: https://ideas.repec.org/c/wuu/hscode/m11003.html
    .. [h-c] Bill Davidson, "Hurst exponent",
             url: http://www.mathworks.com/matlabcentral/fileexchange/9842-hurst-exponent
    .. [h-d] Tomaso Aste, "Generalized Hurst exponent",
             url: http://de.mathworks.com/matlabcentral/fileexchange/30076-generalized-hurst-exponent
  Args:
    data (array of float):
      time series
  Kwargs:
    nvals (iterable of int):
      sizes of subseries to use
      (default: `logarithmic_n(4, 0.1*len(data), 1.2)`)
    fit (str):
      the fitting method to use for the line fit, either 'poly' for normal
      least squares polynomial fitting or 'RANSAC' for RANSAC-fitting which
      is more robust to outliers
    debug_plot (boolean):
      if True, a simple plot of the final line-fitting step will be shown
    plot_file (str):
      if debug_plot is True and plot_file is not None, the plot will be saved
      under the given file name instead of directly showing it through
      `plt.show()`
  Returns:
    float:
      estimated Hurst exponent K using a rescaled range approach (if K = 0.5
      there are no long-range correlations in the data, if K < 0.5 there are
      negative long-range correlations, if K > 0.5 there are positive
      long-range correlations)
  """
  total_N = len(data)
  if nvals is None:
    nvals = binary_n(total_N,10)
  # get individual values for (R/S)_n
  rsvals = np.array([rs(data, n) for n in nvals])
  # filter NaNs (zeros should not be possible, because if R is 0 then
  # S is also zero)
  rsvals = rsvals[np.logical_not(np.isnan(rsvals))]
  # it may happen that no rsvals are left (if all values of data are the same)
  if len(rsvals) == 0:
    poly = [np.nan, np.nan]
  else:
    # fit a line to the logarithm of the obtained (R/S)_n
    poly = np.polyfit(np.log10(nvals), np.log10(rsvals), 1)
    #print(poly)
   # return line slope
  return poly[0]

def test():
    gbm = (np.cumsum(randn(2000)))
    mr = (randn(2000))
    tr = (np.cumsum(randn(2000)-1)+1000)
    s = range(100)
    # Output the Hurst Exponent for each of the above series
    # and the price of Google (the Adjusted Close price) for 
    # the ADF test given above in the article
    print("Hurst(GBM):   %s" % hurst_rs(s))
    print("Hurst(MR):    %s" % hurst_rs(mr))
    print("Hurst(TR):    %s" % hurst_rs(tr))

def test2():
    flist=['600004.XSHG.csv', '600005.XSHG.csv', '600006.XSHG.csv', '600007.XSHG.csv', '600008.XSHG.csv', '600009.XSHG.csv', '600010.XSHG.csv', '600011.XSHG.csv', '600012.XSHG.csv', '600015.XSHG.csv', '600016.XSHG.csv', '600017.XSHG.csv', '600018.XSHG.csv', '600019.XSHG.csv', '600020.XSHG.csv', '600021.XSHG.csv', '600022.XSHG.csv', '600026.XSHG.csv', '600027.XSHG.csv', '600028.XSHG.csv', '600029.XSHG.csv', '600030.XSHG.csv', '600031.XSHG.csv', '600033.XSHG.csv', '600035.XSHG.csv', '600036.XSHG.csv', '600037.XSHG.csv', '600038.XSHG.csv', '600039.XSHG.csv', '600048.XSHG.csv', '600050.XSHG.csv', '600051.XSHG.csv', '600052.XSHG.csv', '600053.XSHG.csv', '600054.XSHG.csv', '600055.XSHG.csv', '600056.XSHG.csv', '600057.XSHG.csv', '600058.XSHG.csv', '600059.XSHG.csv', '600060.XSHG.csv', '600061.XSHG.csv', '600062.XSHG.csv', '600063.XSHG.csv', '600064.XSHG.csv', '600066.XSHG.csv', '600067.XSHG.csv', '600068.XSHG.csv', '600069.XSHG.csv', '600070.XSHG.csv', '600071.XSHG.csv', '600072.XSHG.csv', '600073.XSHG.csv', '600074.XSHG.csv', '600075.XSHG.csv', '600076.XSHG.csv', '600077.XSHG.csv', '600078.XSHG.csv', '600079.XSHG.csv', '600080.XSHG.csv', '600081.XSHG.csv', '600082.XSHG.csv', '600083.XSHG.csv', '600084.XSHG.csv', '600085.XSHG.csv', '600086.XSHG.csv', '600088.XSHG.csv', '600089.XSHG.csv', '600090.XSHG.csv', '600091.XSHG.csv', '600093.XSHG.csv', '600095.XSHG.csv', '600096.XSHG.csv', '600097.XSHG.csv', '600098.XSHG.csv', '600099.XSHG.csv', '600100.XSHG.csv']
    result=[]
    for f in flist:
        df = pd.read_csv("aaa/"+f)
        r = hurst_rs(df[0:1000].close.values)
        result.append(r)
    result = pd.DataFrame(result)
    result.to_csv("newtestmom/hurst.csv")
