import pandas as pd
from datetime import timedelta


def cust_t():
    df = pd.read_csv('ledger_all.csv')
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df[df.debit != 0]
    df.sort_values(['customer_name', 'date'])
    df = df.groupby(['date','customer_name'])['debit'].sum().reset_index()

    df_last = df.groupby(['customer_name'])['date'].max().reset_index()
    df['difference'] = df.groupby('customer_name')['date'].diff().dt.days.fillna(0).astype(int)
    df['difference'] = df.groupby('customer_name')['date'].diff().dt.days.fillna(0).astype(int)

    df_mean = df.groupby(['customer_name'])['difference'].mean().reset_index()
    df_mean.columns = ['customer_name', 'mean_period']


    last_sale = df.date.max()
    list_cust = df['customer_name'].unique().tolist()
    cl = len(df['customer_name'].unique())

    df_app_final = pd.DataFrame(columns = ['date', 'debit', 'difference','customer_name']) 

    i=0
    while(i<cl):

        globals()['df_cust%s' % i] = df[df['customer_name']==list_cust[i]]

        stdev = globals()['df_cust%s' % i].std(axis = 0, skipna = True)
        kp = pd.DataFrame(stdev)
        kp = kp.transpose()

        df_app = pd.DataFrame(columns = ['date', 'debit', 'difference','customer_name']) 
        df_app = df_app.append(kp)
        df_app['customer_name'] = list_cust[i]

        df_app_final = df_app_final.append(df_app)

        i = i+1



    df_app_final = df_app_final[['customer_name','difference']]
    df_app_final.rename({'customer_name': 'customer_name', 'difference': 'std'}, axis=1, inplace=True)

    i = 0
    list_cn = []
    list_prd = []

    while (i<cl):


        num = (df_mean[df_mean['customer_name']==list_cust[i]].mean_period).reset_index()
        x = num.iloc[0]['mean_period']

        if (last_sale > df[df['customer_name']==list_cust[i]].date.max() + timedelta(days = x)):
           #(‘last sale date’ - ‘last purchase date’)/(‘mean purchase period’)
            if x == 0:
                skip_prd = 'no second purchase'
                list_cn.append(list_cust[i]) 
                list_prd.append(skip_prd)

            else:            
                skip_prd = ((last_sale - df[df['customer_name']==list_cust[i]].date.max())/x).days
                list_cn.append(list_cust[i]) 
                list_prd.append(skip_prd)

        else:

            list_cn.append(list_cust[i]) 
            list_prd.append(0)

        i = i+1



    data = {'customer_name': list_cn, 
            'skipped_period': list_prd}  
    new = pd.DataFrame.from_dict(data) 


    df_final_merge = pd.merge(df_mean,df_last, how='left', left_on=["customer_name"], right_on=["customer_name"])
    df_final_merge = pd.merge(df_final_merge,new, how='left', left_on=["customer_name"], right_on=["customer_name"])
    df_final_merge = pd.merge(df_final_merge,df_app_final, how='left', left_on=["customer_name"], right_on=["customer_name"])

    df_final_merge.to_csv('customer_trajectory.csv', index = False)
    
