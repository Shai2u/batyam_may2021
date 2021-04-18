import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from simRunSensitivityApr15 import simGenerator
pd.options.display.max_columns = 100


class senAnalyze:
    colorFile = 'colors_dict_April_15_2021.xlsx'
    incomeDict = {'Low': 9000, 'Medium': 19500, 'High': 1000000}
    Age = {'Under 65': 65, 'Above 65': 65}
    gridBG = '#f2f2f2'

    def __init__(self):
        self.sim = simGenerator()
        self.res_df = self.sim.generateSimulation()
        self.colorExcel = pd.read_excel(senAnalyze.colorFile)
        self.res_df['stay'] = 0
        self.res_df['stay'] = self.res_df['status'].apply(
            lambda x: 1 if x == 'stay' else 0)
        self.res_df['leave'] = 0
        self.res_df['leave'] = self.res_df['status'].apply(
            lambda x: 1 if x == 'leave' else 0)
        self.res_df['New Comers'] = 0
        self.res_df['New Comers'] = self.res_df['status'].apply(
            lambda x: 1 if x == 'New Comers' else 0)
        self.res_df.fillna(0, inplace=True)
        self.res_df['Under 65'] = 0
        self.res_df['Above 65'] = 0
        self.res_df['Low Income'] = 0
        self.res_df['Medium Income'] = 0
        self.res_df['High Income'] = 0

        self.res_df['Under 65'] = self.res_df['age'].apply(
            lambda x: 1 if x < 65 else 0)
        self.res_df['Above 65'] = self.res_df['age'].apply(
            lambda x: 1 if x >= 65 else 0)
        self.res_df['Low Income'] = self.res_df['income'].apply(
            lambda x: 1 if (x < senAnalyze.incomeDict['Low']) else 0)
        self.res_df['Medium Income'] = self.res_df['income'].apply(
            lambda x: 1 if (x >= senAnalyze.incomeDict['Low']) & (x < senAnalyze.incomeDict['Medium']) else 0)
        self.res_df['High Income'] = self.res_df['income'].apply(
            lambda x: 1 if (x >= senAnalyze.incomeDict['Medium']) else 0)
        self.cols_keep = ['aprtmentSize', 'ProjNumber', 'yearsInBldg', 'age', 'rent', 'own', 'agentID', 'prjectType', 'tic', 'status',
                          'CostForStaying', 'rentPrice', 'stay', 'leave', 'New Comers', 'Under 65', 'Above 65', 'Low Income', 'Medium Income', 'High Income']
        self.cols_stat = ['aprtmentSizeMean', 'ProjNumber', 'yearsInBldgMean', 'aprtmentSizeMeanStay', 'aprtmentSizeNewComer', 'AgeMean', 'AgeMeanNew', 'AgeMeanStay', 'AgeMeanLeave', 'AgeOldStayNew', 'AgeYoungStayNew', 'AgeOldStay', 'AgeYoungStay', 'AgeOldNew', 'AgeYoungNew', 'IncomeMean', 'IncomeMeanStay', 'IncomeMeanNew', 'IncomeMeanLeave', 'IncomeHighStay', 'IncomeMedStay',
                          'IncomeLowStay', 'IncomeHighNew', 'IncomeMedNew', 'IncomeLowNew', 'IncomeHighStayNew', 'IncomeMedStayNew', 'IncomeLowStayNew', 'meanIncomeStay', 'meanIncomeNewComers', 'meanIncomeStay_N_new', 'rentCount', 'ownCount', 'rentStayCount', 'rentNewCount', 'ownStayCount', 'ownNewCount', 'TotalAgentsCount', 'prjectType', 'tic', 'stay', 'new comers', 'CostForStaying', 'rentPrice']
        self.res2 = pd.DataFrame()

    def generate_analyze(self, with_zero=False):
        simAggStat = pd.DataFrame(columns=self.cols_stat)
        self.ticList = self.res_df['tic'].unique()
        removeList = []
        for tic in self.ticList:
            projType = self.res_df[self.res_df['tic']
                                   == tic]['prjectType'].iloc[0]
            if tic == 0:
                subset = self.res_df[self.res_df['tic']
                                     == tic][self.cols_keep].copy()
                subset_notLeave = subset[subset['status'].isin(
                    ['stay', 'New Comers'])].copy()
                subset_leave = subset[subset['status'].isin(['leave'])].copy()
                agg_0 = subset_notLeave.agg({'aprtmentSize': 'mean', 'yearsInBldg': 'mean', 'age': 'mean',
                                             'rent': 'sum', 'own': 'sum', 'agentID': 'count', 'rentPrice': 'mean', 'stay': 'sum'})
                agg_0_leave = subset_leave.agg({'leave': 'count'})
                simAggStat.loc[tic, ['aprtmentSizeMean', 'yearsInBldgMean', 'AgeMean', 'rentCount',
                                     'ownCount', 'TotalAgentsCount', 'rentPrice', 'stay']] = agg_0.to_frame().transpose().values
                simAggStat.loc[tic, 'leave'] = agg_0_leave[0]
            else:

                projNumber = self.res_df[self.res_df['tic']
                                         == tic]['ProjNumber'].iloc[0]
                removeList.append(projNumber)
                # Grab all the agents from tic and below
                subset_step1 = self.res_df[(self.res_df['tic'] <= tic)].copy()
                subset_step2 = subset_step1[((subset_step1['tic'] == 0) & (~subset_step1['ProjNumber'].isin(
                    removeList))) | (subset_step1['tic'] > 0)]  # Remove the project from zero
                #subset = self.res_df[ (((self.res_df['tic']<=tic) & (self.res_df['tic']>0)) |  ((self.res_df['tic']==0) & (~self.res_df['ProjNumber'].isin(removeList))))]
                subset_notLeave = subset_step2[subset_step2['status'].isin(
                    ['stay', 'New Comers'])].copy()
                subset_stay = subset_notLeave[subset_notLeave['stay'] == 1].copy(
                )
                subset_newcomers = subset_notLeave[subset_notLeave['New Comers'] == 1].copy(
                )
                subset_leave = subset_step2[subset_step2['leave'] == 1].copy()
                agg_All = subset_notLeave.agg({'aprtmentSize': 'mean', 'yearsInBldg': 'mean', 'age': 'mean', 'rent': 'sum', 'own': 'sum', 'agentID': 'count', 'rentPrice': 'mean', 'stay': 'sum',
                                               'New Comers': 'sum', 'CostForStaying': 'mean', 'Under 65': 'sum', 'Above 65': 'sum', 'Low Income': 'sum', 'Medium Income': 'sum', 'High Income': 'sum', 'income': 'mean'})
                agg_Stay = subset_stay.agg({'aprtmentSize': 'mean', 'age': 'mean', 'rent': 'sum', 'own': 'sum', 'Under 65': 'sum',
                                            'Above 65': 'sum', 'Low Income': 'sum', 'Medium Income': 'sum', 'High Income': 'sum', 'income': 'mean'})
                agg_NewComers = subset_newcomers.agg({'aprtmentSize': 'mean', 'age': 'mean', 'rent': 'sum', 'own': 'sum', 'Under 65': 'sum',
                                                      'Above 65': 'sum', 'Low Income': 'sum', 'Medium Income': 'sum', 'High Income': 'sum', 'income': 'mean'})
                agg_leave = subset_leave.agg({'leave': 'count'})
                simAggStat.loc[tic, ['aprtmentSizeMean', 'yearsInBldgMean', 'AgeMean', 'rentCount', 'ownCount', 'TotalAgentsCount', 'rentPrice', 'stay', 'new comers', 'CostForStaying',
                                     'AgeYoungStayNew', 'AgeOldStayNew', 'IncomeLowStayNew', 'IncomeMedStayNew', 'IncomeHighStayNew', 'meanIncomeStay_N_new']] = agg_All.to_frame().transpose().values[0]
                simAggStat.loc[tic, 'leave'] = agg_leave[0]
                simAggStat.loc[tic, ['aprtmentSizeMeanStay', 'AgeMeanStay', 'rentStayCount', 'ownStayCount', 'AgeYoungStay', 'AgeOldStay',
                                     'IncomeLowStay', 'IncomeMedStay', 'IncomeHighStay', 'meanIncomeStay']] = agg_Stay.to_frame().transpose().values[0]
                simAggStat.loc[tic, ['aprtmentSizeNewComer', 'AgeMeanNew', 'rentNewCount', 'ownNewCount', 'AgeYoungNew', 'AgeOldNew',
                                     'IncomeLowNew', 'IncomeMedNew', 'IncomeHighNew', 'meanIncomeNewComers']] = agg_NewComers.to_frame().transpose().values[0]
                simAggStat.loc[tic, 'ProjNumber'] = projNumber
            simAggStat.loc[tic, 'tic'] = tic
            simAggStat.loc[tic, 'prjectType'] = projType
        if (with_zero):
            self.res2 = simAggStat.loc[0:].copy()
        else:
            self.res2 = simAggStat.loc[1:].copy()
        self.res2 = self.res2[self.res2.columns[self.res2.notnull(
        ).loc[1].values]].copy()
