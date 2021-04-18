import pandas as pd
import numpy as np
import geopandas as gpd
import pyproj
import random
import uuid
from AgentCreationClassAPR15 import agentsCreator
# Pyproj Correction
pyproj.datadir.set_data_dir('/Users/shai/anaconda3/envs/geo_env/share/proj')


class simGenerator:
    arnonaSqM = 5.43
    rentPPM = 70
    buyPPM = 20000
    owners = 0.65
    saveTo = 'sensitivity_simGnerator_april_15.xlsx'

    def __init__(self):
        self.jewishPopDemo2019 = pd.read_excel(
            'israel_population_jewish_lamas_groups_of_10_2019.xlsx')
        self.jewishPopDemo2019.reset_index(inplace=True, drop=True)
        self.jewishPopDemo2019.drop([0, 1], inplace=True)
        tot = self.jewishPopDemo2019['Total'].sum()
        self.jewishPopDemo2019['ratio'] = self.jewishPopDemo2019['Total']/tot
        self.mid = [10*i+25 for i in range(8)]
        self.jewishPopDemo2019['middle'] = self.mid
        self.ageDist = [0.2, 0.2, 0.18, 0.15, 0.14, 0.08, 0.04, 0.01]
        self.ageMiddle = self.jewishPopDemo2019['middle'].values.tolist()
        self.ac = agentsCreator()
        self.ac.createAgentsAgents()
        self.bldgs = pd.read_excel(
            'BuildingInSimulationAndStatsApril12.xlsx')  # Bldgs Data
        # original Agents - can be gerenated many times for sensitivity analysis
        #originalAgents = pd.read_excel('OrigianlAgentsApril12_2021.xlsx')
        self.originalAgents = self.ac.agentsDS.copy()
        self.newApartments = pd.read_excel(
            'newApartmentsDataSetApril_12_1120.xlsx')  # new apartments
        self.newApartments.drop(columns='Unnamed: 0', inplace=True)
        bldg_reference = gpd.read_file('Json/simBldgsData09042021.geojson')
        self.bldAfter = bldg_reference[bldg_reference['status']
                                       == 'Building after']
        self.bldAfter.reset_index(drop=True, inplace=True)
        self.bld_floor = self.bldAfter[['bld_addres', 'floors']]
        self.newBldgMaintenance = pd.DataFrame({'floor_min': [0, 5, 9, 13], 'floor_max': [
                                               4, 8, 12, 100], 'cost': [250, 320, 400, 450]})

    def getConstFromFloor(self, floor):
        floorInt = str(int(floor))
        cost = self.newBldgMaintenance.query(
            f"floor_min<={floorInt} and floor_max>={floorInt}")['cost']
        return cost.values[0]

    def getBldHeight(self, bldCode):
        Floors = self.bld_floor.query(f"bld_addres=='{bldCode}'")['floors']
        return Floors.values[0].astype(int)

    def generateSimulation(self):
        self.ac.createAgentsAgents()
        AgentsTimeSeries = self.ac.agentsDS.copy()
        #AgentsTimeSeries.drop(columns=['Unnamed: 0'], inplace=True)
        AgentsTimeSeries['prjectType'] = 0
        AgentsTimeSeries['tic'] = 0
        AgentsTimeSeries['status'] = 'stay'
        AgentsTimeSeries['noDiscount'] = AgentsTimeSeries['noDiscount'].fillna(
            0)
        AgentsTimeSeriesOriginal = AgentsTimeSeries.copy()
        self.bldgs.sort_values(by='OrderA', inplace=True)
        for tic in self.bldgs['OrderA'].values:
            currentProject = self.bldgs.query(
                'OrderA=='+str(tic))['ProjNumber'].values[0]
            projectType = self.bldgs.query(
                'OrderA=='+str(tic))['ProjType'].values[0].astype(int)
            newApartmentsSlice = self.newApartments.query(
                'ProjNumber=="'+currentProject+'"').copy()
            newApartmentsSlice.reset_index(inplace=True, drop=True)
            CurrentAgents = AgentsTimeSeriesOriginal.query(
                'ProjNumber=="'+currentProject+'"').copy().reset_index(drop=True)
            CurrentAgents.drop(columns=['bldCode', 'doorIndex', 'bldCodeDoorIndex',
                                        'ProjNumber', 'aprtmentSize', 'tic', 'prjectType'], inplace=True)
            CurrentAgentsNewApartments = pd.concat(
                [newApartmentsSlice, CurrentAgents], axis=1).reset_index(drop=True)
            CurrentAgentsNewApartments['tic'] = tic
            AgentsTimeSeries = pd.concat(
                [AgentsTimeSeries, CurrentAgentsNewApartments]).reset_index(drop=True)
            # AgentsTimeSeries.reset_i
        con = AgentsTimeSeries.query("tic>0").index
        AgentsTimeSeries.loc[con, 'Floors'] = AgentsTimeSeries.loc[con, 'bldCode'].apply(
            self.getBldHeight)
        AgentsTimeSeries.loc[AgentsTimeSeries.query("tic>0").index, "Floors"] \
            = AgentsTimeSeries.loc[AgentsTimeSeries.query("tic>0").index, "bldCode"]\
            .apply(lambda x: self.bld_floor.query(f"bld_addres=='{x}'")['floors'].values[0].astype(int))

        AgentsTimeSeries.loc[AgentsTimeSeries.query("tic>0").index, 'MainCost'] = AgentsTimeSeries.loc[AgentsTimeSeries.query(
            "tic>0").index, 'Floors'].apply(self.getConstFromFloor)

        AgentsTimeSeries.loc[(AgentsTimeSeries['tic'] > 0), 'cityTax'] = AgentsTimeSeries.loc[(
            AgentsTimeSeries['tic'] > 0), 'aprtmentSize']*simGenerator.arnonaSqM

        AgentsTimeSeries.loc[(AgentsTimeSeries['tic'] > 0), 'CostForStaying'] = AgentsTimeSeries.loc[(
            AgentsTimeSeries['tic'] > 0), 'cityTax']+AgentsTimeSeries.loc[(AgentsTimeSeries['tic'] > 0), 'MainCost']
        # Not Null do this

        con = ((AgentsTimeSeries['income'].notna())) & (
            AgentsTimeSeries['tic'] > 0)

        AgentsTimeSeries.loc[con, 'ratioCostForStaying'] = AgentsTimeSeries.loc[con,
                                                                                'CostForStaying']/AgentsTimeSeries.loc[con, 'income']

        AgentsTimeSeries.loc[AgentsTimeSeries.query(
            "tic>0 and rent==1.0").index, 'status'] = 'leave'
        AgentsTimeSeries.loc[AgentsTimeSeries.query(
            "tic>0 and rent==1.0").index, 'reason_leave'] = 'Rent'

        AgentsTimeSeries.loc[AgentsTimeSeries.query(
            "(tic>0) and (age>65) and (status=='stay')").index, 'status'] = 'leave'
        AgentsTimeSeries.loc[AgentsTimeSeries.query(
            "(tic>0) and (age>65) and (status=='leave') and ('reason_leave')!='income'").index, 'reason_leave'] = 'Age'

        AgentsTimeSeries.loc[AgentsTimeSeries.query(
            "(tic>0) and (ratioCostForStaying>0.08) and (status=='stay')").index, 'status'] = 'leave'

        AgentsTimeSeries.loc[AgentsTimeSeries.query(
            "(tic>0) and (ratioCostForStaying>0.08) and (status=='leave') and (reason_leave.isnull())").index, 'reason_leave'] = 'Burden'

        AgentsTimeSeries['mortgage'] = 0
        AgentsTimeSeries['rentPrice'] = 0
        AgentsTimeSeries.loc[AgentsTimeSeries['prjectType'] == 3, 'age'] += 3
        AgentsTimeSeries.loc[AgentsTimeSeries['prjectType'].isin(
            [1, 2]), 'age'] += 2
        newAgents = AgentsTimeSeries.query(
            "status.isnull() or status=='leave'", engine='python').copy()
        newAgents.loc[newAgents.query(
            "status.isnull()", engine='python').index, 'group'] = 'existing'
        newAgents.loc[newAgents.query(
            "status=='leave'", engine='python').index, 'group'] = 'add'
        newAgents['yearsInBldg'] = 0

        num = len(newAgents)
        op = self.ageMiddle
        p = self.ageDist
        ages = np.random.choice(op, size=num, p=p)
        rent_own = np.random.choice(
            ['rent', 'own'], size=num, p=[1-simGenerator.owners, simGenerator.owners])
        rent_filter = rent_own == 'rent'
        own_filter = rent_own == 'own'
        newAgents['age'] = ages
        newAgents['age'] = newAgents['age'].apply(
            lambda x: np.random.randint(x-5, x+5))  # add varitation or noise ot ages
        newAgents.loc[:, ['lowDiscount',
                          'highDiscount', 'noDiscount']] = [0, 0, 1]
        newAgents.loc[:, ['rent', 'own']] = [0, 0]
        newAgents.loc[rent_filter, 'rent'] = 1
        newAgents.loc[own_filter, 'own'] = 1
        newAgents['agentID'] = newAgents['agentID'].apply(
            lambda x: uuid.uuid1())
        newAgents['status'] = 'New Comers'
        newAgents['reason_leave'] = np.nan

        newAgents['HouseValue'] = 0
        newAgents['rentPrice'] = 0
        rentFilter = newAgents.query('rent==1').index
        newAgents.loc[rentFilter, 'rentPrice'] = simGenerator.rentPPM * \
            newAgents.loc[rentFilter, 'aprtmentSize']

        ownFilter = newAgents.query('own==1').index
        newAgents.loc[ownFilter, 'HouseValue'] = newAgents.loc[ownFilter,
                                                               'aprtmentSize'] * simGenerator.buyPPM
        newAgents.loc[ownFilter, 'mortgage'] = newAgents.loc[ownFilter, 'HouseValue'].apply(
            lambda x: self.mortgageCal(houseValue=x, downPaymentPercent_range=(0.25, 0.26))).astype(int)
        newAgents['CostForStaying'] = newAgents['MainCost'] + \
            newAgents['cityTax'] + newAgents['rentPrice'] + \
            newAgents['mortgage']
        newAgents['baseIncome'] = newAgents['CostForStaying'] / \
            0.38  # base is 38% for burden
        newAgents['income'] = newAgents['baseIncome'] + \
            newAgents['baseIncome'].apply(
                lambda x: np.random.randint(0, 5000)).astype(int)
        newAgents['ratioCostForStaying'] = (
            newAgents['CostForStaying']/newAgents['income'])

        newAgents_Merge = newAgents.query('group=="existing"').drop(
            columns=['HouseValue', 'rentPrice', 'baseIncome', 'group'])
        newAgents_Add = newAgents.query('group=="add"').drop(
            columns=['HouseValue', 'rentPrice', 'baseIncome', 'group'])
        # Insert new Comers
        AgentsTimeSeries.loc[newAgents_Merge.index] = newAgents_Merge.copy()
        AgentsTimeSeries = AgentsTimeSeries.append(newAgents_Add)
        AgentsTimeSeries.reset_index(inplace=True, drop=True)
        # AgentsTimeSeries.to_excel(simGenerator.saveTo)
        return(AgentsTimeSeries)

    def mortgageCal(self, houseValue, downPaymentPercent_range=(0.25, 0.5), years_pay=25, intrest=3.46):
        '''
            houseValue - House Value
            downPaymentPercent_range=(0.25, 0.5)
            years_pay=25
            intrest=3.46
        '''
        # Mortage Calculator
        # houseValue for example 2 Milion Shekels
        # downPayment percent the the percent that the Agent can pay of the house 25% is 500000 NIS
        # year_pay typical 25 years
        # interset typical 3.46
        dppr = downPaymentPercent_range
        downPaymentPercent = random.uniform(dppr[0], dppr[1])
        downPayment = houseValue * downPaymentPercent  # calculating the downPayment
        P = houseValue-downPayment  # Mortrage requested
        i_m = ((intrest)/100.0)/12.0  # interset percent divided by 12 months
        n_m = years_pay*12  # convert years to months
        M = (P*i_m*np.power((1+i_m), n_m))/(np.power((1+i_m), n_m)-1)
        return M
