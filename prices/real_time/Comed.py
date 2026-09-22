import urllib.request, json
import numpy as np
import pandas as pd
import datetime


#datestart=202106010000&dateend=202109012355
with urllib.request.urlopen("https://hourlypricing.comed.com/api?type=5minutefeed&datestart=202101010000&dateend=202112012355") as url:
    data = json.loads(url.read().decode())
    print(data)

print(data[0]['price'])
#https://www.geeksforgeeks.org/python-split-dictionary-keys-and-values-into-separate-lists/
#https://stackoverflow.com/questions/6521892/how-to-access-a-dictionary-key-value-present-inside-a-list
#myvalues = [i['d'] for i in mylist if 'd' in i]
myprice = [i['price'] for i in data if 'price' in i]
mydatetime = [z['millisUTC'] for z in data if 'millisUTC' in z]

myprice_float = []
for i in range(len(myprice)):
    myprice_float.append(float(myprice[i]))

#mydatetime_float = []
#for i in range(len(mydatetime)):
#    mydatetime_float.append(float(mydatetime[i]))

myprice_np = np.asarray(myprice_float)
df_price = pd.DataFrame(myprice_np, columns=['pricing'])
#mydatetime_np = np.asarray(mydatetime_float)
mydatetime_int = [int(i) for i in mydatetime]
mydatetime_np = np.asarray(mydatetime_int)
new_days = mydatetime_np.copy()

# check the difference between millisUTC timestamp
# The difference is not consistent
# =============================================================================
# alex = np.diff(mydatetime_np)
# import matplotlib.pyplot as plt 
# plt.plot(alex)
# plt.show()
# =============================================================================


#%%

df2 = pd.DataFrame(new_days, columns=['datetime'])

df2['datetime'] = pd.to_datetime(df2['datetime'], unit='ms')

#datetime as index
df_timestamp = df2.set_index('datetime')
minutes = df_timestamp.index.minute

minutes_plot = minutes.tolist() 

#minutes_to_plot = minutes.index.values
#minutes_to_plot = minutes.reset_index()
#minutes.plot()
#end = pd.Datetimeindex(df_timestamp['datetime']).minute

#df2 = datetime.datetime.fromtimestamp(milliseconds/1000.0)
#df3 = df2.sort('Date')
##########################example
#ms=1577858100000
#import datetime
#new = datetime.datetime.fromtimestamp(ms/1000.0)
#%%
############## Combine the prices with dates
final_df = pd.concat([df2, df_price],axis=1, ignore_index=True)
from matplotlib import dates as mdates, pyplot as plt
import os
import pytz
#df_counts = df.your_date_column.resample('D').count() 
#df.index = df['datetime']
final_df.columns = ['datetime', 'price']
df = final_df.set_index("datetime")
df.index = df.index.tz_localize("UTC").tz_convert('US/Pacific')
df = df.groupby(pd.Grouper(freq='H')).mean()
df.to_csv(r'Watt_time_hourly_2021.csv', header='true')

fig1, axes = plt.subplots()
df.plot(ax = axes, color="black")
path = os.getcwd()
df.to_csv(f"{path}\\price_comed_2021.csv")
df_std = df.groupby(pd.Grouper(freq='D')).std()
df_var = df.groupby(pd.Grouper(freq='D')).var()
#df_std.plot(ax = axes, color="green")
df_var.columns= ['variance in price']
df_var.plot(ax = axes, color="blue")
df_var_largest_10 = df_var.nlargest(10, "variance in price")
#df_var_largest_10 = df_var.nsmallest(10, "variance in price")
df_var_largest_10.columns = ['largest 10 variance']
df_var_largest_10.plot(ax = axes, color="red", linestyle = ' ', marker='*')
#print(df_var_largest_10)

fig2, axes1 = plt.subplots(2, 5)
i = 0
j = 0
for x in df_var_largest_10.index:
    print(x.date())
    filter_df = df.loc[(df.index.date==x.date())]
    filter_df.to_csv(f'DAH_{x.date()}.csv')
    
    if j >4:
        i+=1
        j=0
    filter_df.plot(ax=axes1[i, j])
    j+=1



max_std = df_std.max()
max_std = df_std.idxmax()
df_mov_std = df.rolling(window=12).std()
df_mov_std.plot(ax = axes, color="pink")
df_mov_std_mean = df_mov_std.groupby(pd.Grouper(freq='D')).mean()
df_mov_std_mean.plot(ax = axes, color="magenta")

plt.show()



# tentative = final_df.set_index('datetime').groupby(pd.Grouper(freq='D'))
#
# store_std = []
# for name, group in tentative:
#     print(name)
#     store_std.append(group.std())
#     #print(group)
#     #store_std.append(tentative.get_group)
#
# dataframe_std=pd.DataFrame(store_std)
#
# ax = dataframe_std.plot(title='standard deviation for data in each day', fontsize=14)
# ax.set_xlabel("5 min data from 01-01-2019 to 01-01-2020", fontsize=14)
# ax.set_ylabel("price (cents/kWh)", fontsize=14)
#
# #dataframe_std.plot(title='standard deviation for prices 2019-01-01 to 2020-01-01')
#
# store_min = []
# for name, group in tentative:
#     print(name)
#     store_min.append(group.min())
#
# dataframe_min=pd.DataFrame(store_min)
#
# ax = dataframe_min.plot(title='minimum price for data in each day', fontsize=14)
# ax.set_xlabel("5 min data from 01-01-2019 to 01-01-2020", fontsize=14)
# ax.set_ylabel("price (cents/kWh)", fontsize=14)
#
# #dataframe_min.plot(title='minimum price for 2019-01-01 to 2020-01-01')
#
# store_max = []
# for name, group in tentative:
#     print(name)
#     store_max.append(group.max())
#
# dataframe_max=pd.DataFrame(store_max)
#
# ax = dataframe_max.plot(title='maximum price for data in each day', fontsize=14)
# ax.set_xlabel("01-01-2019 to 01-01-2020", fontsize=14)
# ax.set_ylabel("price (cents/kWh)", fontsize=14)
#
# store_mean = []
# for name, group in tentative:
#     print(name)
#     store_mean.append(group.mean())
#
# dataframe_mean=pd.DataFrame(store_mean)
#
# ax = dataframe_mean.plot(title='mean price for data in each day', fontsize=14)
# ax.set_xlabel("from 01-01-2019 to 01-01-2020", fontsize=14)
# ax.set_ylabel("price (cents/kWh)", fontsize=14)
#
# store_median = []
# for name, group in tentative:
#     print(name)
#     store_median.append(group.median())
#
# dataframe_median=pd.DataFrame(store_median)
#
# ax = dataframe_median.plot(title='median prices (cents/kWh)', fontsize=14)
# ax.set_xlabel("from 01-01-2019 to 01-01-2020", fontsize=14)
# ax.set_ylabel("price (cents/kWh)", fontsize=14)
#
# ##############################################
# #### concatenate mean and median
# ##############################################
# df_mean_median = pd.concat([dataframe_mean,dataframe_median], axis=1)
# df_mean_median.columns = ['mean', 'median']
#
# ax = df_mean_median.plot(title='mean and median prices (cents/kWh)', fontsize=14)
# ax.set_xlabel("01-01-2019 to 01-01-2020", fontsize=14)
# ax.set_ylabel("cents/kWh", fontsize=14)
#
# #dataframe_max.plot(title='maximum price for 2019-01-01 to 2020-01-01')
#
# prices_inspect = final_df.copy()
#
# #sort by date
#
# prices_inspect.set_index('datetime')
# prices_inspect_2 = prices_inspect.sort_index(ascending=False)
#
# prices_inspect_3 = prices_inspect_2.reset_index()
#
#
# prices_inspect_4 = prices_inspect_3.drop(['index', 'datetime'], axis=1)
#
# ax = prices_inspect_4.plot(title='raw prices', fontsize=14)
# ax.set_xlabel("5 min data from 01-01-2019 to 01-01-2020", fontsize=14)
# ax.set_ylabel(" price (cents/kWh)", fontsize=14)
#
# # THIS WORKS. I can access data.
# ##alexandros = tentative.get_group('2020-01-01')
# #final_df.index = final_df['datetime']
#
# for name, group in tentative:
#     print(name)
#     #store_max.append(group.max())
#
# ########## Tentative dataframe: Look into the Oct 1st 2019 date
# oct_1_2019 = tentative.get_group('2019-10-01')
# oct_1_2019.plot(title='October 1st 2019', fontsize=14)
# ax.set_xlabel("price (cents/kWh)", fontsize=14)
#
# july_1_2019 = tentative.get_group('2019-07-01')
# july_1_2019.plot(title='July 1st 2019', fontsize=14)
# ax.set_xlabel("price (cents/kWh)", fontsize=14)
#
# sep_7_2019 = tentative.get_group('2019-09-07')
# sep_7_2019.plot(title='Sep 7th 2019', fontsize=14)
# ax.set_xlabel("price (cents/kWh)", fontsize=14)
#
# sep_29_2019 = tentative.get_group('2019-09-29')
# sep_29_2019.plot(title='Sep 29th 2019', fontsize=14)
# ax.set_xlabel("price (cents/kWh)", fontsize=14)
#
# sep_29_2019.to_csv(r'C:\Users\vlac284\OneDrive - PNNL\Documents\CLS-grid\ComEd_Sep_29_2019.csv',index=False, header='true')
#
# sep_3_2019 = tentative.get_group('2019-09-03')
# sep_3_2019.plot(title='Sep 3rd 2019', fontsize=14)
# ax.set_xlabel("price (cents/kWh)", fontsize=14)
#
# june_21_2019 = tentative.get_group('2019-06-21')
# june_21_2019.plot(title='June 21st 2019', fontsize=14)
# ax.set_xlabel("price (cents/kWh)", fontsize=14)
#
# june_21_2019.to_csv(r'C:\Users\vlac284\OneDrive - PNNL\Documents\CLS-grid\ComEd_June_21_2019.csv',index=False, header='true')
#
# june_22_2019 = tentative.get_group('2019-06-22')
# june_22_2019.plot(title='June 22nd 2019', fontsize=14)
# ax.set_xlabel("price (cents/kWh)", fontsize=14)
#
# june_22_2019.to_csv(r'C:\Users\vlac284\OneDrive - PNNL\Documents\CLS-grid\ComEd_June_22_2019.csv',index=False, header='true')
#
# june_23_2019 = tentative.get_group('2019-06-23')
# june_23_2019.plot(title='June 23rd 2019', fontsize=14)
# ax.set_xlabel("price (cents/kWh)", fontsize=14)
#
# june_23_2019.to_csv(r'C:\Users\vlac284\OneDrive - PNNL\Documents\CLS-grid\ComEd_June_23_2019.csv',index=False, header='true')
#
# june_24_2019 = tentative.get_group('2019-06-24')
# june_24_2019.plot(title='June 24th 2019', fontsize=14)
# ax.set_xlabel("price (cents/kWh)", fontsize=14)
#
# june_24_2019.to_csv(r'C:\Users\vlac284\OneDrive - PNNL\Documents\CLS-grid\ComEd_June_24_2019.csv',index=False, header='true')
#
# june_25_2019 = tentative.get_group('2019-06-25')
# june_25_2019.plot(title='June 25th 2019', fontsize=14)
# ax.set_xlabel("price (cents/kWh)", fontsize=14)
#
# june_25_2019.to_csv(r'C:\Users\vlac284\OneDrive - PNNL\Documents\CLS-grid\ComEd_June_25_2019.csv',index=False, header='true')
#
# #####################################
# july_21_2019 = tentative.get_group('2019-07-21')
# july_21_2019.plot(title='July 21st 2019', fontsize=14)
# ax.set_xlabel("price (cents/kWh)", fontsize=14)
# july_21_2019['datestamp'] = july_21_2019.index
#
# july_21_2019.to_csv(r'C:\Users\vlac284\OneDrive - PNNL\Documents\CLS-grid\ComEd_July_21_2019.csv',index=False, header='true')
#
# july_22_2019 = tentative.get_group('2019-07-22')
# july_22_2019.plot(title='July 22nd 2019', fontsize=14)
# ax.set_xlabel("price (cents/kWh)", fontsize=14)
# july_22_2019['datestamp'] = july_22_2019.index
#
# july_22_2019.to_csv(r'C:\Users\vlac284\OneDrive - PNNL\Documents\CLS-grid\ComEd_July_22_2019.csv',index=False, header='true')
#
# july_23_2019 = tentative.get_group('2019-07-23')
# july_23_2019.plot(title='July 23rd 2019', fontsize=14)
# ax.set_xlabel("price (cents/kWh)", fontsize=14)
# july_23_2019['datestamp'] = july_23_2019.index
#
# july_23_2019.to_csv(r'C:\Users\vlac284\OneDrive - PNNL\Documents\CLS-grid\ComEd_July_23_2019.csv',index=False, header='true')
#
# july_24_2019 = tentative.get_group('2019-07-24')
# july_24_2019.plot(title='July 24th 2019', fontsize=14)
# ax.set_xlabel("price (cents/kWh)", fontsize=14)
# july_24_2019['datestamp'] = july_24_2019.index
#
# july_24_2019.to_csv(r'C:\Users\vlac284\OneDrive - PNNL\Documents\CLS-grid\ComEd_July_24_2019.csv',index=False, header='true')
#
# july_25_2019 = tentative.get_group('2019-07-25')
# july_25_2019.plot(title='July 25th 2019', fontsize=14)
# ax.set_xlabel("price (cents/kWh)", fontsize=14)
# july_25_2019['datestamp'] = july_25_2019.index
#
# july_25_2019.to_csv(r'C:\Users\vlac284\OneDrive - PNNL\Documents\CLS-grid\ComEd_July_25_2019.csv',index=False, header='true')
#
#
# #%%
# tentative_month = final_df.set_index('datetime').groupby(pd.Grouper(freq='M'))
#
# store_std_mo = []
# for name, group in tentative_month:
#     print(name)
#     store_std_mo.append(group.std())
#     #print(group)
#     #store_std.append(tentative.get_group)
#
# dataframe_std_mo=pd.DataFrame(store_std_mo)
#
# ax = dataframe_std_mo.plot(marker = '.',title='standard deviation', fontsize=14)
# ax.set_xlabel("months", fontsize=14)
# ax.set_ylabel("price (cents/kWh)", fontsize=14)
#
# store_mean_mo = []
# for name, group in tentative_month:
#     print(name)
#     store_mean_mo.append(group.mean())
#     #print(group)
#     #store_std.append(tentative.get_group)
#
# dataframe_mean_mo=pd.DataFrame(store_mean_mo)
#
# ax = dataframe_mean_mo.plot(marker = '.',title='mean price', fontsize=14)
# ax.set_xlabel("months", fontsize=14)
# ax.set_ylabel("price (cents/kWh)", fontsize=14)
# ax.set_ylim([1.8, 2.8])
#
# store_median_mo = []
# for name, group in tentative_month:
#     print(name)
#     store_median_mo.append(group.median())
#     #print(group)
#     #store_std.append(tentative.get_group)
#
# dataframe_median_mo=pd.DataFrame(store_median_mo)
#
# ax = dataframe_median_mo.plot(marker = '.',title='median price', fontsize=14)
# ax.set_xlabel("months", fontsize=14)
# ax.set_ylabel("price (cents/kWh)", fontsize=14)
# ax.set_ylim([1.8, 2.8])
#
# dataframe_mo_std_mean_median = pd.concat([dataframe_std_mo, dataframe_mean_mo,dataframe_median_mo], axis=1)
# dataframe_mo_std_mean_median.columns = ['price std', 'price mean', 'price median']
#
# ax = dataframe_mo_std_mean_median.plot(marker = '.',title='price (cents/kWh)', fontsize=14)
# ax.set_xlabel("months", fontsize=14)
# ax.set_ylabel("price", fontsize=14)
#
#
#
# #%%
# #https://stackoverflow.com/questions/35907421/pandas-split-dataframe-into-multiple-dataframes-based-on-dates
#
# #https://stackoverflow.com/questions/35907421/pandas-split-dataframe-into-multiple-dataframes-based-on-dates
#
# #store_data = []
# #for group_name, df_group in final_df.groupby(Grouper(freq='D')):
# #    store_data.append(final_df.groupby(pd.Grouper(freq='D')))
# # finding STD
#
# final_df_2 = final_df.copy()
#
# final_df_2.drop(final_df_2.columns[0], axis=1)
#
# tentative = final_df_2.groupby(pd.Grouper(freq='D'))
#
# tentative = final_df.groupby(pd.Grouper(key='datetime', freq="D"))


#https://re-thought.com/group-by/


#https://chrisalbon.com/python/data_wrangling/pandas_group_data_by_time/

#https://chrisalbon.com/python/data_wrangling/group_pandas_data_by_hour_of_the_day/