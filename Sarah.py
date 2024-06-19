import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Set the page title and favicon
st.set_page_config(page_title="Sarah Ulrich's Dashboard", page_icon="🌟")

# Header for the dashboard
st.header("Welcome to Sarah Ulrich's Dashboard!")

# Display an image of Hillsboro Village, Nashville
image_url = 'https://vanderbilthustler.com/wp-content/uploads/2022/10/hillsboro-featured-image-Edited.png'
st.image(image_url, caption='Hillsboro Village, Nashville', use_column_width=True)

# OpenWeather API credentials
api_key_weather = '4e7e8ba154896ec1ce4c22939d4112d9'
lat = '36.1627'
lon = '-86.7816'

# Construct the API request URL for weather
url_weather = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key_weather}'

# Fetch the weather data
response_weather = requests.get(url_weather)
weather_data = response_weather.json()

# Extract and convert weather data
kelvin = weather_data['main']['feels_like']
fahrenheit = round((kelvin - 273.15) * 9/5 + 32)
clouds = weather_data['clouds']['all']
wind = round(weather_data['wind']['speed'] * 2.23694)

# Display the weather information in a styled box
st.markdown(
    f"""
    <div style="background-color: #ADD8E6; padding: 10px; border-radius: 10px; border: 1px solid #ddd;">
        <h2 style="color: #333;">Current Weather in Nashville</h2>
        <p style="font-size: 18px; color: #555;">
            The temperature is currently <b>{fahrenheit}°F</b>, the cloud coverage is roughly <b>{clouds}%</b>,
            and the wind speed is <b>{wind} mph</b>.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Function to fetch upcoming events
def get_upcoming_events(api_key, city='Nashville'):
    url_events = 'https://app.ticketmaster.com/discovery/v2/events'
    params = {
        'apikey': api_key,
        'city': city,
        'countryCode': 'US',
        'classificationName': 'Music',
        'size': 10,
        'sort': 'date,asc'
    }
    response_events = requests.get(url_events, params=params)
    if response_events.status_code == 200:
        return response_events.json().get('_embedded', {}).get('events', [])
    else:
        st.error(f"Failed to fetch events. Status code: {response_events.status_code}")
        return []

# Function to format date and time
def format_datetime(date_str, time_str):
    if time_str == 'N/A':
        return date_str, time_str
    dt_str = f"{date_str} {time_str}"
    dt_obj = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
    formatted_date = dt_obj.strftime('%b %d, %Y')
    formatted_time = dt_obj.strftime('%I:%M %p')
    return formatted_date, formatted_time

# Function to get ticket price range
def get_ticket_price_range(event):
    if 'priceRanges' in event:
        price_range = event['priceRanges'][0]
        min_price = price_range.get('min', 'N/A')
        max_price = price_range.get('max', 'N/A')
        currency = price_range.get('currency', '')
        return f"${min_price} - ${max_price} {currency}"
    return "N/A"

# Function to create DataFrame for events
def create_events_dataframe(events):
    event_list = []
    for event in events:
        event_name = event['name']
        event_date = event['dates']['start']['localDate']
        event_time = event['dates']['start'].get('localTime', 'N/A')
        formatted_date, formatted_time = format_datetime(event_date, event_time)
        venue_name = event['_embedded']['venues'][0]['name']
        ticket_price_range = get_ticket_price_range(event)
        event_list.append({
            'Event Name': event_name,
            'Date': formatted_date,
            'Time': formatted_time,
            'Venue': venue_name,
            'Ticket Price': ticket_price_range
        })
    return pd.DataFrame(event_list)

# Streamlit section for upcoming events
st.title("Upcoming Events in Nashville")

api_key_events = 'Yl6fyIP5yKWxtqkdUoFnWGXIFk8aZKNc'

events = get_upcoming_events(api_key_events)

if events:
    events_df = create_events_dataframe(events)
    st.table(events_df.style
             .set_table_styles([
                 {'selector': 'th', 'props': [('font-size', '16px'), ('text-align', 'center')]},
                 {'selector': 'td', 'props': [('font-size', '14px'), ('text-align', 'center')]}
             ])
    )
else:
    st.write("No upcoming events found.")
