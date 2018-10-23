
import pandas as pd
import numpy as np
import math
import re
class Binning:
    def __init__(self,bin_df, gbflag = 'gbflag', bin_num = 10):
        self.bin_df = bin_df
        self.gbflag = gbflag
        self.bin_num = bin_num

    def binning_num(self,column):
        self.bin_df[column] = self.bin_df[column].fillna(-9999)
        nan_df = self.bin_df[self.bin_df[column] == -9999]
        an_df = self.bin_df[self.bin_df[column] != -9999]    
        d1_1_temp = pd.DataFrame({"X": an_df[column], "Y": an_df[self.gbflag], column: pd.qcut(an_df[column], self.bin_num,precision=2,duplicates = 'drop')})
        d1_1 = d1_1_temp.sort_values(by = ['X'])
        if nan_df.shape[0] >0 :
            d1_2 = pd.DataFrame({"X": nan_df[column], "Y": nan_df[self.gbflag], column: pd.qcut(nan_df[column], 1,duplicates = 'drop')})
            d1 = pd.concat([d1_1,d1_2])
        else:
            d1 = d1_1
        d2 = pd.crosstab(d1[column],d1['Y'],margins =True)
        d2['Badrate'] = (d2[0] / d2['All']).apply(lambda x: "{0:.2f}%".format(x*100))
        d2['Pctn'] = d2['All'] / self.bin_df.shape[0]
        d2['Pctn'] = d2['Pctn'].apply(lambda x: "{0:.2f}%".format(x*100))
        return d2
    
    def binning_char(self,column): 
        self.bin_df[column] = self.bin_df[column].fillna(-9999)
        d2 = pd.crosstab(self.bin_df[column],self.bin_df[self.gbflag],margins =True)
        d2['Badrate'] = (d2[0] / d2['All']).apply(lambda x: "{0:.2f}%".format(x*100))
        d2['Pctn'] = d2['All'] / self.bin_df.shape[0]
        d2['Pctn'] = d2['Pctn'].apply(lambda x: "{0:.2f}%".format(x*100))        
        return d2

    def binning_print(self):
        print_df = pd.DataFrame()
        for column in self.bin_df.columns:
            column_df = pd.DataFrame([[column,column,column,column,column]],columns=[0, 1, 'All', 'Badrate', 'Pctn'],index =[column])
            if column != self.gbflag and self.bin_df[column].unique().shape[0] < 50:
                if pd.unique(self.bin_df[column]).shape[0] < 20 or self.bin_df[column].dtype not in ['float','int','float64','int64']:
                    print(self.binning_char(column))
                    print_df = pd.concat([print_df,column_df])
                    print_df = pd.concat([print_df,self.binning_char(column)])
                else:
                    print(self.binning_num(column))
                    print_df = pd.concat([print_df,column_df])
                    print_df = pd.concat([print_df,self.binning_num(column)])
        return print_df
        
    def iv_column(self,column):
        iv_dict = {'column':column}
        if pd.unique(self.bin_df[column]).shape[0] > 1 and re.sub(u'_','',column.lower()) not in [self.gbflag, 'opendate', 'appid', 'userid']:
            if pd.unique(self.bin_df[column]).shape[0] < 20 or self.bin_df[column].dtype not in ['float','int','float64','int64']:
                d2 = self.binning_char(column)
            else:
                d2 = self.binning_num(column)
            d2 = d2.assign(Badratio = d2[0] / d2[0]['All'],Goodratio = d2[1] / d2[1]['All'])            
            d2 = d2.assign(woe = d2.apply(lambda d2: math.log((d2['Goodratio']+0.000000001)/(d2['Badratio']+0.000000001)),axis = 1))             
            d2 = d2.assign(iv = d2.apply(lambda d2 : d2['woe']*(d2['Goodratio']-d2['Badratio']),axis = 1))           
            iv_dict['bin_num'] = d2.shape[0]-1
            iv_dict['iv'] = d2['iv'].sum()
        return iv_dict
        
    def iv(self):
        lst_dict_iv = []
        for column in self.bin_df.columns:
            if pd.unique(self.bin_df[column]).shape[0] > 1 and column != self.gbflag:
                iv_dict = self.iv_column(column)
                lst_dict_iv.append(iv_dict)
        df_iv = pd.DataFrame(lst_dict_iv)
        df_iv_sort = df_iv.sort_values(by = ['iv'],ascending=False)
        return df_iv_sort
        
                    
