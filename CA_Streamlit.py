import streamlit as st
import pandas as pd
from sodapy import Socrata
import logging
import requests

# Set the title of the app
st.title("Property Tax Data Search")

#subheader below 
st.write('In order to use this application, upload a CSV file with the first column = Parcel ID. This application works for the following counties: Cook County, IL')

# Create a file uploader widget
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    # Read the uploaded CSV file
    df = pd.read_csv(uploaded_file)
    st.write(df)  # Display the uploaded CSV file

    APN = df.iloc[:, 0]
    APN_List = APN.tolist()

    # Cook County, IL API Connection
    def cook_IL(parcel_ids):
        # Define your credentials directly in the script
        app_token = "QQBG9q4gt1NIrzOf0IFuI6oNn"
        username = "aaron@taxproper.com"
        password = "27rmaK*LTwvKcmeJcf!L"

        # Authenticated client for non-public datasets
        client = Socrata(
            "datacatalog.cookcountyil.gov",
            app_token,
            username=username,
            password=password
        )

        # Create a condition string for the API query
        parcel_ids_condition = " OR ".join([f"pin='{pid}'" for pid in parcel_ids])
        tax_year_condition = "(tax_year='2024' OR tax_year IS NULL)"
        where_clause = f"({parcel_ids_condition}) AND {tax_year_condition}"

        # Initialize a flag for the header
        write_header = True

        try:
            # Fetch a chunk of data with filtering
            results = client.get("uzyt-m557", limit=1000, where=where_clause)

            # Convert to pandas DataFrame
            results_df = pd.DataFrame.from_records(results)

            if not results_df.empty:
                # Save the results to a CSV file in append mode
                results_df.to_csv('cook_IL.csv', mode='a', header=write_header, index=False)
                
                # After writing the first chunk, disable header writing
                write_header = False

            st.success("Data has been fetched and saved to cook_IL.csv")
        except requests.exceptions.HTTPError as http_err:
            logging.error(f"HTTP error occurred: {http_err}")
            logging.error(f"Response content: {http_err.response.content}")
            st.error("HTTP error occurred while fetching data.")
        except Exception as err:
            logging.error(f"An error occurred: {err}")
            st.error("An error occurred while fetching data.")

    # Add a button to trigger the API connection and data fetching
    if st.button('Fetch Property Tax Data'):
        cook_IL(APN_List)

    # Read the saved CSV file
    with open('cook_IL.csv', 'rb') as file:
        st.download_button(
            label="Download CSV",
            data=file,
            file_name='cook_IL.csv',
            mime='text/csv'
        )
