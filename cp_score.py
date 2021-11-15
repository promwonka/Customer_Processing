from datetime import datetime, timedelta
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler

    
def cp_run():
    
    def date_finder(i,j):
        cp = (df_pay.iloc[i,0] - df_purch.iloc[j,0]).days
        list_cp = []
        list_cp.append(df_purch.iloc[j,4])
        list_cp.append(df_purch.iloc[j,2])
        list_cp.append(cp)
        list_cs.append(list_cp)
        

    def pay_loc(i,j): # accepts index of cum_credit & cum_debit || outputs 1 if cum_credit > cum_debit, else 0
        if (df_pay.iloc[i,5] >= df_purch.iloc[j,5]): # if cum_credit is greater than cum_debit
            return(0)
        elif (df_pay.iloc[i,5] < df_purch.iloc[j,5]):
            return(1)
    
    df = pd.read_csv('ledger_all.csv')
    list_cust = df['customer_name'].unique().tolist()
    icn = 0
    cn = len(list_cust)
    on =0
    df_all_purch = pd.DataFrame()
    df_all_pay = pd.DataFrame()
    cp_dict = {}
    cs_dict = {}
    list_cs = []

    while (icn < cn):

        i = 0
        j = 0
        i_c = 0
        i_d = 0
        k = 0
        l = 0
        q = 0
        jk = 0
        jkn = 0


        df_c = df[df['customer_name'] == list_cust[icn]]
        df_pay = df_c[df_c['debit'] == 0]
        df_pay = df_pay[df_pay['credit'] != 0]
        df_pay['date'] = pd.to_datetime(df_pay['date'], errors='coerce')
        df_pay['CUMSUM'] = df_pay['credit'].cumsum()



        df_purch = df_c[df_c['credit'] == 0]
        df_purch = df_purch[df_purch['debit'] != 0]
        df_purch['date'] = pd.to_datetime(df_purch['date'], errors='coerce')
        df_purch['purchase'] = df_purch['debit'].cumsum()

        df_pay.sort_values(by=['date'], ascending=False).inplace = True
        df_purch.sort_values(by=['date'], ascending=False).inplace = True


        if (len(df_pay['CUMSUM']) != 0 and len(df_purch['purchase']) != 0 ):

            def on_fn():
                if df_purch['purchase'].max() > df_pay['CUMSUM'].max():
                    on = 0
                elif df_purch['purchase'].max() < df_pay['CUMSUM'].max():
                    on = 1
                elif df_purch['purchase'].max() == df_pay['CUMSUM'].max():
                    on = 2
                elif len(df_pay['CUMSUM']) == 0:
                    on = 3

                return on



            def jkn_fn():
                oni = on_fn()
                if oni == 0:
                    df_diff = (df_purch[df_purch['purchase'] > (df_pay['CUMSUM'].max())])
                    jkn = len(df_diff['sales'])

                elif oni == 1:
                    df_diff = (df_pay[df_pay['CUMSUM'] > (df_purch['purchase'].max())])
                    jkn = len(df_diff['sales'])

                elif oni == 2:
                    if (abs(len(df_pay['sales']) - len(df_purch['sales'])) == 0) :
                        jkn = 1
                    else:
                        jkn = abs(len(df_pay['sales']) - len(df_purch['sales']))
                elif oni == 3:
                    jkn = 0

                return jkn


            if (on_fn() != 1):

                jk = ((len(df_purch) + len(df_pay)) - jkn_fn())
                cp = df_pay.iloc[i,0]


                while(l<jk):

                    if pay_loc(k,q) == 0:

                        date_finder(k,q)
                        i_c = i_c
                        i_d = i_d+1

                    else:

                        i_c = i_c+1
                        i_d = i_d

                    k = i_c
                    q = i_d
                    l+=1



            else:
                pass



        else:
            pass

        icn = icn + 1


    df_credit_score = pd.DataFrame(list_cs, columns = ['customer_name' , 'debit', 'credit_period'])

    df_credit1 = df_credit_score.groupby(['customer_name'])['debit'].sum().reset_index()
    df_credit2 = df_credit_score.groupby(['customer_name'])['credit_period'].mean().reset_index()
    df_credit_rank = pd.merge(df_credit2, df_credit1, on='customer_name')

    # scaler = MinMaxScaler()

    # def order_cluster(cluster_field_name, target_field_name,df_,ascending):
    #     new_cluster_field_name = 'new_' + cluster_field_name
    #     df_new = df_.groupby(cluster_field_name)[target_field_name].mean().reset_index()
    #     df_new = df_new.sort_values(by=target_field_name,ascending=ascending).reset_index(drop=True)
    #     df_new['index'] = df_new.index
    #     df_final = pd.merge(df_,df_new[[cluster_field_name,'index']], on=cluster_field_name)
    #     df_final = df_final.drop([cluster_field_name],axis=1)
    #     df_final = df_final.rename(columns={"index":cluster_field_name})
    #     return df_final


    # kmeans = KMeans(n_clusters = 7)

    # kmeans.fit(df_credit_rank[['debit']])
    # df_credit_rank['debit_cluster'] = kmeans.predict(df_credit_rank[['debit']])
    # df_credit_rank = order_cluster('debit_cluster', 'debit',df_credit_rank,False)

    # kmeans.fit(df_credit_rank[['credit_period']])
    # df_credit_rank['period_cluster'] = kmeans.predict(df_credit_rank[['credit_period']])
    # df_credit_rank = order_cluster('period_cluster', 'credit_period',df_credit_rank,False)

    # dictm = {0:6, 1:5, 2:4, 3:3, 4:2, 5:1, 6:0} 
    # df_credit_rank = df_credit_rank.replace({"debit_cluster": dictm}) 

    df_credit_rank['debit_percentile'] = df_credit_rank.debit.rank(pct = True) 
    df_credit_rank['debit_percentile'] = df_credit_rank['debit_percentile']*100
    df_credit_rank['cp_percentile'] = df_credit_rank.credit_period.rank(pct = True) 
    df_credit_rank['cp_percentile'] = df_credit_rank['cp_percentile']*100
    df_credit_rank['cp_percentile'] = 100 - df_credit_rank['cp_percentile']

    df_credit_rank['credit_worthiness'] = 0.5*(df_credit_rank.debit_percentile + df_credit_rank.cp_percentile)

    df_sales = pd.read_csv('sales_all.csv')
    df_sales['date'] = pd.to_datetime(df_sales['date']).dt.date
    df_sales['profit'] = df_sales['billed_quantity']*(df_sales['sale_price'] - df_sales['cost_price'])
    df_sales = df_sales.groupby(['customer_name'])['profit'].sum().reset_index()

    df_credit_score['interest'] = df_credit_score['debit']*((0.12*df_credit_score['credit_period'])/365)
    df_debit1 = df_credit_score.groupby(['customer_name'])['interest'].sum().reset_index()

    df_final_merge = pd.merge(df_debit1,df_sales, how='left', left_on=["customer_name"], right_on=["customer_name"])

    df_final_merge['actual_profit'] = df_final_merge['profit'] - df_final_merge['interest']
    df_final_merge = df_final_merge.dropna()

    # kmeans.fit(df_final_merge[['actual_profit']])
    # df_final_merge['profit_cluster'] = kmeans.predict(df_final_merge[['actual_profit']])
    # df_final_merge = order_cluster('profit_cluster', 'actual_profit',df_final_merge,False)

    # df_final_merge = df_final_merge.replace({"profit_cluster": dictm}) 

    df_final_merge = pd.merge(df_credit_rank, df_final_merge, on='customer_name')

    df_final_merge = df_final_merge.dropna()
    df_final_merge['profit_percentile'] = df_final_merge.actual_profit.rank(pct = True) 
    df_final_merge['profit_percentile'] = df_final_merge['profit_percentile']*100
    df_final_merge['profit_ratio'] = (df_final_merge['actual_profit']/df_final_merge['debit'])*100
    df_final_merge['profit_ratio_percentile'] = df_final_merge.profit_ratio.rank(pct = True) 
    df_final_merge['profit_ratio_percentile'] = df_final_merge['profit_ratio_percentile']*100

    df_final_merge.to_csv('customer_scores.csv', index = False)
    
