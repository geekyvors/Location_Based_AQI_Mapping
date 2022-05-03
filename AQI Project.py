#!/usr/bin/env python
# coding: utf-8

# # IMPORTS

# In[1]:


import requests
import openrouteservice
from openrouteservice import convert
import folium
import json


# ## INPUT
# 1. Take n number of names. (either dynamically or by asking number of locations prior)
# 2. Use geoCoding to get coordinates
# 3. Get AQI scores using coordinates
# 4. Show coordinates which return best AQI score
# 5. Show path between best coordinates and current coordinates/

# # APIs Rejected
# 1. Mapbox
# 2. Google Maps
# 3. TomTom
# 4. PositionStack
# 5. QGIS

# # APIs Used 
# 1. OpenRouteService - For Mapping
# 2. Geocodify - For Geocoding
# 3. AirVisual - For AQI Values
# 

# # MAP FETCH FROM API

# In[2]:


# REVERSE GEOCODING

# latitude = "28.640375217792634" 
# longitude = "77.11536553977894"
# address = "A-701, Fakhruddin Apartments, Dwarka, New Delhi, India"
# reverse_url = f'https://api.geocodify.com/v2/reverse?api_key={token}&lat={latitude}&lng={longitude}'
# rdata = requests.get(reverse_url).json()
# rdata['response']['features'][0]['properties']['label']

# FORWARD GEOCODING 

# address = "A-701, Fakhruddin Apartments, Dwarka, New Delhi, India"
# token = "9c52eceb2898a0d67379b45a0fd961ac32f4c968"
# forward_url = f'https://api.geocodify.com/v2/geocode?api_key={token}&q={address}'
# fdata = requests.get(forward_url).json()
# print(fdata)
# print(fdata['response']['features'][0]['geometry']['coordinates'])
# coordinates are in longitude and latitude form 
# n = (77.0415471227 + 77.0515471227)/2
# print(n) 


# In[3]:


# Returns a 2D array with (longitude,latitude) via forward geocoding 
def forward_geocoding(token, address):
    forward_url = f'https://api.geocodify.com/v2/geocode?api_key={token}&q={address}'
    fdata = requests.get(forward_url).json()
    return fdata['response']['features'][0]['geometry']['coordinates']


# In[4]:


# Returns a rough location string using coordinates 
def reverse_geocoding(token, latitude, longitude):
    reverse_url = f'https://api.geocodify.com/v2/reverse?api_key={token}&lat={latitude}&lng={longitude}'
    rdata = requests.get(reverse_url).json()
    return rdata['response']['features'][0]['properties']['label']


# # AQI FETCH FROM API 

# In[5]:


# country = "India"
# api_url = f'http://api.airvisual.com/v2/states?country={country}&key={api_token}'
# data = requests.get(api_url).json()
# state = "Delhi"
# api_url_for_states = f'http://api.airvisual.com/v2/cities?state={state}&country={country}&key={api_token}'
# latitude = "28.640375217792634" 
# longitude = "77.11536553977894"


# In[6]:


# returns AQI score of the given coordinates
def coordinate_to_AQI(coordinates,aqi_api_token):
    latitude = coordinates[1]
    longitude = coordinates[0]
    api_url_for_coordinates = f'http://api.airvisual.com/v2/nearest_city?lat={latitude}&lon={longitude}&key={aqi_api_token}'
    data = requests.get(api_url_for_coordinates).json()
    return data['data']['current']['pollution']['aqius']


# In[7]:


# return coordinates for the location with best AQI Score
def return_coordinates(current_location, destination, aqi_api_token,map_api_token):
    min_aqi_score = coordinate_to_AQI(forward_geocoding(map_api_token,destination[0]),aqi_api_token)
    final_destination = destination[0]
    for destination_string in destination:
        coordinates = forward_geocoding(map_api_token,destination_string)
        aqi_score = coordinate_to_AQI(coordinates,aqi_api_token)
        if(aqi_score < min_aqi_score):
            min_aqi_score = aqi_score
            final_destination = destination_string
    # this for loop will give us destination string with minimum AQI
    coordinates = forward_geocoding(map_api_token,final_destination)
    # return [final_destination, min_aqi_score]
    return coordinates


# In[8]:


def input_locations():
    current_location = input("Enter current location : ")
    n = int(input("Number of locations : "))
    # Make an Array of Strings
    destination = []
    for i in range(0,n):
        destination_string = input("Enter destination : ")
        destination.append(destination_string) 
    return current_location, destination


# # MAIN FUNCTION 

# In[8]:


aqi_api_token = "8a388fd5-2f11-419d-ae99-e84ca8b65c9b"
map_api_token = "9c52eceb2898a0d67379b45a0fd961ac32f4c968"
# current_location, destination = input_locations()

current_location = "Manav Rachna Campus Rd, Gadakhor Basti Village, Sector 43, Faridabad, Haryana, India"
destination = ["IIT Delhi Main Rd, Hauz Khas, New Delhi, India"," Jaypee Institute of Information Technology, Sector 62, Noida, Uttar Pradesh, India"]

print("current locations : ")
print(current_location)
print("destinations are : ")
print(destination)
current_coords = forward_geocoding(map_api_token,current_location)
final_coords = return_coordinates(current_location, destination, aqi_api_token,map_api_token)
print("Current location coordinates are ", current_coords)
print("Final destination coordinates are ", final_coords)


# In[12]:


client = openrouteservice.Client(key='5b3ce3597851110001cf6248f3bac5667e98430e98f8074943957418')

coords = (current_coords,final_coords)
res = client.directions(coords)
geometry = client.directions(coords)['routes'][0]['geometry']
decoded = convert.decode_polyline(geometry)
distance_txt = "<h4> <b>Distance :&nbsp" + "<strong>"+str(round(res['routes'][0]['summary']['distance']/1000,1))+" Km </strong>" +"</h4></b>"
duration_txt = "<h4> <b>Duration :&nbsp" + "<strong>"+str(round(res['routes'][0]['summary']['duration']/60,1))+" Mins. </strong>" +"</h4></b>"
center_location = [current_coords[1],current_coords[0]]
m = folium.Map(location=center_location,zoom_start=10, control_scale=True)
folium.GeoJson(decoded).add_child(folium.Popup(distance_txt+duration_txt,max_width=300)).add_to(m)

folium.Marker(
    location=list(coords[0][::-1]),
    popup="Galle fort",
    icon=folium.Icon(color="green"),
).add_to(m)

folium.Marker(
    location=list(coords[1][::-1]),
    popup="Jungle beach",
    icon=folium.Icon(color="red"),
).add_to(m)

m.save('map.html')


# In[ ]:




