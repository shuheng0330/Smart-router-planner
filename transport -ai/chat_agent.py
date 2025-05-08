# from langchain.chat_models import ChatOpenAI
# from langchain.agents import Tool, initialize_agent
# from langchain.agents.agent_types import AgentType
# from route_handler import get_route_info, get_fastest_route_summary
# from dotenv import load_dotenv
# import os
# import re
# import json
#
# load_dotenv()
#
# # Store favorite routes in memory
# FAV_ROUTE_FILE = "favorite_routes.json"
# favorite_routes = {}
#
# def get_route_summary(input_text: str) -> str:
#     if "to" not in input_text:
#         return "Please specify origin and destination using the format: from A to B"
#
#     parts = input_text.lower().split("to")
#     origin = parts[0].replace("from", "").strip()
#     destination = parts[1].split("using")[0].strip()
#
#     mode = "transit"
#     if "driving" in input_text:
#         mode = "driving"
#     elif "walking" in input_text:
#         mode = "walking"
#     elif "bicycling" in input_text:
#         mode = "bicycling"
#
#     status, route = get_route_info(origin, destination, mode)
#     if route:
#         return "Final Answer: " + f"{status}\nDuration: {route['duration']}\nDistance: {route['distance']}\nSteps:\n- " + "\n- ".join(route["steps"])
#     else:
#         return status
#
# def load_favorite_routes():
#     if os.path.exists(FAV_ROUTE_FILE):
#         with open(FAV_ROUTE_FILE, "r") as f:
#             return json.load(f)
#     return {}
#
# def save_favorite_routes(routes):
#     with open(FAV_ROUTE_FILE, "w") as f:
#         json.dump(routes, f, indent=2)
#
# def save_favorite_route(input_text: str) -> str:
#     try:
#         # Natural language format with case-insensitive matching
#         match = re.search(
#             r"save (?:this )?route as (\w+): from (.+?) to (.+?)(?: using (.+))?$",
#             input_text,
#             re.IGNORECASE
#         )
#         if match:
#             name = match.group(1).strip()
#             origin = match.group(2).strip()
#             destination = match.group(3).strip()
#             mode = match.group(4).strip() if match.group(4) else "transit"
#         else:
#             # Fallback to comma-separated format
#             parts = [x.strip() for x in input_text.split(",")]
#             if len(parts) < 3:
#                 return "Invalid input format. Use: 'name, origin, destination[, mode]'"
#             name, origin, destination = parts[:3]
#             mode = parts[3].strip() if len(parts) > 3 else "transit"
#
#         # Save the route
#         favorite_routes[name] = {
#             "origin": origin,
#             "destination": destination,
#             "mode": mode
#         }
#         return f"Route '{name}' saved successfully."
#     except Exception as e:
#         return f"Failed to save favorite route: {e}"
#
# def get_favorite_route_summary(name: str) -> str:
#     favorite_routes = load_favorite_routes()
#     fav = favorite_routes.get(name.lower())
#     if not fav:
#         return f"No favorite route named '{name}'."
#
#     status, route = get_route_info(fav["origin"], fav["destination"], fav["mode"])
#     if route:
#         return "Final Answer: " + f"{status}\nDuration: {route['duration']}\nDistance: {route['distance']}\nSteps:\n- " + "\n- ".join(route["steps"])
#     else:
#         return status
#
# # LangChain tools
# tools = [
#     Tool(
#         name="RouteFinder",
#         func=get_route_summary,
#         description="Find route from A to B. Example: 'from UM to KLCC using MRT'"
#     ),
#     Tool(
#         name="FastestRouteFinder",
#         func=get_fastest_route_summary,
#         description="Find fastest route from A to B using all transport modes."
#     ),
#     Tool(
#         name="FavoriteRouteSaver",
#         func=save_favorite_route,
#         description="Save a favorite route. Format: 'name, origin, destination, mode'"
#     ),
#     Tool(
#         name="FavoriteRouteGetter",
#         func=get_favorite_route_summary,
#         description="Get a saved favorite route by name. Format: 'home', 'work', etc."
#     )
# ]
#
# llm = ChatOpenAI(
#     model="mistralai/mistral-7b-instruct:free",
#     temperature=0,
#     openai_api_key=os.getenv("OPENROUTER_API_KEY"),
#     openai_api_base="https://openrouter.ai/api/v1"
# )
#
# agent = initialize_agent(
#     tools,
#     llm,
#     agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
#     verbose=True,
#     handle_parsing_errors=True
# )
#
# def ask_transport_bot(prompt):
#     return agent.invoke({"input": prompt})["output"]


from langchain.chat_models import ChatOpenAI
from langchain.agents import Tool, initialize_agent
from langchain.agents.agent_types import AgentType
from route_handler import get_route_info, get_fastest_route_summary
from dotenv import load_dotenv
import os
import re
import json

load_dotenv()

# Store favorite routes in memory
FAV_ROUTE_FILE = "favorite_routes.json"

# --- Helper Functions for File I/O ---
def _load_favorite_routes_from_file():
    if os.path.exists(FAV_ROUTE_FILE):
        with open(FAV_ROUTE_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Error decoding {FAV_ROUTE_FILE}. Starting with empty favorites.")
                return {}
    return {}

def _save_favorite_routes_to_file(routes_data):
    with open(FAV_ROUTE_FILE, "w") as f:
        json.dump(routes_data, f, indent=2)

# --- Global State ---
favorite_routes = _load_favorite_routes_from_file()

# --- Core Logic Functions (Tools) ---
def get_route_summary(input_text: str) -> str:
    if "to" not in input_text:
        return "Please specify origin and destination using the format: from A to B"

    parts = input_text.lower().split("to")
    origin = parts[0].replace("from", "").strip()
    destination = parts[1].split("using")[0].strip()

    # Extract mode if mentioned
    mode = "transit"
    if "driving" in input_text.lower():
        mode = "driving"
    elif "walking" in input_text.lower():
        mode = "walking"
    elif "bicycling" in input_text.lower():
        mode = "bicycling"

    status, route = get_route_info(origin, destination, mode)
    if route:
        duration = route.get("duration", "N/A")
        distance = route.get("distance", "N/A")
        steps = route.get("steps", [])
        if not isinstance(steps, list):
            steps = [str(steps)]
        return "Final Answer: " + f"{status}\nDuration: {duration}\nDistance: {distance}\nSteps:\n- " + "\n- ".join(steps)
    else:
        return status

def save_favorite_route(input_text: str) -> str:
    try:
        name = "custom"  # Default name if not provided
        origin = destination = mode = None

        # First: try flexible natural phrase parsing
        natural_match = re.search(
            r"from\s+(.*?)\s+to\s+(.*?)(?:\s+by\s+(\w+))?",
            input_text,
            re.IGNORECASE
        )
        if natural_match:
            origin = natural_match.group(1).strip()
            destination = natural_match.group(2).strip()
            mode_raw = natural_match.group(3)
            mode = mode_raw.lower() if mode_raw else "transit"
        else:
            # Second: try comma-separated format
            parts = [x.strip() for x in input_text.split(",")]
            if len(parts) >= 3:
                name = parts[0].lower()
                origin = parts[1]
                destination = parts[2]
                mode = parts[3].lower() if len(parts) > 3 else "transit"
            else:
                return ("❌ Invalid format. Use:\n"
                        "• 'from ORIGIN to DESTINATION by MODE'\n"
                        "• or 'name, origin, destination[, mode]'")

        # Clean up mode
        valid_modes = ["driving", "walking", "transit", "bicycling"]
        for vm in valid_modes:
            if vm in mode:
                mode = vm
                break
        else:
            return f"❌ Invalid transport mode. Use one of: {', '.join(valid_modes)}"

        # Validate origin/destination
        if not origin or not destination:
            return "❌ Please specify both origin and destination clearly."
        if any(x in origin.lower() for x in ["get me", "route"]) or \
           any(x in destination.lower() for x in ["get me", "route"]):
            return "❌ Invalid origin/destination. Please use proper place names only."

        # Save route
        favorite_routes[name] = {
            "origin": origin,
            "destination": destination,
            "mode": mode
        }
        _save_favorite_routes_to_file(favorite_routes)
        return f"✅ Route '{name}' saved successfully.\nFrom: {origin} → {destination} using {mode}"

    except Exception as e:
        return f"❌ Failed to save route: {e}"


def get_favorite_route_summary(name: str) -> str:
    fav_name = name.lower().strip()
    fav = favorite_routes.get(fav_name)
    if not fav:
        return f"No favorite route named '{name}'."

    status, route = get_route_info(fav["origin"], fav["destination"], fav["mode"])
    if route:
        duration = route.get("duration", "N/A")
        distance = route.get("distance", "N/A")
        steps = route.get("steps", [])
        if not isinstance(steps, list):
            steps = [str(steps)]
        return "Final Answer: " + f"{status}\nDuration: {duration}\nDistance: {distance}\nSteps:\n- " + "\n- ".join(steps)
    else:
        return status

# --- LangChain Tools ---
tools = [
    Tool(
        name="RouteFinder",
        func=get_route_summary,
        description="Find route from A to B. Input should be like 'from [origin] to [destination] [using transport mode]'. Example: 'from UM to KLCC using MRT'"
    ),
    Tool(
        name="FastestRouteFinder",
        func=get_fastest_route_summary,
        description="Find the fastest route from A to B using all transport modes. Input: 'fastest route from [origin] to [destination]'"
    ),
    Tool(
        name="FavoriteRouteSaver",
        func=save_favorite_route,
        description="Save a favorite route. Input: 'save route as NAME: from ORIGIN to DESTINATION using MODE' or 'name, origin, destination[, mode]'"
    ),
    Tool(
        name="FavoriteRouteGetter",
        func=get_favorite_route_summary,
        description="Get a saved favorite route by name. Input: just the name. Example: 'my work'"
    )
]

# --- LLM and Agent Setup ---
llm = ChatOpenAI(
    model="mistralai/mistral-7b-instruct:free",
    temperature=0,
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1"
)

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors="True"
)

# --- Main Interface ---
def ask_transport_bot(prompt: str) -> str:
    return agent.invoke({"input": prompt})["output"]





