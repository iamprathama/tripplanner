import requests

from dotenv import load_dotenv
import os

load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
UNSPLASH_KEY = os.getenv("UNSPLASH_KEY")

from datetime import datetime

def get_city_image(destination):
    url = "https://api.unsplash.com/search/photos"
    params = {
        "query": f"{destination} city travel",
        "client_id": UNSPLASH_KEY,
        "per_page": 3
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print("Unsplash API error:", response.text)
        return "https://via.placeholder.com/600x400?text=Image+Unavailable"

    data = response.json()
    if data.get("results"):
        return data["results"][0]["urls"]["regular"]
    else:
        return "https://via.placeholder.com/600x400?text=No+Image+Found"

def fetch_attractions(location_id):
    url = "https://travel-advisor.p.rapidapi.com/attractions/list"
    querystring = {
        "location_id": location_id,
        "currency": "INR",
        "lang": "en_IN",
        "lunit": "km",
        "limit": "5"
    }
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "travel-advisor.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    print("Attractions Status Code:", response.status_code)
    if response.status_code != 200:
        print("Attractions API error:", response.text)
        return []

    data = response.json()
    attractions = []
    for item in data.get("data", []):
        if "name" in item:
            attractions.append({
                "name": item.get("name"),
                "description": item.get("description", "No description available"),
                "image": item.get("photo", {}).get("images", {}).get("original", {}).get("url", "https://via.placeholder.com/300x200?text=No+Image")
            })

    return attractions

def get_location_id(city):
    url = "https://travel-advisor.p.rapidapi.com/locations/search"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "travel-advisor.p.rapidapi.com"
    }
    params = {
        "query": city,
        "limit": "1",
        "offset": "0",
        "units": "km",
        "currency": "INR",
        "sort": "relevance",
        "lang": "en_US"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        location_id = data['data'][0]['result_object']['location_id']
        print(f"✅ City: {city}, location_id: {location_id}")
        return location_id
    except Exception as e:
        print(f"❌ Error fetching location ID for {city}: {e}")
        return None
import requests

def fetch_hotels(location_id):
    url = "https://travel-advisor.p.rapidapi.com/hotels/list"
    querystring = {
        "location_id": location_id,
        "adults": "2",
        "currency": "INR",
        "lang": "en_US",
        "nights": "1",
        "offset": "0",
        "order": "asc",
        "limit": "5",
        "sort": "recommended"
    }
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "travel-advisor.p.rapidapi.com"
    }

    hotels = []

    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=10)
        response.raise_for_status()
        data = response.json()

        for hotel in data.get("data", []):
           
            if isinstance(hotel, dict) and hotel.get("name"):
                hotels.append({
                    "name": hotel.get("name", "N/A"),
                    "price": hotel.get("price", {}).get("display", "N/A") 
                              if isinstance(hotel.get("price"), dict) else "N/A",
                    "image": hotel.get("photo", {}).get("images", {}).get("large", {}).get(
                        "url", "https://via.placeholder.com/300x200?text=No+Image"
                    ) if isinstance(hotel.get("photo"), dict) else "https://via.placeholder.com/300x200?text=No+Image",
                    "rating": hotel.get("rating", "N/A"),
                    "address": hotel.get("address", "N/A")
                })

        # ✅ Fallback dummy data if no hotels found
        if not hotels:
            hotels = [
                {
                    "name": "Sunrise Palace",
                    "price": "₹2,500",
                    "image": "https://images.unsplash.com/photo-1576671081837-d2f6f8b6e9d3?auto=format&fit=crop&w=800&q=80",
                    "rating": "4.3",
                    "address": "MG Road, Jaipur"
                },
                {
                    "name": "Ocean View Resort",
                    "price": "₹3,200",
                    "image": "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=800&q=80",
                    "rating": "4.7",
                    "address": "Beach Road, Goa"
                },
                {
                    "name": "Green Valley Inn",
                    "price": "₹1,800",
                    "image": "https://images.unsplash.com/photo-1501117716987-c8e01f3aee50?auto=format&fit=crop&w=800&q=80",
                    "rating": "4.0",
                    "address": "Nainital Lakeview"
                },
                {
                    "name": "Royal Heritage Hotel",
                    "price": "₹2,900",
                    "image": "https://images.unsplash.com/photo-1584132967334-10e028bd69f7?auto=format&fit=crop&w=800&q=80",
                    "rating": "4.6",
                    "address": "City Palace Road, Udaipur"
                }
            ]

    except requests.exceptions.RequestException as e:
        print(f"❌ Hotel Fetch Request Error: {e}")

    except Exception as e:
        print(f"❌ Unexpected Hotel Fetch Error: {e}")

    return hotels

    


FLIGHT_API_HOST = "aerodatabox.p.rapidapi.com"

def get_flight_details(source, destination, date):
    try:
        url = f"https://aerodatabox.p.rapidapi.com/flights/airports/icao/{source}/{date}T00:00/{date}T12:00"
        params = {
            "direction": "departure",
            "withLeg": "true",
            "withCancelled": "false",
            "withCodeshared": "true",
            "withCargo": "false",
            "withPrivate": "false"
        }
        headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": FLIGHT_API_HOST
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print("⚠️ Flight API Error:", response.status_code, response.text)
            return []

        departures = response.json().get("departures", [])[:5]

        flights = []
        for flight in departures:
            flights.append({
                "flight_number": flight.get("flight", {}).get("number", "N/A"),
                "departure_time": flight.get("departure", {}).get("scheduledTimeLocal", "Unknown"),
                "arrival_airport": flight.get("arrival", {}).get("airport", {}).get("name", "N/A"),
            })

        return flights

    except Exception as e:
        print("Unhandled error in flight fetch:", e)
        return []
