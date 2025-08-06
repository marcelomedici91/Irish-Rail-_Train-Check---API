#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import requests
import pandas as pd
import xmltodict
from datetime import datetime


def get_station_data(station_name):
    url = f'https://api.irishrail.ie/realtime/realtime.asmx/getStationDataByNameXML?StationDesc={station_name}'
    response = requests.get(url)
    if response.status_code == 200 and response.content.strip().startswith(b'<?xml'):
        data = xmltodict.parse(response.content)
        station_data = data['ArrayOfObjStationData']['objStationData']
 
        if isinstance(station_data, dict):
            station_data = [station_data]
        return pd.DataFrame(station_data)
    else:
        print(f"Error'{station_name}'.")
        return None


def get_train_movements(train_id, train_date):
    url = f'https://api.irishrail.ie/realtime/realtime.asmx/getTrainMovementsXML?TrainId={train_id}&TrainDate={train_date}'
    response = requests.get(url)
    if response.status_code == 200 and response.content.strip().startswith(b'<?xml'):
        data = xmltodict.parse(response.content)
        movements = data['ArrayOfObjTrainMovements']['objTrainMovements']
        if isinstance(movements, dict):
            movements = [movements]
        return pd.DataFrame(movements)
    else:
        print("Error.")
        return None


def plan_route(origin, destination, train_date, expected_departure):
    df_origin = get_station_data(origin)

    if df_origin is None or df_origin.empty:
        print("No train found in the deperture station.")
        return

    expected_time = datetime.strptime(expected_departure, '%H:%M')

    df_origin['Expdepart_dt'] = pd.to_datetime(df_origin['Expdepart'], format='%H:%M')

    df_filtered = df_origin[df_origin['Expdepart_dt'] >= expected_time]

    if df_filtered.empty:
        print("None departure after the expected time.")
        return

    print("\nTrains Available:")
    print(df_filtered[['Traincode', 'Expdepart', 'Destination', 'Status']])

    
    for _, row in df_filtered.iterrows():
        train_id = row['Traincode']
        train_destination = row['Destination']

        print(f"\nVerifying train {train_id} destination to {train_destination}...")

        if destination.lower() in train_destination.lower():
            print(f"O train {train_id} goes direct {destination}!")
            return 

        movements_df = get_train_movements(train_id, train_date)

        if movements_df is not None and not movements_df.empty:
            if destination in movements_df['LocationFullName'].values:
                print(f"The Train {train_id} pass by {destination}!")
                return

    print("No train found that goes to the specified destination.")


def get_input():
    origin = input("Origen: ")
    destination = input("Destination_Station: ")
    train_date = input("Date (DD MMM YYYY): ")
    expected_departure = input("Deperture Time (HH:MM): ")
    return origin, destination, train_date, expected_departure


if __name__ == "__main__":
    origin, destination, train_date, expected_departure = get_input()
    plan_route(origin, destination, train_date, expected_departure)


# In[ ]:




