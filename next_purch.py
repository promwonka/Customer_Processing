from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import scipy as sp
from sklearn.metrics.pairwise import cosine_similarity
import operator


def nxtpurch():
    df_sales = pd.read_csv('sales_all.csv')
    df_sales['date'] = pd.to_datetime(df_sales['date']).dt.date


    df_sales = df_sales.groupby(['customer_name','item_name'])['billed_quantity'].count().reset_index()
    list_item = df_sales['item_name'].unique()
    ln = len(list_item)
    df_cust_all = pd.DataFrame(columns = ['customer_name','item_name', 'billed_quantity','affinity' ])

    i = 0

    while (i<ln):

        df_cust_item =  df_sales[df_sales['item_name'] == list_item[i]]
        df_cust_item['affinity_b'] = df_cust_item['billed_quantity']/df_cust_item['billed_quantity'].max()

        df_cust_all = df_cust_all.append(df_cust_item)

        i = i +1

    df_cust_all['affinity'] = df_cust_all['affinity_b']*10
    df_cust_all['affinity'] = df_cust_all['affinity'].round(2)

    merged_sub = df_cust_all
    list_cust = merged_sub['customer_name'].unique()
    piv = merged_sub.pivot_table(index=['customer_name'], columns=['item_name'], values='affinity')

    piv_norm = piv.apply(lambda x: (x-np.mean(x))/(np.max(x)-np.min(x)), axis=1)

    # Drop all columns containing only zeros representing users who did not rate
    piv_norm.fillna(0, inplace=True)
    piv_norm = piv_norm.T
    piv_norm = piv_norm.loc[:, (piv_norm != 0).any(axis=0)]

    piv_sparse = sp.sparse.csr_matrix(piv_norm.values)
    item_similarity = cosine_similarity(piv_sparse)
    user_similarity = cosine_similarity(piv_sparse.T)

    item_sim_df = pd.DataFrame(item_similarity, index = piv_norm.index, columns = piv_norm.index)
    user_sim_df = pd.DataFrame(user_similarity, index = piv_norm.columns, columns = piv_norm.columns)


    def top_items(anime_name):
        count = 1
        lp = []
        lpa = []

        for item in item_sim_df.sort_values(by = anime_name, ascending = False).index[1:5]:


            lp = ('{}:{}'.format(count, item))
            lp = lp.split(":",1)[1]
            lpa.append(lp)
            count +=1  

        return lpa


    def top_users(user):

        if user not in piv_norm.columns:
            return('No data available on user {}'.format(user))

        print('Most Similar Users:\n')
        sim_values = user_sim_df.sort_values(by=user, ascending=False).loc[:,user].tolist()[1:11]
        sim_users = user_sim_df.sort_values(by=user, ascending=False).index[1:11]
        zipped = zip(sim_users, sim_values,)
        for user, sim in zipped:
            print('User #{0}, Similarity value: {1:.2f}'.format(user, sim)) 


    def similar_user_recs(user):

        if user not in piv_norm.columns:
            return('No data available on user {}'.format(user))

        sim_users = user_sim_df.sort_values(by=user, ascending=False).index[1:11]
        best = []
        most_common = {}

        for i in sim_users:
            max_score = piv_norm.loc[:, i].max()
            best.append(piv_norm[piv_norm.loc[:, i]==max_score].index.tolist())
        for i in range(len(best)):
            for j in best[i]:
                if j in most_common:
                    most_common[j] += 1
                else:
                    most_common[j] = 1
        sorted_list = sorted(most_common.items(), key=operator.itemgetter(1), reverse=True)
        return sorted_list[:30]  


    def predicted_rating(anime_name, user):
        sim_users = user_sim_df.sort_values(by=user, ascending=False).index[1:1000]
        user_values = user_sim_df.sort_values(by=user, ascending=False).loc[:,user].tolist()[1:1000]
        rating_list = []
        weight_list = []
        for j, i in enumerate(sim_users):
            rating = piv.loc[i, anime_name]
            similarity = user_values[j]
            if np.isnan(rating):
                continue
            elif not np.isnan(rating):
                rating_list.append(rating*similarity)
                weight_list.append(similarity)
        return sum(rating_list)/sum(weight_list)  



    list_all = []
    list_upsell_all = []
    i = 0
    while i< len(list_cust):

        list_rec = similar_user_recs(list_cust[i])

        try : 
            list_upsell = top_items(list_rec[0][0])
        except :
            list_upsell = ['None']

        list_upsell_all.append(list_upsell)
        list_all.append(list_rec)
        i = i +1



    dicts = {}
    keys = list_cust
    i = 0
    while i < len(list_cust):
        dicts[list_cust[i]] = list_all[i]
        i = i +1    


    df_next_purch = pd.DataFrame(list(dicts.items()),columns = ['customer_name','next_purchase_items']) 
    df_next_purch['upsell_cross'] =  list_upsell_all
    df_next_purch.to_csv('next_purchase_items.csv')
    
