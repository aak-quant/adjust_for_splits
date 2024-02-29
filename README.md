My Python code to correct data for splits events.
The main part of the code is the function called adjust_for_splits_final to adjust prices and volumes by splits for individual stocks.
The function takes three inputs:
  1) df1 - the dataframe with dates, stock ids, prices and volumes
  2) df2 -the dataframe with dates, stock ids and split factors
  3) asofdate - the  knowledge date, the last date for which prices, volumes and split information are available. For the example provided in your email  asofdate = "2019-03-31”.

The function returns the  dataframe with split-adjusted prices and volumes: close, closeUsd and volume.
The function is quite generic and it can use any reasonable asofdate. As a unit test I got results for APPL and asofdate = "2019-03-31” .
