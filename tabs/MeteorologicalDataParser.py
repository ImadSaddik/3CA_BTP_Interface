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
    API_KEY = '3nlkiduDWKW3Az0uqE9d6eh4OCqFRM9_'
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    
    duration = "P31D"
    format_ = "json"
    time_zone = "utc"
    output_parameters = "air_temp,albedo,azimuth,clearsky_dhi,clearsky_dni,clearsky_ghi,clearsky_gti,cloud_opacity,dewpoint_temp,dhi,dni,ghi,gti,precipitable_water,precipitation_rate,relative_humidity,surface_pressure,wind_direction_100m,wind_direction_10m,wind_speed_100m,wind_speed_10m,zenith"
    
    responses = []
    for date in date_range:
        start = f"{date.strftime('%Y-%m-%d')}T00:00:00.000Z"
        url = f"https://api.solcast.com.au/data/historic/radiation_and_weather?latitude={latitude}&longitude={longitude}&start={start}&duration={duration}&format={format_}&time_zone={time_zone}&output_parameters={output_parameters}"

        response = requests.get(url, headers=headers)
        responses.append(response)
        
    try:
        meteo_df = parse_meteo_data(responses)
        preprocessed_meteo_df = preprocess_data(meteo_df)
        preprocessed_meteo_df = add_day_month_year(preprocessed_meteo_df)
        
        return preprocessed_meteo_df
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

    df['day'] = df['date'].dt.day
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year

    return df


def preprocess_data(df):
    df['date'] = pd.to_datetime(df['date'], utc=True)
    df['date'] = df['date'].dt.strftime('%d-%m-%Y')
    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')

    df.set_index('date', inplace=True)
    
    columns = list(df.columns)[:-1]
    agg_dict = {col: ['mean', 'std', 'min', q1, q2, q3, 'max'] for col in columns}

    df_resampled = df.resample('D').agg(agg_dict)
    df_resampled = df_resampled.reset_index()

    df_resampled.columns = [
        '_'.join(col).strip() for col in df_resampled.columns.values]
    
    df_resampled.rename(columns={'date_': 'date'}, inplace=True)
    
    return df_resampled

    
def q1(x):
    return x.quantile(0.25)


def q2(x):
    return x.quantile(0.50)


def q3(x):
    return x.quantile(0.75)
