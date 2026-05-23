import streamlit as st
import requests
from bs4 import BeautifulSoup

# Setup page configuration
st.set_page_config(page_title="Fuel Cost Calculator", page_icon="⛽", layout="centered")

st.title("⛽ Kerala Fuel Cost Calculator")

# Access API key from secrets
try:
    API_KEY = st.secrets["OPENROUTE_API_KEY"]
except Exception:
    st.error("API Key not found in secrets. Please configure .streamlit/secrets.toml")
    st.stop()

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_fuel_price(fuel_type, district):
    url = f"https://www.v3cars.com/kerala/{fuel_type}-price-in-{district.lower()}"
    try:
        source = requests.get(url).text
        soup = BeautifulSoup(source, "lxml")
        price_elem = soup.find("span", class_="fPrice")
        if price_elem:
            return float(price_elem.text.strip())
        return None
    except Exception as e:
        return None

@st.cache_data(ttl=3600)
def get_min_max_prices(fuel_type):
    url = f"https://www.v3cars.com/kerala/{fuel_type}-price"
    try:
        source = requests.get(url).text
        soup = BeautifulSoup(source, "lxml")
        fmax = 0.0
        fmin = 300.0
        maxplace = ""
        minplace = ""
        
        table = soup.find("tbody", class_="ftable")
        if not table: return None, None, None, None
        
        prices = table.find_all("tr")
        for i in prices:
            price_td = i.find("td", class_="td-price-width")
            state_td = i.find("td", class_="state-td-width first-col")
            if price_td and state_td:
                price_text = price_td.text.strip()
                price_value = float(price_text.replace("₹", "").replace("/L", "").strip())
                
                if price_value > fmax:
                    fmax = price_value
                    maxplace = state_td.text.strip()
                if price_value < fmin:
                    fmin = price_value
                    minplace = state_td.text.strip()
        return fmin, minplace, fmax, maxplace
    except Exception as e:
        return None, None, None, None

@st.cache_data
def get_coordinates(place_name):
    url = "https://api.openrouteservice.org/geocode/search"
    params = {"api_key": API_KEY, "text": place_name}
    try:
        r = requests.get(url, params=params)
        data = r.json()
        if not data.get('features'):
            return None
        lon, lat = data['features'][0]['geometry']['coordinates']
        return [lon, lat]
    except Exception:
        return None

@st.cache_data
def get_distance(start_coords, end_coords):
    url = "https://api.openrouteservice.org/v2/directions/driving-car"
    body = {"coordinates": [start_coords, end_coords]}
    headers = {"Authorization": API_KEY, "Content-Type": "application/json"}
    try:
        r = requests.post(url, json=body, headers=headers)
        data = r.json()
        summary = data['routes'][0]['summary']
        distance_km = summary['distance'] / 1000
        duration_hr = summary['duration'] / 3600
        return distance_km, duration_hr
    except Exception:
        return None, None

# Sidebar navigation
app_mode = st.sidebar.radio("Choose the calculator:", ["Monthly Fuel Cost", "Trip Fuel Cost"])

if app_mode == "Monthly Fuel Cost":
    st.header("Monthly Fuel Cost Calculator")
    
    with st.form("monthly_form"):
        district = st.text_input("Enter your district (e.g., Ernakulam)")
        fuel_choice = st.radio("Select your fuel type", ["Petrol", "Diesel"], horizontal=True)
        distance = st.number_input("Enter monthly distance (km)", min_value=0.0, step=10.0)
        mileage = st.number_input("Enter vehicle mileage (km/L)", min_value=1.0, step=1.0)
        
        submitted = st.form_submit_button("Calculate Monthly Cost")
        
    if submitted:
        if not district:
            st.warning("Please enter a district.")
        else:
            fuel_type = fuel_choice.lower()
            with st.spinner("Fetching fuel prices..."):
                fuelprice = get_fuel_price(fuel_type, district)
                
            if fuelprice:
                st.success(f"Current {fuel_choice} price in {district}: **₹{fuelprice}**")
                
                liters_req = distance / mileage
                total_cost = liters_req * fuelprice
                
                col1, col2 = st.columns(2)
                col1.metric("Liters Required", f"{liters_req:.2f} L")
                col2.metric("Total Monthly Cost", f"₹{total_cost:.2f}")
                
                st.markdown("---")
                st.subheader("Kerala Price Analytics")
                with st.spinner("Analyzing statewide prices..."):
                    fmin, minplace, fmax, maxplace = get_min_max_prices(fuel_type)
                    
                if fmin and fmax:
                    col3, col4 = st.columns(2)
                    col3.info(f"**Lowest Price:** ₹{fmin} (in {minplace})")
                    col4.error(f"**Highest Price:** ₹{fmax} (in {maxplace})")
                else:
                    st.warning("Could not fetch statewide price analytics.")
            else:
                st.error("Could not fetch fuel price for the given district. Please check the spelling.")

elif app_mode == "Trip Fuel Cost":
    st.header("Trip Fuel Cost Calculator")
    
    st.subheader("Starting Location")
    col1, col2, col3 = st.columns(3)
    scity = col1.text_input("City", key="scity")
    sdistrict = col2.text_input("District", key="sdistrict")
    sstate = col3.text_input("State", value="Kerala", key="sstate")
    
    st.subheader("Destination Location")
    col4, col5, col6 = st.columns(3)
    dcity = col4.text_input("City", key="dcity")
    ddistrict = col5.text_input("District", key="ddistrict")
    dstate = col6.text_input("State", value="Kerala", key="dstate")
    
    st.subheader("Vehicle Details")
    col7, col8 = st.columns(2)
    fuel_choice = col7.radio("Select fuel type", ["Petrol", "Diesel"], horizontal=True, key="trip_fuel")
    mileage = col8.number_input("Vehicle mileage (km/L)", min_value=1.0, step=1.0, key="trip_mileage")
    
    calculate_trip = st.button("Calculate Trip Cost")
    
    if calculate_trip:
        if not (scity and sdistrict and sstate and dcity and ddistrict and dstate):
            st.warning("Please fill in all location fields.")
        else:
            start_place = f"{scity} {sdistrict} {sstate}"
            end_place = f"{dcity} {ddistrict} {dstate}"
            
            with st.spinner("Calculating route distance..."):
                start_coords = get_coordinates(start_place)
                end_coords = get_coordinates(end_place)
                
                if start_coords and end_coords:
                    distance_km, duration_hr = get_distance(start_coords, end_coords)
                    
                    if distance_km and duration_hr:
                        st.success(f"**Road distance from {scity} to {dcity}:** {distance_km:.2f} km")
                        st.info(f"**Estimated travel time:** {duration_hr:.2f} hours")
                        
                        fuel_type = fuel_choice.lower()
                        with st.spinner("Fetching fuel price..."):
                            fuelprice = get_fuel_price(fuel_type, sdistrict)
                            
                        if fuelprice:
                            st.write(f"Current {fuel_choice} price in {sdistrict}: **₹{fuelprice}**")
                            liters_req = distance_km / mileage
                            total_cost = liters_req * fuelprice
                            
                            metrics_col1, metrics_col2 = st.columns(2)
                            metrics_col1.metric("Liters Required", f"{liters_req:.2f} L")
                            metrics_col2.metric("Total Trip Cost", f"₹{total_cost:.2f}")
                        else:
                            st.error(f"Could not fetch {fuel_choice} price for {sdistrict}.")
                    else:
                        st.error("Could not calculate driving route between these locations.")
                else:
                    st.error("Could not find coordinates for the provided locations. Please verify the city/district names.")
