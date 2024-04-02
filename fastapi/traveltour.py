from fastapi import FastAPI, HTTPException, Path
import httpx
from pydantic import BaseModel
import requests
from iata_codes_db import IATA_CODES

app = FastAPI(title="Travel&Tourism")

GOOGLE_API_KEY = "AIzaSyDvvW7nyc45Hw-eUnGIw7puyHeh-6jDga4"
AVIATION_API_KEY = "91aeb735254a542ad7a4689cfc49b512"


def get_iata_code(city: str) -> str:
    full_match_entries = [
        entry 
        for entry in IATA_CODES 
        if city.upper().strip() == entry.get("municipality").upper() .strip()
    ]

    if full_match_entries:
        return full_match_entries[0]["iata_code"]

    partial_matched_entries = [
        entry 
        for entry in IATA_CODES 
        if city.upper().strip() in entry.get("municipality").upper().strip()
    ]

    if partial_matched_entries:
        return partial_matched_entries[0]["iata_code"]
    else:
        raise Exception("No airport found.")


@app.get("/hotels/{city_name}")
async def get_hotels(city_name: str):
    try:
        # Step 1: Get geocoordinates for the provided location using the Google Places API
        async with httpx.AsyncClient() as client:
            geocoding_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            params = {"query": city_name, "key": GOOGLE_API_KEY}
            geocoding_response = await client.get(geocoding_url, params=params)
            geocoding_data = geocoding_response.json()
            location_info = geocoding_data["results"][0]["geometry"]["location"]
            lat, lng = location_info["lat"], location_info["lng"]

        # Step 2: Get hotels based on the obtained geocoordinates
        async with httpx.AsyncClient() as client:
            places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            places_params = {
                "location": f"{lat},{lng}",
                "radius": 5000,  # Adjust the radius as needed
                "type": "lodging",
                "key": GOOGLE_API_KEY,
            }
            places_response = await client.get(places_url, params=places_params)
            places_data = places_response.json()
            hotels = [{"name": place["name"], "address": place.get("vicinity"), "rating": place.get("rating")} for place in places_data["results"]]

        return {"hotels": hotels}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")



@app.get("/attractions/{city_name}")
async def get_attractions(city_name: str):
    try:
        # Step 1: Get geocoordinates for the provided location using the Google Places API
        async with httpx.AsyncClient() as client:
            geocoding_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            params = {"query": city_name, "key": GOOGLE_API_KEY}
            geocoding_response = await client.get(geocoding_url, params=params)
            geocoding_data = geocoding_response.json()
            location_info = geocoding_data["results"][0]["geometry"]["location"]
            lat, lng = location_info["lat"], location_info["lng"]

        # Step 2: Get Tourist attraction places near by based on the obtained geocoordinates
        async with httpx.AsyncClient() as client:
            places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            places_params = {
                "location": f"{lat},{lng}",
                "radius": 5000,  # Adjust the radius as needed
                "type": "tourist_attraction",
                "key": GOOGLE_API_KEY,
            }
            places_response = await client.get(places_url, params=places_params)
            places_data = places_response.json()
            tourist_attractions = [
                {"name": place["name"], "address": place.get("vicinity"), "rating": place.get("rating")} for place in places_data["results"]
            ]

        return {"tourist_attractions": tourist_attractions}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    

@app.get("/flights/")
async def get_flights(from_city_name: str, to_city_name: str):
    try:
        # Step 1: We created a static DB with IATAcodes & used flights api to get real time flights information
        async with httpx.AsyncClient() as client:
            from_iata_code = get_iata_code(from_city_name)
            to_iata_code =  get_iata_code(to_city_name)

            print(f"From IATA Code: {from_iata_code}")
            print(f"To IATA Code: {to_iata_code}")

            flights_params = {"dep_iata": from_iata_code, "arr_iata": to_iata_code, "access_key": AVIATION_API_KEY}
            flights_response = await client.get(f'http://api.aviationstack.com/v1/flights', params=flights_params)
            flights_data = flights_response.json()
    
        # Step 2: Extract and format relevant flight information
        if "data" in flights_data and isinstance(flights_data["data"], list):
            formatted_flights = [
                {
                    "flight_date": flight.get("flight_date", "N/A"),
                    "airline_name": flight.get("airline", {}).get("name", "N/A"),
                    "flight_number": flight.get("flight", {}).get("number", "N/A")
                }
                for flight in flights_data["data"]
            ]
            return {"flights": formatted_flights}
        else:
            return {"flights": []}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")


