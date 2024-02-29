
import pandas as pd
import os
import time
import numpy as np
from pandas.tseries import offsets


def adjust_for_splits_final(df1, df2, asofdate):
   """
   Function to adjust prices and volumes by splits for individual stocks
   :param df1: Dataframe with dates, stock ids, prices and volumes
   :param df2: Dataframe with dates, stock ids and split factors
   :param asofdate: Knowledge date
   :return: Dataframe with split-adjusted prices and volumes
   """
   # create Date columns with time stamps and convert asofdate to timestamp,
   df1["Date"] = pd.to_datetime(df1["pricingDate"])
   df2["Date"] = pd.to_datetime(df2["SplitDate"])
   asofdate_converted = pd.Timestamp(asofdate)

   # use split information on or before asofdate, and make cumulative split factor
   df_split = df2.loc[df2["Date"] <= asofdate_converted]
   df_split = df_split.sort_values(["tradingItemId", "Date"], ascending=[True, False])
   df_split["csf"] = df_split.groupby("tradingItemId").latestSplitFactor.cumprod()
   
   # save first cumulative split factor for each stock id
   df_split_first = df_split.sort_values(df_split.columns.tolist()).drop_duplicates(subset=["tradingItemId"], keep='first')
   df_split_first["Date"] = min(df_split["Date"].min() ,df2["Date"].min()) - offsets.BDay() 

   # shift cumulative split factor by 1, fill the most recent value with 1 and concatinate with saved first cumulative split factor  
   df_split["csf"] = df_split.groupby(["tradingItemId"])["csf"].shift(1)
   df_split["csf"] = df_split["csf"].fillna(1.0)
   df_split = pd.concat([df_split, df_split_first], axis=0)
   df_split = df_split.sort_values(["tradingItemId", "Date"], ascending=[True, False])

   # use price_volume information on or before asofdate
   df_pv = df1.loc[df1["Date"] <= asofdate_converted]

   # merge in split information
   df = pd.merge(df_pv, df_split[["Date", "tradingItemId", "csf"]], on=["Date", "tradingItemId"], how='outer')
   df = df.sort_values(["tradingItemId", "Date"], ascending=[True, True])

   # fill-forward cumulative split factor for each stock
   df.update(df.groupby("tradingItemId")["csf"].ffill())

   # adjust prices and volumes
   df["csf"] = df["csf"].fillna(1.0)
   df["close"] /= df["csf"]
   df["closeUsd"] /= df["csf"]
   df["volume"] *= df["csf"]

   # select rows and columns that we need
   df = df.loc[df["volume"].notnull(), df1.columns]

   return df

#define working directory
#os.chdir("/Users/alexanderkarpikov/Documents/adjust_for_splits/")
#df1 = pd.read_csv("daily_price_volume.zip")
df_part1 = pd.read_csv("daily_price_volume_part1.zip")
df_part2 = pd.read_csv("daily_price_volume_part2.zip")
df1 = pd.concat([df_part1, df_part2],ignore_index=True)
df2 = pd.read_csv("daily_splitinfo.zip")


asofdate = "2019-03-31"

start = time.time()
df_new = adjust_for_splits_final(df1, df2, asofdate)
print("overall time", time.time() - start, "\n")

df_new["pricingDate"] = pd.to_datetime(df_new["pricingDate"])

## Check for AAPL:
print(df_new.loc[(df_new["tradingItemId"] == 2590360) & (df_new["pricingDate"] >= "2014-06-03") & (df_new["pricingDate"] <= "2014-06-13")])

