import pandas as pd
import numpy as np
import quandl
import pytz
from datetime import datetime
#import matplotlib.pyplot as plt
import statsmodels
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint
import itertools

def name_to_ticker(name, dict):
    return dict.get(name, "not found")
def zscore(series):
    return (series - series.mean()) / np.std(series)

def backtest_pair(pair, df,risk):
    X = pair[0]
    Y = pair[1]
    capital = 10000
    half = capital / 2;
    trades = []
    profit_loss = []
    enter_trade = []
    exit_trade = []
    position_size = []
    go_long = " "
    openposition = False
    ctr_enter = 1
    ctr_exit = 1
    enter_zscore = float(risk[0])
    exit_zscore = float(risk[1])
    #print("\nBACKTEST RESULTS - \n")
    for i in range(len(df)):
        date = df.index[i]
        cur_z_score = df['ZScore'].iloc[i]
        cur_z_score = round(cur_z_score,2)
        if ((openposition == False) and (abs(cur_z_score)) > enter_zscore):
            if (cur_z_score < 0):
                go_long = "Y"
            else:
                go_long = "X"
            X_price = df[X].iloc[i]
            Y_price = df[Y].iloc[i]
            num_of_stocks_X = (half - (half % X_price)) / X_price
            remaining_capital = capital - (num_of_stocks_X * X_price)
            num_of_stocks_Y = (remaining_capital - (remaining_capital % Y_price)) / Y_price

            if (go_long == "Y"):
                short_position = X_price * num_of_stocks_X
                long_position = Y_price * num_of_stocks_Y
                enter_trade.append(date)
                position_size.append(short_position + long_position)
                log = "%s)  ENTER TRADE ON %s:\n      SHORT %i stocks of %s @ %s\n      LONG %i stocks of %s @ %s\n      Z-Score = %s\n" % (
                ctr_enter, date, num_of_stocks_X, X, X_price, num_of_stocks_Y, Y, Y_price, cur_z_score)
                trades.append(log)
                openposition = True
                ctr_enter += 1
            if (go_long == "X"):
                long_position = X_price * num_of_stocks_X
                short_position = Y_price * num_of_stocks_Y
                enter_trade.append(date)
                position_size.append(short_position + long_position)
                log = "%s)  ENTER TRADE ON %s:\n      LONG %i stocks of %s @ %s\n      SHORT %i stocks of %s @ %s\n      Z-Score = %s\n" % (
                ctr_enter, date, num_of_stocks_X, X, X_price, num_of_stocks_Y, Y, Y_price, cur_z_score)
                trades.append(log)
                openposition = True
                ctr_enter += 1

        if (openposition == True):
            if (abs(cur_z_score)) < exit_zscore:
                X_price = df[X].iloc[i]
                Y_price = df[Y].iloc[i]
                if (go_long == "Y"):
                    short_pl = short_position - (X_price * num_of_stocks_X)
                    long_pl = (Y_price * num_of_stocks_Y) - long_position
                    total_pl = short_pl + long_pl
                    log = "%s)  EXIT TRADE ON %s:\n      %s SHORT @ %s\n      %s LONG @ %s\n      Total P/L = %s\n      Z-Score = %s\n" % (
                    ctr_exit, date, X, X_price, Y, Y_price, total_pl, cur_z_score)
                    trades.append(log)
                    capital += total_pl
                    exit_trade.append(date)
                    profit_loss.append(total_pl)
                    openposition = False
                    ctr_exit += 1
                if (go_long == "X"):
                    short_pl = short_position - (Y_price * num_of_stocks_Y)
                    long_pl = (X_price * num_of_stocks_X) - long_position
                    total_pl = short_pl + long_pl
                    log = "%s)  EXIT TRADE ON %s:\n      %s LONG @ %s\n      %s SHORT @ %s\n      Total P/L = %s\n      Z-Score = %s\n" % (
                    ctr_exit, date, X, X_price, Y, Y_price, total_pl, cur_z_score)
                    trades.append(log)
                    capital += total_pl
                    exit_trade.append(date)
                    profit_loss.append(total_pl)
                    openposition = False
                    ctr_exit += 1

    if (openposition == True):
        X_price = df[X].iloc[len(df) - 1]
        Y_price = df[Y].iloc[len(df) - 1]
        date = df.index[(len(df) - 1)]
        cur_z_score = df['ZScore'].iloc[len(df) - 1]
        if (go_long == "Y"):
            short_pl = short_position - (X_price * num_of_stocks_X)
            long_pl = (Y_price * num_of_stocks_Y) - long_position
            total_pl = short_pl + long_pl
            log = "%s)  EXIT TRADE ON %s:\n      %s SHORT @ %s\n      %s LONG @ %s\n      Total P/L = %s\n      Z-Score = %s\n" % (
            ctr_exit, date, X, X_price, Y, Y_price, total_pl, cur_z_score)
            trades.append(log)
            capital += total_pl
            exit_trade.append(date)
            profit_loss.append(total_pl)
            openposition = False
        if (go_long == "X"):
            short_pl = short_position - (Y_price * num_of_stocks_Y)
            long_pl = (X_price * num_of_stocks_X) - long_position
            total_pl = short_pl + long_pl
            log = "%s)  EXIT TRADE ON %s:\n      %s LONG @ %s\n      %s SHORT @ %s\n      Total P/L = %s\n      Z-Score = %s\n" % (
            ctr_exit, date, X, X_price, Y, Y_price, total_pl, cur_z_score)
            trades.append(log)
            capital += total_pl
            exit_trade.append(date)
            profit_loss.append(total_pl)
            openposition = False

    total_profit_loss = round(sum(profit_loss),2)
    capital=round(capital,2)

    returns = round((total_profit_loss/100),2)

    log = "Total P/L = %s" % (total_profit_loss)
    trades.append(log)
    log = "Final Portfolio Value = %s" % (capital)
    trades.append(log)
    log = "Total Returns = %s%%" % (returns)
    trades.append(log)
    log = "Level Of Risk = %s" % (risk[2])
    trades.append(log)

    return trades

"""def plot_pair(S1, S2):
plt.subplot(211)
plt.plot(S1, color='red')
plt.plot(S2, color='blue')
plt.legend([best_pair[0], best_pair[1]])
plt.subplot(212)
zscore(spread).plot()
plt.axhline(zscore(spread).mean(), color='black')
plt.axhline(1.0, color='red', linestyle='--')
plt.axhline(-1.0, color='green', linestyle='--')
plt.legend(['Z-Score', 'Mean', '+1', '-1']);
plt.show()"""



#if __name__=='__main__':

def getpairs(start,end):

    quandl.ApiConfig.api_key = 'NnpyEUkNcmVdsAR9Y56A'

    bank_nifty = ['NSE/HDFCBANK.5', 'NSE/ICICIBANK.5', 'NSE/AXISBANK.5', 'NSE/KOTAKBANK.5', 'NSE/SBIN.5',
    'NSE/INDUSINDBK.5', 'NSE/YESBANK.5', 'NSE/BANKBARODA.5', 'NSE/FEDERALBNK.5', 'NSE/PNB.5', 'NSE/CANBK.5']
    mydata = quandl.get(bank_nifty, start_date=start, end_date=end,authtoken = quandl.ApiConfig.api_key)
    col_names = ['HDFC', 'ICICI', 'AXISBANK', 'KOTAK', 'SBIN', 'INDUSIND', 'YESBANK', 'BANKOFBARODA', 'FEDERALBANK',
    'PNB', 'CANARABANK']
    mydata.columns = col_names
    allpairs = itertools.combinations(col_names, 2)
    pairs = []
    for pair in allpairs:
        pairs.append(pair)
    pvalues = []
    for pair in pairs:
        X = pd.Series(mydata[pair[0]])
        Y = pd.Series(mydata[pair[1]])
        score, pvalue, _ = coint(X, Y)
        pvalues.append(pvalue)

    coint_table = pd.DataFrame({'Pair': pairs, 'P-Value': pvalues})
    coint_table.sort_values(by=['P-Value'], axis=0, ascending=True, inplace=True)
    #print(coint_table)
    best_pairs = [coint_table['Pair'].iloc[0],coint_table['Pair'].iloc[1],coint_table['Pair'].iloc[2]]
    return best_pairs
    #return ("\nHighest Co-Integrated Pair Is - " + best_pair[0] + " and " + best_pair[1])

def profits(pair,start,end,risk):
    #print("\nP-Value Is - ", coint_table['P-Value'].iloc[0])
    #X = pd.Series(mydata[best_pair[0]])
    #Y = pd.Series(mydata[best_pair[1]])

    bank_nifty = ['NSE/HDFCBANK.5', 'NSE/ICICIBANK.5', 'NSE/AXISBANK.5', 'NSE/KOTAKBANK.5', 'NSE/SBIN.5',
    'NSE/INDUSINDBK.5', 'NSE/YESBANK.5', 'NSE/BANKBARODA.5', 'NSE/FEDERALBNK.5', 'NSE/PNB.5',
    'NSE/CANBK.5']
    col_names = ['HDFC', 'ICICI', 'AXISBANK', 'KOTAK', 'SBIN', 'INDUSIND', 'YESBANK', 'BANKOFBARODA', 'FEDERALBANK',
    'PNB', 'CANARABANK']
    switcher = dict(zip(col_names, bank_nifty))

    quandl.ApiConfig.api_key = 'NnpyEUkNcmVdsAR9Y56A'
    stock1 = name_to_ticker(pair[0], switcher)
    stock2 = name_to_ticker(pair[1], switcher)
    btstocks = [stock1, stock2]

# plot_pair(X,Y)

    backtest_data = quandl.get(btstocks, start_date=start, end_date=end,authtoken = quandl.ApiConfig.api_key)
    backtest_data.columns = [pair[0], pair[1]]
    S1 = pd.Series(backtest_data[pair[0]])
    S2 = pd.Series(backtest_data[pair[1]])
    S1 = sm.add_constant(S1)
    results = sm.OLS(S2, S1).fit()

    S1 = S1[pair[0]]
    b = results.params[pair[0]]

    spread = S2 - b * S1
    #print(spread)

    backtest_data = backtest_data.assign(ZScore=zscore(spread).values)
    #print(backtest_data)
    trades = backtest_pair(pair, backtest_data,risk)

    return trades
