# https://www.quantopian.com/posts/mebane-faber-relative-strength-strategy-with-ma-rule?c=1
"""
Mebane Faber Relative Strength Strategy with MA Rule

This is a synthesis of two methods

Relative Strength Strategies for Investing
Asset Class Momentum - Rotational System
http://papers.ssrn.com/sol3/papers.cfm?abstract_id=1585517

A Quantitative Approach to Tactical Asset Allocation
Asset Class Trend Following
Mebane Faber's MA Rule
http://papers.ssrn.com/sol3/papers.cfm?abstract_id=962461

I think it's pretty common and Mebane probably has published this somewhere.

    Measure the M-month trailing returns of a basket of stocks
    Rank the stocks and buy the top-K if monthly price > 10-month SMA.
    Else, hold cash

It reduces the drawdown of the relative strength approach.
"""

# http://papers.ssrn.com/sol3/papers.cfm?abstract_id=962461
# SPY EFA AGG VNQ GLD

def initialize(context):
    context.secs = [sid(8554),sid(22972),sid(25485),sid(26669),sid(26807)]
    set_commission(commission.PerShare(cost=.005))
    leverage = 1.0
    context.top_k = 1
    context.weight = leverage/context.top_k

import numpy as np

@batch_transform(refresh_period=20, window_length=61)
def trailing_return(datapanel):
    if datapanel['price'] is None: return None
    pricedf = np.log(datapanel['price'])
    return pricedf.ix[-1]-pricedf.ix[0]

def reweight(context,data,wt,min_pct_diff=0.1):
    liquidity = context.portfolio.positions_value+context.portfolio.cash
    orders = {}
    pct_diff = 0
    for sec in wt.keys():
        target = liquidity*wt[sec]/data[sec].price
        current = context.portfolio.positions[sec].amount
        orders[sec] = target-current
        pct_diff += abs(orders[sec]*data[sec].price/liquidity)
    if pct_diff > min_pct_diff:
        #log.info(("%s ordering %d" % (sec, target-current)))
        for sec in orders.keys(): order(sec, orders[sec])

def handle_data(context, data):
    ranks = trailing_return(data)
    abs_mom = lambda x: data[x].mavg(20)-data[x].mavg(200)

    if ranks is None: return
    ranked_secs = sorted(context.secs, key=lambda x: ranks[x], reverse=True)
    top_secs = ranked_secs[0:context.top_k]
    wt = dict(((sec,context.weight if sec in top_secs and abs_mom(sec) > 0 else 0.0) for sec in context.secs))
    reweight(context,data,wt)