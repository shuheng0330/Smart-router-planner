import re

import googlemaps
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Initialize client
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
gmaps = googlemaps.Client(key=API_KEY)

# def get_route_info(origin, destination, mode="transit", arrival_time=None):
#     try:
#         params = {
#             "origin": origin,
#             "destination": destination,
#             "mode": mode,
#             "departure_time": "now"
#         }
#
#         if arrival_time:
#             params["arrival_time"] = arrival_time
#             params.pop("departure_time", None)
#
#         directions_result = gmaps.directions(**params)
#
#         if not directions_result:
#             return "No route found.", None
#
#         leg = directions_result[0]['legs'][0]
#         steps = [
#             f"{step['html_instructions']} ({step['distance']['text']})"
#             for step in leg['steps']
#         ]
#         summary = {
#             "duration": leg['duration']['text'],
#             "distance": leg['distance']['text'],
#             "start": leg['start_address'],
#             "end": leg['end_address'],
#             "steps": steps
#         }
#         return "Route found successfully.", summary
#
#     except Exception as e:
#         # Handle quota or limit exceeded errors with a friendly message
#         error_message = str(e).lower()
#         if "quota" in error_message or "limit" in error_message or "exceeded" in error_message:
#             return "API limit exceeded. Please try again later.", None
#         return f"Error fetching route: {str(e)}", None

def get_route_info(origin, destination, mode="transit", departure_time=None, arrival_time=None):
    try:
        params = {
            "origin": origin,
            "destination": destination,
            "mode": mode
        }

        # Default to "now" only if driving and no time is provided
        if departure_time:
            params["departure_time"] = departure_time
        elif mode == "driving":
            params["departure_time"] = "now"

        if arrival_time:
            params["arrival_time"] = arrival_time
            params.pop("departure_time", None)  # can't use both

        directions_result = gmaps.directions(**params)

        if not directions_result:
            return "No route found.", None

        leg = directions_result[0]['legs'][0]
        steps = [
            f"{step['html_instructions']} ({step['distance']['text']})"
            for step in leg['steps']
        ]
        summary = {
            "duration": leg['duration']['text'],
            "distance": leg['distance']['text'],
            "start": leg['start_address'],
            "end": leg['end_address'],
            "steps": steps
        }
        return "Route found successfully.", summary

    except Exception as e:
        error_message = str(e).lower()
        if "quota" in error_message or "limit" in error_message or "exceeded" in error_message:
            return "API limit exceeded. Please try again later.", None
        return f"Error fetching route: {str(e)}", None


# def get_fastest_route_summary(input_text: str) -> str:
#     if "to" not in input_text:
#         return "Please specify origin and destination using the format: from A to B"
#
#     parts = input_text.lower().split("to")
#     origin = parts[0].replace("from", "").strip()
#     destination = parts[1].split("using")[0].strip()
#
#     for mode in ["transit", "driving", "walking", "bicycling"]:
#         status, route = get_route_info(origin, destination, mode=mode, departure_time="now")
#         if route:
#             return "Final Answer: Fastest route found:\n" + \
#                    f"Duration: {route['duration']}\nDistance: {route['distance']}\nSteps:\n- " + \
#                    "\n- ".join(route["steps"])
#     return "No valid routes found."

def get_fastest_route_summary(input_text: str):
    # Parse input like 'from A to B'
    if "to" not in input_text.lower():
        return "Invalid input format.", None

    parts = input_text.lower().split("to")
    origin = parts[0].replace("from", "").strip()
    destination = parts[1].split("using")[0].strip()

    best_route = None
    best_duration = float("inf")
    best_status = ""

    for mode in ["transit", "driving", "walking", "bicycling"]:
        status, route = get_route_info(origin, destination, mode=mode, departure_time="now")
        if route:
            # Extract duration in minutes for comparison
            match = re.findall(r'\d+', route["duration"])
            total_minutes = sum(int(n) for n in match) if match else float("inf")

            if total_minutes < best_duration:
                best_route = route
                best_status = f"Fastest route found using {mode}"
                best_duration = total_minutes

    if best_route:
        return best_status, best_route
    else:
        return "No valid routes found.", None

