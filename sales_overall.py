import pandas as pd
from statsmodels.graphics.tsaplots import plot_acf,plot_pacf
import statsmodels.api as sm


def sales_all_forecast():

    print('overall forecast')
    
    df = pd.read_csv('sales_all.csv')
    df['date'] = pd.to_datetime(df['date']).dt.date
    df['sale_price'] = df['sale_price'] * df['billed_quantity']
    df = df[['date', 'sale_price', 'item_name']]
    df = df.groupby(['date','item_name'])['sale_price'].sum().reset_index()
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    df['quarters'] = df.date.dt.month
    df['year'] = pd.DatetimeIndex(df['date']).year
    df['QY']= df['year'].astype(str) + df['quarters'].astype(str)
    df.sort_values("QY", axis = 0, ascending = True, inplace = True, na_position ='last') 
    qy_val = df.QY.unique() 
    ln = len(qy_val)
    df = df.groupby(['QY'])['sale_price'].sum().reset_index() 
    df.set_index('QY',inplace=True)
    #future dates

    strl = qy_val.max()
    splitat = 4
    yr, month = strl[:splitat], strl[splitat:]

    yr = int(yr) 
    month = int(month) 


    i= month
    j = 0
    yrs = yr
    lm = []
    ly = []
    lmy = []

    while(j<12):

        i = i+1
        if i > 12:
            yrs = yr +1
            i = 1
            lm.append(str(i))
            ly.append(str(yrs))

        else:
            lm.append(str(i))
            ly.append(str(yrs))

        lmy.append(ly[j] + lm[j])
        j = j+1

    future_dates = pd.DataFrame(lmy, columns = ['QY'])
    future_dates['sale_price'] = 0
    future_dates.set_index('QY',inplace=True)
    df = df.append(future_dates)

    model=sm.tsa.statespace.SARIMAX(df['sale_price'],order=(1, 1, 1),seasonal_order=(1,1,1,12))
    results=model.fit()
    df['forecast']=results.predict(start=(ln-5),end=(ln+10),dynamic=True)
    df['QY'] = df.index
    df['forecast'] = df['forecast'].abs()
    df.to_csv('overall_sales_forecast.csv', index = False)
    