import requests

import pandas as pd
import streamlit as st


def get_meteorological_data(start_date, end_date, latitude, longitude):
    start_month = pd.to_datetime(start_date, format='%Y%m%d').to_period('M').start_time
    end_month = pd.to_datetime(end_date, format='%Y%m%d').to_period('M').start_time
    date_range = pd.date_range(start=start_month, end=end_month, freq='MS')
    
    df = call_solcast_api(date_range, latitude, longitude)
    if df is not None:
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
        return df
    
    return None
    
    
def call_solcast_api(date_range, latitude, longitude):
    # API_KEY = '3nlkiduDWKW3Az0uqE9d6eh4OCqFRM9_'
    API_KEY = 'iJduZRhJN6HooniHwU5o_jwYcFMQ9qcQ'
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    
    duration = "P31D"
    format_ = "json"
    time_zone = "utc"
    output_parameters = "air_temp,dewpoint_temp,relative_humidity,surface_pressure,dni,dhi,wind_direction_10m,wind_speed_100m"
    
    responses = []
    for date in date_range:
        start = f"{date.strftime('%Y-%m-%d')}T00:00:00.000Z"
        url = f"https://api.solcast.com.au/data/historic/radiation_and_weather?latitude={latitude}&longitude={longitude}&start={start}&duration={duration}&format={format_}&time_zone={time_zone}&output_parameters={output_parameters}"

        response = requests.get(url, headers=headers)
        responses.append(response)
        
    try:
        meteo_df = parse_meteo_data(responses)
        meteo_df = convert_to_month(meteo_df)
        meteo_df = rename_columns(meteo_df)
        meteo_df = add_day_month_year(meteo_df)
        meteo_df = handle_units(meteo_df)
        
        return meteo_df
    except:
        st.error('An error occurred while fetching the meteo data, check the validity of the API Key.')
        return None
    
    
def parse_meteo_data(responses):
    df = pd.DataFrame()

    for response in responses:
        df = pd.concat(
            [df, pd.DataFrame(response.json()['estimated_actuals'])])
        
    df = df.reset_index(drop=True)
    df.rename(columns={'period_end': 'date'}, inplace=True)
    df.drop(columns=['period'], inplace=True)
    
    return df


def add_day_month_year(df):
    df['date'] = pd.to_datetime(df['date'])

    df['Day'] = df['date'].dt.day
    df['Month'] = df['date'].dt.month

    return df


def convert_to_month(df):
    df['date'] = pd.to_datetime(df['date'], utc=True)
    df['date'] = df['date'].dt.strftime('%d-%m-%Y')
    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')

    df.set_index('date', inplace=True)
    df_resampled = df.resample('D').mean()
    df_resampled.reset_index(inplace=True)
    
    return df_resampled


def rename_columns(df):
    df.rename(columns={
        'air_temp': 'Dry Bulb Temperature',
        'dewpoint_temp': 'Dew Point Temperature',
        'relative_humidity': 'Relative Humidity',
        'surface_pressure': 'Atmospheric Station Pressure',
        'dhi': 'Diffuse Horizontal Illuminance',
        'dni': 'Direct Normal Illuminance',
        'wind_direction_10m': 'Wind Direction',
        'wind_speed_100m': 'Wind Speed'
    }, inplace=True)
    
    return df


def handle_units(df):
    df['Atmospheric Station Pressure'] = df['Atmospheric Station Pressure'] * 100
    
    return df
