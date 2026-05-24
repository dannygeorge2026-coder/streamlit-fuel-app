import requests
from bs4 import BeautifulSoup
import csv
district = input("Enter your district : ")
print("\n")
fuels = ["petrol","diesel"]
choice = int(input("Select your fuel type 1)Petrol 2)Diesel : "))
print("\n")
distance = float(input("Enter monthly distance(km) : "))
print("\n")
mileage = float(input("Enter vehicle mileage(km/L) : "))
print("\n")
if choice == 1:
    fuel = fuels[0]
    source = requests.get("https://www.v3cars.com/kerala/petrol-price"+"-in-"+district).text
    soup = BeautifulSoup(source,"lxml")
    #print(soup)
elif choice == 2:
    fuel = fuels[1]
    source = requests.get("https://www.v3cars.com/kerala/diesel-price"+"-in-"+district).text
    soup = BeautifulSoup(source,"lxml")
else:
    print("Invalid chocie")
    exit()

fuelprice = float((soup.find("span",class_="fPrice").text).strip())
print("Current fuel price for ",fuel," = ",fuelprice)
print("Liters of ",fuel," required = ",distance/mileage)
print("Total cost = ",(distance/mileage)*fuelprice)
print("\n")
source = requests.get("https://www.v3cars.com/kerala/"+fuel+"-price").text
soup = BeautifulSoup(source,"lxml")
fmax = 0.0
fmin = 300.0
maxplace = ""
minplace = ""
prices = soup.find("tbody",class_="ftable").find_all("tr")
#print(prices)
for i in prices:
    price_text = i.find("td", class_="td-price-width").text.strip()
    # Remove ₹ and /L
    price_value = float(price_text.replace("₹", "").replace("/L", "").strip())

    if price_value > fmax:
        fmax = price_value
        maxplace = i.find("td", class_="state-td-width first-col").text.strip()

    if price_value < fmin:
        fmin = price_value
        minplace = i.find("td", class_="state-td-width first-col").text.strip()
print("Lowest price for ",fuel," = ",fmin)
print(minplace)
print("\n")
print("Highest price for ",fuel," = ",fmax)
print(maxplace)



