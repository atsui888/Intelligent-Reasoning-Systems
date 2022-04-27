# Software Developer: Richard Chai: https://www.linkedin.com/in/richardchai/

#!/usr/bin/env python
# coding: utf-8

# # 00 Combined RE and ARIMA Server_tA

# In[ ]:


# !pip install yfinance
# !pip install anvil-uplink


# In[ ]:


import pandas as pd
import statsmodels.api as sm
import yfinance as yf
from datetime import datetime
from dateutil.relativedelta import relativedelta
from zCreds import creds
import anvil.server
anvil.server.connect(creds['anvil'])
import numpy as np
from Collaborative_Filtering import Euclidian_Similarity, Recommendations
from pandas.tseries.offsets import BDay


# # Global Vars

# In[ ]:


df_funds        = pd.DataFrame()
df_user_data    = pd.DataFrame()
df_user_profile = pd.DataFrame()
df_item_profile = pd.DataFrame()
user_eu_sim_df  = pd.DataFrame()
item_eu_sim_df  = pd.DataFrame()
user_is_new = False


# # Functions

# ##### Recommendation Engine

# In[ ]:


def load_lu_funds():
    global df_funds
    df_funds = pd.read_csv('data/lu_funds.csv')
    df_funds.set_index('fund_id', inplace=True)    


# In[ ]:


def load_user_data():
    global df_user_data
    df_user_data = pd.read_csv('data/user_data.csv')    


# In[ ]:


def prep_existing_user_profiles():
    global df_user_data
    global df_user_profile
    df_user_profile = df_user_data[['user_id','risk_appetite','investment_objective',
                                'equities_alloc','bonds_alloc']].copy()
    df_user_profile.set_index('user_id', inplace=True)    


# In[ ]:


# perform feature scaling
def numeric_df_min_max_scaling(df):
    df = df.copy()
    cols = df.columns.to_list()
    for col in cols:
        col_min = df[col].min()
        col_max = df[col].max()
        df[col] = (df[col]-col_min)/(col_max-col_min)
    return df


# In[ ]:


def calc_user_based_eu_sim():
    global user_eu_sim_df
    user_eu_sim = Euclidian_Similarity(df_user_profile, verbose=0)
    user_eu_sim_df = user_eu_sim.get_sim_scores_df()  # get the similarity scores matrix


# In[ ]:


def calc_df_item_profile():    
    global df_user_data
    global df_item_profile
    
    # create df_Item_profile, this is also used in 'item-based' collaborative filtering
    zz = df_user_data[['fund_id' ,'user_id','user_satisfaction']].copy()
    zz.set_index('user_id',inplace=True)

    col_lbls = zz.fund_id.unique()
    col_lbls= col_lbls[~pd.isnull(col_lbls)]

    index_lbls = sorted(zz.index.to_list())

    df_item_profile = pd.DataFrame(index=index_lbls, columns=col_lbls)

    for uid,row in zz.iterrows():            
        fid = zz.loc[uid,'fund_id']
        if pd.isnull(fid):
            continue
        cust_sat = zz.loc[uid,'user_satisfaction']    
        df_item_profile.loc[uid,fid] = cust_sat   


# In[ ]:


def calc_item_based_eu_sim():
    global item_eu_sim_df    
    item_eu_sim = Euclidian_Similarity(df_item_profile.T, verbose=0)  # note the transpose ('items' in rows,'users' in cols)
    item_eu_sim_df = item_eu_sim.get_sim_scores_df()  # get the similarity scores matrix


# In[ ]:


@anvil.server.callable
def add_new_user_to_user_profiles(data):
    """
    input: 
    data = {
        'user_id': ['uid_101'],
        'risk_appetite': [1],
        'investment_objective':  [1],
        'equities_alloc':  [50],
        'bonds_alloc': [50]
    }
    """
    global df_user_data
    global df_user_profile
    
    new_user_df = pd.DataFrame(data)
    new_user_df.set_index('user_id',inplace=True)
    
    # insert the user details into df_user_profile as new or replace if exists
    try:
        # df_user_profile is a temp df used for calculating similarity
        df_user_profile.loc[new_user_df.index[0],'risk_appetite'] = new_user_df['risk_appetite'][0]    
        df_user_profile.loc[new_user_df.index[0],'investment_objective'] = new_user_df['investment_objective'][0]    
        df_user_profile.loc[new_user_df.index[0],'equities_alloc'] = new_user_df['equities_alloc'][0]    
        df_user_profile.loc[new_user_df.index[0],'bonds_alloc'] = new_user_df['bonds_alloc'][0]  

        # df_user_data is permanent storage for users' data
        df_user_data.set_index('user_id',inplace=True)
        df_user_data.loc[new_user_df.index[0],'risk_appetite'] = new_user_df['risk_appetite'][0]    
        df_user_data.loc[new_user_df.index[0],'investment_objective'] = new_user_df['investment_objective'][0]    
        df_user_data.loc[new_user_df.index[0],'equities_alloc'] = new_user_df['equities_alloc'][0]    
        df_user_data.loc[new_user_df.index[0],'bonds_alloc'] = new_user_df['bonds_alloc'][0]  
        df_user_data.reset_index(inplace=True)

    except KeyError:        
        # # df_user_profile is a temp df used for calculating similarity        
        # key does not exist, so we append the new user_id
        df_user_profile = df_user_profile.append(new_user_df, ignore_index = False)   
        
        # df_user_data is permanent storage for users' data
        df_user_data.set_index('user_id',inplace=True)
        df_user_data = df_user_data.append(new_user_df, ignore_index = False)
        df_user_data.reset_index(inplace=True)
        

    except Exception as e:
        print(e)

    # min_max scale
    # scale data
    df_user_profile = numeric_df_min_max_scaling(df_user_profile)   
    
    # unless we load the stored user_based_eu_sim from disk, we always have to calculate
    # regardless of new or existing user_id (for future optimisation)
    calc_user_based_eu_sim()
        
    calc_df_item_profile()  # uid_101 needs this
    
    
    # print(new_user_df.index[0]) # display uid
    rec_dict = given_user_recommend_item(new_user_df.index[0])
    
    return rec_dict
    
# return user_eu_sim_df.iloc[0,10]
# return new_user_df.reset_index(inplace=False).to_dict(orient='records')
# return df_user_profile.reset_index(inplace=False).to_dict(orient='records')


# In[ ]:


@anvil.server.callable
def given_user_recommend_item(uid):
    """
    uid must already have been added via add_new_user_to_user_profiles()
    
    """
    user_id = uid
    rec = Recommendations(user_id, df_item_profile, user_eu_sim_df, verbose=0)

    threshold = 3
    top_k=3
    df_rec, rec_lst = rec.get_recommendations(threshold=threshold, top_k=top_k)
    
    investment_returns_lst = []
    for fund_id in rec_lst:
        #investment_returns_lst.append(df_user_data[df_user_data.fund_id == fund_id].investment_return.mean().round(2))
        investment_returns_lst.append(df_user_data[df_user_data.fund_id == fund_id].investment_return.mean())

    data = {'fund_id': rec_lst,'investment_returns': investment_returns_lst}    
    df_iReturns = pd.DataFrame(data)
    df_iReturns.set_index('fund_id', inplace=True)
    df_recs_to_return = pd.DataFrame()
    df_recs_to_return = pd.concat([df_funds.loc[rec_lst,['fund_chosen']], df_rec['recommendation_score']],axis=1)
    df_recs_to_return = pd.concat([df_recs_to_return,df_iReturns[['investment_returns']]],axis=1) 

    # display(df_recs_to_return)
    return df_recs_to_return.reset_index(inplace=False).to_dict(orient='records')


# In[ ]:


@anvil.server.callable
def given_item_recommend_item(fid='fid_1'):
    """
    uid: string, user id
        uid must already have been added via add_new_user_to_user_profiles()
        we use the default first uid as the 'ficticious user'
    fid: string fund id
         default: 'fid_1'
         we need this because this is what the user selected in the App UI
    
    """
    # coz this is item-based, it doesn't matter which user_id it is, we just need to mark one uid
    # so that the algorithm can return recommendations for a ficticious uid
    # the recs are not stored. For future, if item-based similarities are scored, it is calculated
    # from the actual user ratings, not from here.
    user_id = 'uid_1'     
    user_id_profile = df_item_profile.loc[[user_id],:].copy()
    user_id_profile.loc[user_id, fid] = 2.5  # this is the fid user has select to display in the UI
    # nb: it is NOT a rating, it's just selected, hence 2.5 is the mid-point from rating 1 to 5    
    
    rec = Recommendations(user_id, user_id_profile, item_eu_sim_df, cf_type='item', verbose=0)
    
    threshold = 3
    top_k=1    
    df_rec, rec_lst = rec.get_recommendations(threshold=0, top_k=top_k)
    
    investment_returns_lst = []
    for fund_id in rec_lst:
        investment_returns_lst.append(df_user_data[df_user_data.fund_id == fund_id].investment_return.mean())

    data = {'fund_id': rec_lst,'investment_returns': investment_returns_lst}    
    df_iReturns = pd.DataFrame(data)
    df_iReturns.set_index('fund_id', inplace=True)
    df_recs_to_return = pd.DataFrame()
    df_recs_to_return = pd.concat([df_funds.loc[rec_lst,['fund_chosen']], df_rec['recommendation_score']],axis=1)
    df_recs_to_return = pd.concat([df_recs_to_return,df_iReturns[['investment_returns']]],axis=1) 

    # display(df_recs_to_return)
    return df_recs_to_return.reset_index(inplace=False).to_dict(orient='records')


# ##### ARIMA

# In[ ]:


def load_ticker(ticker, start_date, end_date, train_size=0.8):    
    
    # df = yf.download(ticker, start=start_date, end=end_date, group_by="ticker")
    
    # https://stackoverflow.com/questions/67291926/remove-comment-from-yfinance
    # stop progress bar
    df = yf.download(ticker, start=start_date, end=end_date, group_by="ticker",progress=False)
    
    df = df.asfreq('b')  # set frequency 'b' business day - Mon to Fri
    
    if df.isnull().sum().sum()>0:
        df=df.fillna(method='ffill')
    

    # train_set_size = int(df.shape[0] * train_size) # if want train split
    train_set_size = df.shape[0]  # take all rows, NO, train test split
    X_train, X_test = df.iloc[:train_set_size], df.iloc[train_set_size:] 
    return X_train, X_test


# In[ ]:


def train_arima_model(train_set, verbose=0):
    model = sm.tsa.arima.ARIMA(train_set, order=(2,2,2))
    results_model = model.fit()
    if verbose>0:        
        print(results_model.summary())
    return results_model


# In[ ]:


def arima_predict(trained_model, start_date, forecast_date, verbose=0):
    # nb: model must be fitted first before calling .predict()
    forecast = trained_model.predict(start=start_date, end=forecast_date)  # returns a pandas series
    if verbose>0:
        print(type(forecast))
        print()
        print(forecast.head(3))
        print()
        print(forecast.tail(3))
        print()    
        print(forecast[-1:])
        print()
        print(forecast[-1:].index[0].strftime('%Y-%m-%d'))
        print()
        target_date = forecast[-1:].index[0].strftime('%Y-%m-%d')
    
    
    #return forecast
#     print('temp:')
#     display(forecast.head())    
    return forecast.reset_index(inplace=False).to_dict(orient='records')


# In[ ]:


@anvil.server.callable
def arima_main(ticker='AAPL', ohlc='Adj Close', verbose=0):
    
    if verbose>0:
        print('today:', datetime.now())
    
    start_date = datetime.now() - relativedelta(years=3)    # 3 years ago    
    start_date = start_date - BDay(1)
    start_date = start_date.strftime('%Y-%m-%d')
    if verbose>0:
        print('start_date', start_date)

    end_date = datetime.now() - relativedelta(days=1)       # 1 day ago    
    end_date = end_date - BDay(1)
    end_date = end_date.strftime('%Y-%m-%d')     
    if verbose>0:
        print('end_date', end_date)

    forecast_date = datetime.now() - relativedelta(days=1) + relativedelta(years=5) # 5 years from now
    forecast_date = forecast_date - BDay(1)    
    forecast_date = forecast_date.strftime('%Y-%m-%d')
    if verbose>0:
        print('forecast_date', forecast_date)

    X_train, X_test = load_ticker(ticker, start_date, end_date)
    # I think yfinance automatically skips public holidays in whatever market the ticker falls under, e.g. USA market
    # hence, if the start_date I selected above is a PH, yFinance will not load it. Instead, it will load the next
    # available business day. 
    # so the quickest fix is to take the earliest date AFTER yfinance loads the ticker data and then set my start_date
    # to it, so that when calling ._predict() the start date will match.

    if verbose>0:
        print('\n\nstart date_initial:\t', start_date)
        print('X_train starting date:\t', X_train.index[0].strftime('%Y-%m-%d'))       
        
    start_date = X_train.index[0].strftime('%Y-%m-%d')
    end_date = X_train.index[-1].strftime('%Y-%m-%d')
        
    if verbose>0:
        print('start date_after using X_train starting date:', start_date)
        print()
    
    X_train = X_train[ohlc]
    X_test  = X_test[ohlc] 
    if verbose>0:
        print('\n','X_train.shape:', X_train.shape, 'X_test.shape:',X_test.shape,'\n')    
        print('X_train.head()')
        display(X_train.head(3))
        print()
        print('X_test.head()')
        display(X_test.head(3))        
    
    if verbose>0:
        print('\nBEFORE exec "train_arima_model()"')
    results_ar_1_i_1_ma_1 = train_arima_model(X_train, verbose=verbose)
    if verbose>0:
        print('AFTER exec "train_arima_model()"','\n')

    # forecast date may also be a PH, so need to ensure it is a business day and NOT a PH??
    # so far no error, but something to look out for, maybe?    
    forecast = arima_predict(results_ar_1_i_1_ma_1, start_date, forecast_date, verbose=verbose)
    
    return forecast


# ##### Misc

# In[ ]:


@anvil.server.callable
def hello(name, msg):
    msg = 'From HW_laptop: hello {}, this is your msg: {}. Time is: {}'.format(name,msg, datetime.now())
    return msg


# # main()

# In[ ]:


# Recommendation Engine : must run these to load into globals
load_lu_funds()
load_user_data()
prep_existing_user_profiles()

# since this is based on existing user_data, can precalc?
calc_df_item_profile()
calc_item_based_eu_sim()  


# # Offline Testing

# ##### Recommendation Engine

# In[ ]:


# # Offine Testing: Comment out if not in use
# #Given User, Recommend one or more Items

# user_id = 'uid_72'  
# user_id = 'uid_101'  

# data = {
#     'user_id': [user_id],
#     'risk_appetite': [1],
#     'investment_objective':  [1],
#     'equities_alloc':  [50],
#     'bonds_alloc': [50]
# }
# df = pd.DataFrame(data)

# result = add_new_user_to_user_profiles(df)
# display(result)


# In[ ]:


# #Given Item, recommend one or more items

# fid = 'fid_1'
# result = given_item_recommend_item(fid=fid)
# result


# ##### ARIMA

# In[ ]:


# # Offine Testing: Comment out if not in use
# ticker = "AAPL"
# forecast = arima_main(ticker, verbose=0)

# print(forecast[0])
# print(forecast[0]['index'].strftime('%Y-%m-%d'))
# print(round(forecast[0]['predicted_mean'],2))
# print()
# print(forecast[-1])
# print(forecast[-1]['index'].strftime('%Y-%m-%d'))
# print(round(forecast[-1]['predicted_mean'],2))


# # -----------------------------------------------------

# # Start Server

# In[ ]:


# # Online Server, comment out if doing off-line test
anvil.server.wait_forever()

