import requests
from bs4 import BeautifulSoup

import os

API_KEY = os.environ.get("OPENROUTE_API_KEY")
if not API_KEY:
    print("❌ OPENROUTE_API_KEY environment variable not set.")
    exit()

def get_coordinates(place_name):
    url = "https://api.openrouteservice.org/geocode/search"
    params = {"api_key": API_KEY, "text": place_name}
    r = requests.get(url, params=params)
    data = r.json()
    if not data['features']:
        return None
    lon, lat = data['features'][0]['geometry']['coordinates']
    return [lon, lat]   # IMPORTANT: [longitude, latitude]

def get_distance(start_coords, end_coords):
    url = "https://api.openrouteservice.org/v2/directions/driving-car"
    body = {"coordinates": [start_coords, end_coords]}
    headers = {"Authorization": API_KEY, "Content-Type": "application/json"}
    r = requests.post(url, json=body, headers=headers)
    data = r.json()

    try:
        # Use 'routes' → 'summary'
        summary = data['routes'][0]['summary']
        distance_km = summary['distance'] / 1000
        duration_hr = summary['duration'] / 3600
        return distance_km, duration_hr
    except (KeyError, IndexError):
        print("❌ Could not parse route data. Full response:")
        print(data)
        return None, None
# --- Main Program ---
print("Please enter in the format (city , district , state)")
print("Enter Starting location")
scity = input("Enter city: ")
sdistrict = input("Enter district: ")
sstate = input("Enter state: ")

print("Enter Destiantion location")
dcity = input("Enter city: ")
ddistrict = input("Enter district: ")
dstate = input("Enter state: ")


start_place = scity + " " + sdistrict + " " + sstate
end_place = dcity + " " + ddistrict + " " + dstate

start_coords = get_coordinates(start_place)
end_coords = get_coordinates(end_place)

if start_coords and end_coords:
    distance, duration = get_distance(start_coords, end_coords)
    if distance and duration:
        print(f"✅ Road distance from {start_place} to {end_place}: {distance:.2f} km")
        print(f"🕒 Estimated travel time: {duration:.2f} hours")
    else:
        print("❌ Could not calculate distance.")
        exit()
else:
    print("❌ Invalid input. Please try again with correct city names.")
    exit()

fuels = ["petrol","diesel"]
choice = int(input("Select your fuel type 1)Petrol 2)Diesel : "))
print("\n")
mileage = float(input("Enter vehicle mileage(km/L) : "))
print("\n")
if choice == 1:
    fuel = fuels[0]
    source = requests.get("https://www.v3cars.com/kerala/petrol-price"+"-in-"+sdistrict).text
    soup = BeautifulSoup(source,"lxml")
    #print(soup)
elif choice == 2:
    fuel = fuels[1]
    source = requests.get("https://www.v3cars.com/kerala/diesel-price"+"-in-"+sdistrict).text
    soup = BeautifulSoup(source,"lxml")
else:
    print("Invalid chocie")
    exit()
fuelprice = float((soup.find("span",class_="fPrice").text).strip())
print("Current fuel price for ",fuel," = ",fuelprice)
print("Liters of ",fuel," required = ",distance/mileage)
print("Total cost = ",(distance/mileage)*fuelprice)
print("\n")