import streamlit as st
import pandas as pd
from sodapy import Socrata
from datetime import datetime
import os
from bs4 import BeautifulSoup as soup
import requests


current_year = datetime.now().year
previous_year = current_year - 1

# Socrata API credentials
app_token = "QQBG9q4gt1NIrzOf0IFuI6oNn"
username = "aaron@taxproper.com"
password = "27rmaK*LTwvKcmeJcf!L"

# Set the title of the app
st.title("Property Tax Data Search")

st.markdown("""
        This app allows you to fetch property tax data from counties using APNs. <br> <br>
        **Directions**: Upload a CSV file with APNs in the first column and the county name in the second column. Click the button to fetch the data. <br>
         """, unsafe_allow_html=True)

st.markdown("""The following counties are supported: <br>
            **Cook County, IL** <br>
            **Maricopa County, AZ**""", unsafe_allow_html=True)

# Create a file uploader and convert the file into a dataframe
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    # Read the uploaded CSV file
    df = pd.read_csv(uploaded_file)
    st.write(df)  # Display the uploaded CSV file

    APN = df.iloc[:, 0]
    APN_List = APN.tolist()

    # Cook County, IL API Connection
    def cook_IL(parcel_ids):
        # Generate a unique filename based on the current date and time
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Results_{timestamp}.csv"
      
        # Authenticated client for non-public datasets
        client = Socrata(
            "datacatalog.cookcountyil.gov",
            app_token,
            username=username,
            password=password
        )

        # Create a condition string for the API query
        parcel_ids_condition = " OR ".join([f"pin='{pid}'" for pid in parcel_ids])
        tax_year_condition = f"(tax_year='{current_year}' OR tax_year='{previous_year}')"
        where_clause = f"({parcel_ids_condition}) AND {tax_year_condition}"

        try:
            # Fetch a chunk of data with filtering
            results = client.get("uzyt-m557", limit=1000, where=where_clause)

            # Convert to pandas DataFrame
            results_df = pd.DataFrame.from_records(results)

            if not results_df.empty:
                # Save the results to a CSV file
                results_df.to_csv(filename, index=False)
                st.success(f"Data has been fetched and saved to {filename}")
                return filename
            else:
                st.error("No data found for the given APNs.")
                return None
        except Exception as e:
            st.error(f"An error occurred while fetching data: {e}")
            return None

    #Maricopa, AZ API Connection 
    def maricopa_AZ(parcel_ids):
        # Generate a unique filename based on the current date and time
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Results_{timestamp}.csv"
        
        #API Token 
        token = '7df3c7e8-4674-4f40-8f61-c34dfb7e9a90'
    
        
        #Headers for API 
        headers = {
            'Authorization': token,
            'User-Agent': 'Null'
        }
        
        all_results = []
        
        for parcel in parcel_ids:
            url = f'https://mcassessor.maricopa.gov/parcel/{parcel}/propertyinfo'
            try:
                # Fetch data for each parcel
                response = requests.get(url, headers=headers)
                response.raise_for_status()  # Raise an HTTPError for bad responses
                parcel_data = response.json()
                all_results.append(parcel_data)
            except requests.exceptions.RequestException as e:
                st.error(f"An error occurred while fetching data for parcel {parcel}: {e}")
        
        # Convert the list of results to a DataFrame
        if all_results:
            results_df = pd.json_normalize(all_results)
            # Save the results to a CSV file
            results_df.to_csv(filename, index=False)
            st.success(f"Data has been fetched and saved to {filename}")
            return filename
        else:
            st.error("No data found for the given APNs.")
            return None

    
    # Cook, IL Button 
    if 'Cook' in df.iloc[:, 1].values:
        # Display Button to fetch Cook, IL Property Tax Data
        if st.button('Fetch Cook, IL Property Tax Data'):
            generated_filename = cook_IL(APN_List)

            # Provide a download button for the newly created file if it exists
            if generated_filename and os.path.exists(generated_filename):
                with open(generated_filename, 'rb') as file:
                    st.download_button(
                        label="Download CSV",
                        data=file,
                        file_name=generated_filename,
                        mime='text/csv'
                    )
    
    
    
    #Maricopa, AZ Button 
    if 'Maricopa' in df.iloc[:,1].values:
        #Display button to fetch Marciopa, AZ Property Tax Data 
        if st.button('Fetch Maricopa, AZ Property Tax Data'):
            generated_filename = maricopa_AZ(APN_List)

            # Provide a download button for the newly created file if it exists
            if generated_filename and os.path.exists(generated_filename):
                with open(generated_filename, 'rb') as file:
                    st.download_button(
                        label="Download CSV",
                        data=file,
                        file_name=generated_filename,
                        mime='text/csv'
                    )

else:
    st.info("No file uploaded.")



