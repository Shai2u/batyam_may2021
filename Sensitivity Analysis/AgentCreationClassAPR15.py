import uuid
import pandas as pd
import numpy as np


class agentsCreator:
    def __init__(self):
        self.excelBuildingInformation = "BuildingInSimulationAndStatsApril12.xlsx"
        self.buildingsDf = pd.read_excel(self.excelBuildingInformation)
        mainColumns = self.buildingsDf.columns.tolist()
        self.buildingsDf = self.buildingsDf.drop(columns=['Unnamed: 0'])
        self.AgeDistribution = pd.DataFrame({'Age': [20, 30, 40, 50, 65, 70, 80, 90, 100], 'Distribution': [
            0.14, 0.18, 0.23, 0.14, 0.09, 0.08, 0.07, 0.06, 0.01]})
        self.mainColumns = ['ProjNumber', 'BeforeBldgs', 'min_living_till_2020', 'max_living_till_2020', 'Average_age_2020', 'StdDev_age_2020',
                            'Before_app', 'Above_65', 'Area_round_mode', 'High_discount_sum', 'Low_Discount_35_sum', 'Renter_sum', 'averageApartments']
        self.ApartmentColums = ['bldCode', 'doorIndex', 'bldCodeDoorIndex', 'ProjNumber', 'aprtmentSize',
                                'yearsInBldg', 'age', 'lowDiscount', 'highDiscount', 'noDiscount', 'income', 'rent', 'own', 'agentID']
        self.agentsDS = pd.DataFrame()

    def createAgentsAgents(self):
        orginalAgentsDS = pd.DataFrame(columns=self.ApartmentColums)
        orginalAgentsDS['doorIndex'] = orginalAgentsDS['doorIndex'].astype(
            'int')
        orginalAgentsDS['aprtmentSize'] = orginalAgentsDS['aprtmentSize'].astype(
            'int')
        orginalAgentsDS['yearsInBldg'] = orginalAgentsDS['yearsInBldg'].astype(
            'int')
        orginalAgentsDS['age'] = orginalAgentsDS['age'].astype('int')
        orginalAgentsDS['lowDiscount'] = orginalAgentsDS['lowDiscount'].astype(
            'int')
        orginalAgentsDS['highDiscount'] = orginalAgentsDS['highDiscount'].astype(
            'int')
        orginalAgentsDS['noDiscount'] = orginalAgentsDS['noDiscount'].astype(
            'int')
        orginalAgentsDS['rent'] = orginalAgentsDS['rent'].astype(
            'int')
        orginalAgentsDS['own'] = orginalAgentsDS['own'].astype('int')
        orginalAgentsDSJustHead = orginalAgentsDS.copy()  # Just Leave Head
        for i in self.buildingsDf.index:
            bldgInfo = self.buildingsDf.loc[i, self.mainColumns]
            currentBldg = self.createAgentAndApartment(
                bldgInfo, orginalAgentsDSJustHead.copy())
            if (i == 0):
                orginalAgentsDS = currentBldg
            else:
                orginalAgentsDS = orginalAgentsDS.append(currentBldg)

        orginalAgentsDS.reset_index(inplace=True)
        orginalAgentsDS.drop(columns='index', inplace=True)
        discountTalbe = pd.DataFrame({'noDiscount': [9220, 15430], 'lowDiscount': [
            6514, 9219], 'highDiscount': [5011, 6513]}, index=['min_', 'max_'])
        for item in ['lowDiscount', 'highDiscount', 'noDiscount']:
            con = orginalAgentsDS[item] == 1
            orginalAgentsDS.loc[con, 'income'] = orginalAgentsDS.loc[con].apply(lambda x: np.random.randint(
                discountTalbe.loc['min_', item], discountTalbe.loc['max_', item]), axis=1)
        orginalAgentsDS['agentID'] = orginalAgentsDS['agentID'].apply(
            lambda x: uuid.uuid1())
        self.agentsDS = orginalAgentsDS
        # orginalAgentsDS.to_excel('OrigianlAgents_sens.xlsx')

    def createAgentAndApartment(self, bldgInfo, hedersonly):
        bldgInfo['Above_65'] = bldgInfo['Above_65'].astype(int)
        bldgInfo.numApartments = bldgInfo['Before_app']
        bldgInfo.apartmentSize = bldgInfo['Area_round_mode'].astype('int')
        bldgInfo.rent = bldgInfo['Renter_sum'].astype('int')
        bldgInfo.High = bldgInfo['High_discount_sum'].astype('int')
        bldgInfo.Low = bldgInfo['Low_Discount_35_sum'].astype('int')
        bldgInfo.code = bldgInfo['BeforeBldgs'].split(',')
        bldgInfo.project = bldgInfo['ProjNumber']
        currentBldgloop = hedersonly.copy()
        currentBldg = hedersonly.copy()
        for bldItem in bldgInfo.code:
            tempDataSet = pd.DataFrame({'doorIndex': [door for door in range(1, int(bldgInfo.numApartments)+1)],
                                        'min_living_till_2020': bldgInfo['min_living_till_2020'], 'max_living_till_2020': bldgInfo['max_living_till_2020'],
                                        'Average_age_2020': bldgInfo['Average_age_2020'], 'StdDev_age_2020': bldgInfo['StdDev_age_2020']})
            # Age
            AgeDistRandom = np.random.choice(a=self.AgeDistribution['Age'].values, size=bldgInfo.numApartments.astype(
                int), p=self.AgeDistribution['Distribution'].values)
            AgeDistRandomNoise = [np.random.randint(
                age-5, age+5) for age in AgeDistRandom]  # add Some Noise
            tempDataSet['age_'] = AgeDistRandomNoise
            tempDataSet['yearsLivingInBldg'] = tempDataSet.apply(lambda x: np.random.randint(
                x['min_living_till_2020'], x['max_living_till_2020']), axis=1)
            tempDataSet = tempDataSet[[
                'doorIndex', 'age_', 'yearsLivingInBldg']]

            currentBldgloop['doorIndex'] = [
                door for door in range(1, int(bldgInfo.numApartments)+1)]
            currentBldgloop['bldCode'] = bldItem  # Coppy Clean Slate
            currentBldgloop['bldCodeDoorIndex'] = currentBldgloop['bldCode'] + \
                "_"+currentBldgloop['doorIndex'].astype(str)
            currentBldgloop['aprtmentSize'] = bldgInfo.apartmentSize
            currentBldgloop = pd.merge(
                currentBldgloop, tempDataSet, on='doorIndex')
            currentBldgloop['age'] = currentBldgloop['age_']
            currentBldgloop['yearsInBldg'] = currentBldgloop['yearsLivingInBldg']
            currentBldgloop.drop(
                columns=['age_', 'yearsLivingInBldg'], inplace=True)
            currentBldgloop.loc[currentBldgloop.sample(
                bldgInfo.High).index, 'highDiscount'] = 1

            lowdiscountIndex = currentBldgloop.loc[currentBldgloop['highDiscount'].isna(
            )].sample(n=bldgInfo.Low).index
            currentBldgloop.loc[lowdiscountIndex, 'lowDiscount'] = 1
            currentBldgloop['lowDiscount'].fillna(0)
            currentBldgloop['lowDiscount'] = currentBldgloop['lowDiscount'].fillna(
                0)
            currentBldgloop['highDiscount'] = currentBldgloop['highDiscount'].fillna(
                0)
            currentBldgloop.loc[currentBldgloop.query(
                'highDiscount==0 and lowDiscount==0').index, 'noDiscount'] = 1
            currentBldg['noDiscount'] = currentBldgloop['noDiscount'].fillna(
                0)
            # Rent Own
            currentBldgloop['rent'] = 0
            currentBldgloop['own'] = 0
            currentBldgloop['rent'] = currentBldgloop['rent'].astype('int')
            currentBldgloop['own'] = currentBldgloop['own'].astype('int')
            rentIndex = currentBldgloop.sample(n=bldgInfo.rent).index
            currentBldgloop.loc[rentIndex, 'rent'] = 1
            currentBldgloop.loc[currentBldgloop.query(
                'rent==0').index, 'own'] = 1

            currentBldgloop.loc[:, 'ProjNumber'] = bldgInfo.project
            if bldItem == bldgInfo.code[0]:
                currentBldg = currentBldgloop
            else:
                currentBldg = currentBldg.append(currentBldgloop)
                currentBldg.reset_index(inplace=True, drop=True)
            currentBldgloop = hedersonly.copy()

        return currentBldg.copy()
