from google.transit import gtfs_realtime_pb2
import requests
import time # imports module for Epoch/GMT time conversion
import os # imports package for dotenv
from dotenv import load_dotenv, find_dotenv # imports module for dotenv
load_dotenv(find_dotenv()) # loads .env from root directory

# The root directory requires a .env file with API_KEY assigned/defined within
# and dotenv installed from pypi. Get API key from http://datamine.mta.info/user
api_key = '4a204723c21fb518c5c5f47ffe82d519'

#Feeds:

feeds ={'123456s': 'http://datamine.mta.info/mta_esi.php?key={}&feed_id=1'.format(api_key),
        'aceh': 'http://datamine.mta.info/mta_esi.php?key={}&feed_id=26'.format(api_key),
        'nqrw': 'http://datamine.mta.info/mta_esi.php?key={}&feed_id=16'.format(api_key),
        'bdfm': 'http://datamine.mta.info/mta_esi.php?key={}&feed_id=21'.format(api_key),
        'l': 'http://datamine.mta.info/mta_esi.php?key={}&feed_id=2'.format(api_key),
        'g': 'http://datamine.mta.info/mta_esi.php?key={}&feed_id=31'.format(api_key),
        'jz': 'http://datamine.mta.info/mta_esi.php?key={}&feed_id=36'.format(api_key),
        '7': 'http://datamine.mta.info/mta_esi.php?key={}&feed_id=51'.format(api_key),
        }

def feedSelection(train):
    for key, value in feeds.items():
        if train.lower() in key:
            return value

selectedTrainFeeds = map(feedSelection,"f".split())

print(selectedTrainFeeds)
print (feedSelection('n'))
# Requests subway status data feed from City of New York MTA API
feed = gtfs_realtime_pb2.FeedMessage()
response = requests.get('http://datamine.mta.info/mta_esi.php?key={}&feed_id=1'.format(api_key))
feed.ParseFromString(response.content)

# The MTA data feed uses the General Transit Feed Specification (GTFS) which
# is based upon Google's "protocol buffer" data format. While possible to
# manipulate this data natively in python, it is far easier to use the
# "pip install --upgrade gtfs-realtime-bindings" library which can be found on pypi
from protobuf_to_dict import protobuf_to_dict
subway_feed = protobuf_to_dict(feed) # subway_feed is a dictionary
realtime_data = subway_feed['entity'] # train_data is a list



import json

with open('result_station_time.json', 'w') as fp:
    json.dump(realtime_data , fp)

# Because the data feed includes multiple arrival times for a given station
# a global list needs to be created to collect the various times
collected_times = []

# This function takes a converted MTA data feed and a specific station ID and
# loops through various nested dictionaries and lists to (1) filter out active
# trains, (2) search for the given station ID, and (3) append the arrival time
# of any instance of the station ID to the collected_times list
def station_time_lookup(train_data, line, station = True):
    for trains in train_data: # trains are dictionaries
        train_object = {}
        if trains.get('trip_update', False) != False: #active train
            unique_train_schedule = trains['trip_update'] # train_schedule is a dictionary with trip and stop_time_update
            if unique_train_schedule.get('stop_time_update', False) != False and unique_train_schedule['trip']['route_id'] in line: #has a stop time update
                unique_arrival_times = unique_train_schedule['stop_time_update'] # arrival_times is a list of arrivals
                for scheduled_arrivals in unique_arrival_times: #arrivals are dictionaries with time data and stop_ids
                    if ( (scheduled_arrivals.get('stop_id', False) == station) or (station == True and scheduled_arrivals.get('stop_id', False) != False)  ):
                        if scheduled_arrivals.get('arrival', False) != False:
                            time_data = scheduled_arrivals['arrival']
                            unique_time = time_data['time']
                            if unique_time != None:
                                train_object['station'] = scheduled_arrivals['stop_id']
                                train_object['unique_time'] = unique_time
                                train_object['line'] = unique_train_schedule['trip']['route_id']
                                train_object['trip_id'] = unique_train_schedule['trip']['trip_id']
                                collected_times.append(train_object)

# Run the above function for the station ID for Broadway-Lafayette
station_time_lookup(realtime_data,"1")

# Sort the collected times list in chronological order (the times from the data
# feed are in Epoch time format)
#collected_times.sort()

for times in collected_times:
    print(time.localtime(times['unique_time']))
    print(times['line'])
    print(times['station'])

# # Pop off the earliest and second earliest arrival times from the list
# nearest_arrival_time = collected_times[0]
# second_arrival_time = collected_times[1]
#
# # Grab the current time so that you can find out the minutes to arrival
# current_time = int(time.time())
# time_until_train = int(((nearest_arrival_time - current_time) / 60))
#
# # This final part of the code checks the time to arrival and prints a few
# # different messages depending on the circumstance
# if time_until_train > 3:
#     print(f"""
# It's currently {time.strftime("%I:%M %p")}
# The next Brooklyn-bound B/D train from
# Broadway-Lafayette Station arrives in
# {time_until_train} minutes at {time.strftime("%I:%M %p", time.localtime(nearest_arrival_time))}""")
# elif time_until_train <= 0:
#     print(f"""
# Welp... You *just* missed the train. (╯°□°）╯︵ ┻━┻
# Ah well, the next train will arrive at {time.strftime("%I:%M %p", time.localtime(second_arrival_time))}""")
# else:
#     print(f"""
# HURRY UP YOU HAVE {time_until_train} MINUTES TO GET TO
# BROADWAY-LAFAYETTE IF YOU WANT TO GET HOME!
# THE TRAIN GETS IN AT {time.strftime("%I:%M %p", time.localtime(nearest_arrival_time))}""")
#
#
# # These are useful print statments used for script debugging, commented out
# #
# # for times in collected_times:
# #     print(times, "=", time.strftime("%I:%M %p", time.localtime(times)))
# # print(collected_times)
# # print(nearest_arrival_time)
# # print(second_arrival_time)
# # print(time_until_train)