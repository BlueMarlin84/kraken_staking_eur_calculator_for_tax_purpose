# -*- coding: utf-8 -*-
"""
@author: giancarlo.pagliaroli
"""
import pandas as pd
from pandas_datareader import data, wb
import yfinance as yf
import datetime
import numpy as np

#dataframe from nexo
df = pd.read_csv('ledgers_KRAKEN.csv', sep=',')
df = df[df['type']=='staking']
df[['Date','Time']] = df['time'].str.split(' ',expand=True)
df = df[['Date', 'type', 'asset', 'amount']]
df['asset'] = df['asset'].str.replace('XTZ','XTZ-EUR')
df['asset'] = df['asset'].str.replace('.S','')

currency_list = df['asset'].unique()
df['eur'] = np.NaN
df['tot'] = np.NaN
df.sort_values('Date', inplace=True)

#fiscal period of interest
start = datetime.datetime(2020, 1,1)
end= datetime.datetime(2020, 12,31)
print(currency_list)

#first loop on my cripto list getting yahoo prices
for i in currency_list:
    dfy= data.get_data_yahoo(i, start, end)   
    dfy['Data'] = dfy.index.map(str)
    dfy[['Data','Time']] = dfy['Data'].str.split(' ',expand=True)
       
    for index, data1,currency in zip(df.index, df['Date'],df['asset']):
        
        for data2,close in zip(dfy['Data'],dfy['Close']):
                       
            if (data1==data2) and (currency == i):
                df.loc[index, 'eur']=close
                df.loc[index, 'tot']=df.loc[index,'amount']*close
            else:
                #do nothing for now if yahoo is not getting price e.g on Sunday but nexo gives iterest everyday. It will be solved at step x
                continue
            
values = []
dictionary = dict(zip(currency_list, values))            

for index, x,y in zip(df.index, df['asset'],df['eur']):
    if np.isnan(y):
        
        df.loc[index, 'eur'] = dictionary[x]
        df.loc[index, 'tot'] = df.loc[index, 'eur'] * df.loc[index, 'amount']
    else:
        #step x: get the price from the last available yahoo price
        dictionary[x] = y
                
print(df)
totale = round(df['tot'].sum(),0)
print('totale interessi in euro (staking) da dichiarare nel quadro RL del Modello PF: ' + str(totale))
df.to_excel('staking.xlsx')  

