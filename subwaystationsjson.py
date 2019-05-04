

import pandas as pd

Subway_LIST = {"1":[], "2":[], "3":[], "4":[], "5":[], "6":[], "7":[], "a":[], "c":[], "e":[], "f":[], "b":[], "n":[], "r":[],
               "q":[],"w":[], "m":[], "s":[], "j":[], "z":[], "d":[], "g":[],"l":[], "sir":[]}

df = pd.read_csv('Stations.csv')
for i, row in df.iterrows():
    print (row['Daytime Routes'])
    trains_list = row['Daytime Routes'].split()

    for train in trains_list:
        Subway_LIST[train.lower()].append(row.to_dict())

#dump a json object with the subway beign the key that references an array of stations
import json
with open('SubwayStationJson.json', 'w') as fp:
    json.dump(Subway_LIST, fp)

print(Subway_LIST)