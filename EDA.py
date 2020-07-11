import pandas            as pd
import numpy             as np
import matplotlib.pyplot as plt

from copy import deepcopy

class Dataset:
    def __init__(self, data):
        self.data                = data
        self.num_data            = np.shape(self.data)[0]
        self.nan_rows            = []
        self.unique_manufacturer = []

    def missing_value(self, drop_nan = False, export_data = False, name_cleaned = None, name_dropped = None):

        row_nan    = self.data.isna().sum(axis = 1) != 0
        nan_rows   = []
        clean_rows = np.arange(self.num_data).tolist()

        for i in range(self.num_data):
            if row_nan[i] == 1:
                nan_rows.append(i)

        for i in nan_rows:
            clean_rows.remove(i)

        num_row_nan = row_nan.sum()

        print('\nNumber of row with missing value : ' + str(num_row_nan) + '\n')
        print('Missing value by column :')

        dropped_data = self.data.drop(index=clean_rows).reset_index(drop=True)
        dropped_data.to_csv(name_dropped, index=False)

        if drop_nan == True:
            print(self.data.isna().sum())
            self.data     = self.data.drop(index = nan_rows).reset_index(drop = True)
            self.num_data = np.shape(self.data)[0]
            print('Rows with at least one missing value has been omitted')
        else:
            print(self.data.isna().sum())

        if export_data == True:
            self.data.to_csv(name_cleaned, index = False)
            print('File ' + name_cleaned + ' contains cleaned data' )
            print('File ' + name_dropped + ' contains dropped data' )
        print(' ')

        return nan_rows

    def del_mileage_unit(self):
        # We assume that the density of gasoline is 780Kg/m3 or 0.78Kg/l so that km/l = 0.78 * km/kg
        # We want to convert mileage data unit into km/l
        data_mileage = []
        for i in range(self.num_data):
            words = self.data['Mileage'].iloc[i]
            if pd.isna(words):
                mileage_value = np.nan
            else:
                split_words = words.split(' ')
                value       = float(split_words[0])
                unit        =       split_words[1]
                if value == 0:
                    mileage_value = np.nan
                else:
                    mileage_value = value
                    if unit == 'km/kg':
                        mileage_value *= 0.78
            data_mileage.append(mileage_value)
        self.data['Mileage'] = data_mileage
        print('\nUnit of Mileage has been dropped\n')

    def del_units(self, feature):
        new_values = []
        for i in range(self.num_data):
            words = self.data[feature].iloc[i]
            if pd.isna(words):
                value = np.nan
            else:
                split_words = words.split(' ')
                value       = split_words[0]
                unit        = split_words[1]
                if value in ['null','nan','Nan','NaN','none','Null','',' ']:
                    value = np.nan
                else:
                    value = float(value)
                    if value == 0:
                        value = np.nan
            new_values.append(value)

        print('\nUnit of ' + feature + ' has been dropped\n')

        self.data[feature] = new_values

    def add_manufacturer(self):

        manufacturer = []

        for i in range(self.num_data):
            name = self.data.Name[i].split()[0]
            if name == 'ISUZU':
                name = 'Isuzu'
            manufacturer.append(name)

        self.data['Manufacturer'] = manufacturer

        self.unique_manufacturer = self.data.Manufacturer.unique()
        num_unique_manufacturer  = len(self.unique_manufacturer)

        print('\nNew manufacturer column added, which consists of ' + str(num_unique_manufacturer) + ' manufacturers.')
        print(self.unique_manufacturer)
        print()

    def count_manufacturer(self, export_data = False):

        manufacturer_count = self.data.Manufacturer.value_counts()
        manufacturer_count = pd.DataFrame({'Manufacturer': manufacturer_count.index, 'Count': manufacturer_count.values})

        print('\nNumber of car by manufacturer')
        print(manufacturer_count)

        if export_data == True:
            manufacturer_count.to_csv('jawaban_soal_1.csv', index = False)
            print('Output has been saved at jawaban_soal_1.csv\n')

        return(manufacturer_count)

    def count_used_per_city(self, export_data = False):

        dataset_used = deepcopy(self.data)
        drop_index   = []

        for i in range(self.num_data):
            if self.data.Owner_Type.iloc[i]  == 'First':
                drop_index.append(i)

        dataset_used   = dataset_used.drop(index = drop_index).reset_index(drop = True)
        location_count = dataset_used.Location.value_counts()
        location_count = pd.DataFrame({'Location': location_count.index, 'Count': location_count.values})

        print('\nCity with most secondhand car is : ' + str(location_count.iloc[0, 0]))
        print('Below is shown the number of used car per location')
        print(location_count)
        if export_data == True:
            location_count.to_csv('jawaban_soal_2.csv', index = False)
            print('Output has been saved at jawaban_soal_2.csv')
        print()

        return(location_count)

    def count_not_first(self, exclude_wear ='First'):

        dataset_used = deepcopy(self.data)
        drop_index = []

        for i, owner_type in enumerate(self.data.Owner_Type):
            if owner_type in exclude_wear:
                drop_index.append(i)

        dataset_used   = dataset_used.drop(index = drop_index).reset_index(drop = True)
        count_criteria = np.shape(dataset_used)[0]

        print('\nThe number of cars that is not ', end = '')
        for i, item in enumerate(exclude_wear):
            if i != len(exclude_wear) - 1:
                print(item, end = ' and ')
            else:
                print(item, end = ' ')
        print('ownership is ' + str(count_criteria) + '\n')

    def count_mileage_per_fuel(self, export_data = False, name = None):

        unique_fuel  = list(self.data['Fuel_Type'].unique())
        mean_mileage = []

        for i in unique_fuel:
            current_mean = self.data.loc[self.data.Fuel_Type == i].Mileage.mean()
            mean_mileage.append(current_mean)

        fuel_mileage                 = pd.DataFrame()
        fuel_mileage['fuel']         = unique_fuel
        fuel_mileage['mean_mileage'] = mean_mileage
        fuel_mileage                 = fuel_mileage.sort_values('mean_mileage', ascending = False)

        print('\nFuel with lowest mileage value is ' + fuel_mileage.iloc[-1, 0] + ' with mean mileage of ' + str(fuel_mileage.iloc[-1, 1]))
        print(fuel_mileage)

        if export_data == True:
            fuel_mileage.to_csv(name)

        print()

    def plot_dist(self, feature, partitions = 22, export_data = False, name = None):

        data_hist = self.data[feature]

        if export_data == True:
            freq_dist = data_hist.value_counts()
            freq_dist = pd.DataFrame({feature : freq_dist.index, 'count' : freq_dist.values}, dtype= float)
            freq_dist = freq_dist.sort_values(feature, axis = 0)
            freq_dist.to_csv(name, index=False)
            print('\nAnswer ' + name + ' has been saved.\n')

        plt.hist(data_hist, bins = partitions)
        plt.title('The histogram of ' + feature)
        plt.xlabel('Years')
        plt.ylabel('Frequency')
        plt.show()

    def plot_scatter(self, feature1, feature2):
        data_x = self.data[feature1]
        data_y = self.data[feature2]

        plt.scatter(data_x,data_y)
        plt.title('The scatter plot of ' + feature1 + ' and ' + feature2)
        plt.xlabel(feature1)
        plt.ylabel(feature2)
        plt.show()

    def dist_below(self, x = 50000):

        dist_below_x = (self.data.Kilometers_Driven < x).sum()
        print('\nThe number of cars with distance traveled below ' + str(x) + ' KM is : ' + str(dist_below_x) + '\n')
        return dist_below_x