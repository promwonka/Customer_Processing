import pandas as pd
from cp_score import cp_run
from cash_flow import cash_flow_fn
from next_purch import nxtpurch
from customer_traj import cust_t
from sales_overall import sales_all_forecast

import sys
 

def main_fn():
    
    
    cash_flow_fn()
    
    cp_run()
    
    nxtpurch()
    
    cust_t()
    
    sales_all_forecast()
    
    
    df_cscore = pd.read_csv('customer_scores.csv')
    df_ctraj = pd.read_csv('customer_trajectory.csv')
    df_csq = pd.merge(df_cscore, df_ctraj, on='customer_name')
    df_csq = df_csq.round(0)
    df_csq['overall_score'] = 0.5*(df_csq['profit_percentile'] + df_csq['credit_worthiness'])
    df_csq['segment'] = 'Bad Customers'
    df_csq.loc[df_csq['overall_score']>40,'segment'] = 'Average Customers' 
    df_csq.loc[df_csq['overall_score']>80,'segment'] = 'Good Customers' 


    df = df_csq
    df['credit_period']= abs(df['credit_period'])
    df['cp_percentile'] = df.credit_period.rank(pct = True) 
    df['cp_percentile'] = df['cp_percentile']*100
    df['cp_percentile'] = 100 - df['cp_percentile']
    df['credit_worthiness'] = 0.5*(df.debit_percentile + df.cp_percentile)
    df['overall_score'] = 0.5*(df['profit_percentile'] + df['credit_worthiness'])
    df['segment'] = 'Bad Customers'
    df.loc[df['overall_score']>40,'segment'] = 'Average Customers' 
    df.loc[df['overall_score']>80,'segment'] = 'Good Customers' 

    df1 = pd.read_csv('sales_all.csv')
    df1['sale_price'] = df1['sale_price']*df1['billed_quantity']
    df1 = df1.groupby(['customer_name'])['sale_price'].sum().reset_index()
    df1['debit2'] = df1['sale_price']
    df_f = pd.merge(df,df1, on = 'customer_name')
    df_f['profit_ratio'] = (df_f['actual_profit']/df_f['debit2'])*100
    df_f['profit_ratio_percentile'] = df_f.profit_ratio.rank(pct = True) 
    df_f['profit_ratio_percentile'] = df_f['profit_ratio_percentile']*100
    df_f = df_f.round(0)
    dfc = pd.read_csv('contact_list.csv')
    df_final_merge = pd.merge(df_f,dfc, how='left', left_on=["customer_name"], right_on=["customer_name"])  
    
    df_final_merge.to_csv('customer_final_scores.csv',index = False)

    df0 = df_f
    df1 = df0[df0['skipped_period']!= 'no second purchase']
    df1['skipped_period'] = df1['skipped_period'].astype(int)
    df_sk = df1[df1['skipped_period']< 5]
    sk_list  = df_sk['customer_name'].unique()
    df2 = df0[['customer_name', 'segment']]
    
    df_fore = pd.read_csv('cash_forecast.csv')
    df_fore = pd.merge(df_fore, df2, on='customer_name')
    df_fore1 = df_fore[df_fore['customer_name'].isin(sk_list)]
    df_fore2 = df_fore[~df_fore['customer_name'].isin(sk_list)]
    df_fore2['forecast'] = 0
    df_res = df_fore1.append(df_fore2)
    df_res['forecast'] = df_res['forecast'].abs()
    df_res.to_csv('forecast_seg.csv',index = False)
    
    
    
 
main_fn() 
