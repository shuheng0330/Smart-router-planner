import streamlit as st
from chat_agent import ask_transport_bot, save_favorite_route, favorite_routes
from route_handler import get_route_info, get_fastest_route_summary
from dotenv import load_dotenv
import googlemaps
import os
import folium
from streamlit_folium import st_folium
from streamlit_autorefresh import st_autorefresh
import datetime
import json
import re

def strip_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def convert_duration_to_minutes(duration_str):
    match = re.findall(r'\d+', duration_str)
    return sum([int(n) for n in match]) if match else 0

# Load environment
load_dotenv()
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
gmaps = googlemaps.Client(key=API_KEY)
FAV_ROUTE_FILE = "favorite_routes.json"

def delete_favorite_route(name):
    if name in favorite_routes:
        del favorite_routes[name]
        with open(FAV_ROUTE_FILE, "w") as f:
            json.dump(favorite_routes, f, indent=2)
        return f"Route '{name}' deleted successfully."
    return f"Route '{name}' not found."

# Setup UI
st.set_page_config(page_title="Transport Planner", layout="centered")
st.title("🚍 Malaysia Transport Planner Bot")

st.markdown("""
Use this assistant to:
- 🔍 Find a route (e.g., `from UM to KLCC using MRT`)
- 🚀 Fastest route (e.g., `fastest way from UM to KL Sentral`)
- 💾 Save a route (e.g., `work, University Malaya, KL Sentral, transit`)
- 📂 Retrieve or delete saved routes below
""")

# Favorite Route Section
st.markdown("## 📂 View or Delete Saved Routes")
if not favorite_routes:
    st.info("You don't have any saved routes yet.")
else:
    route_names = list(favorite_routes.keys())
    selected_name = st.selectbox("Choose a saved route", route_names)

    col1, col2 = st.columns([2, 1])
    if col1.button("Load Selected Route"):
        st.session_state["load_fav_route"] = selected_name
    if col2.button("❌ Delete This Route"):
        st.success(delete_favorite_route(selected_name))
        st.experimental_rerun()

# If route selected, display details
if "load_fav_route" in st.session_state:
    selected = favorite_routes[st.session_state["load_fav_route"]]
    origin = selected["origin"]
    destination = selected["destination"]
    mode = selected.get("mode", "transit")

    st.markdown(f"### 📍 Route: **{st.session_state['load_fav_route'].capitalize()}**")
    date = st.date_input("Departure Date", value=datetime.date.today(), key="fav_date")
    time = st.time_input("Departure Time", value=datetime.datetime.now().time(), key="fav_time")
    departure_dt = datetime.datetime.combine(date, time)
    departure_ts = int(departure_dt.timestamp())

    status, route = get_route_info(origin, destination, mode, departure_time=departure_ts)
    if route:
        directions = gmaps.directions(origin, destination, mode=mode, departure_time=departure_ts)
        if directions and "overview_polyline" in directions[0]:
            decoded = googlemaps.convert.decode_polyline(directions[0]['overview_polyline']['points'])
            midpoint = decoded[len(decoded)//2]
            m = folium.Map(location=[midpoint['lat'], midpoint['lng']], zoom_start=13)
            folium.PolyLine([(p['lat'], p['lng']) for p in decoded], color="green", weight=5).add_to(m)
            folium.Marker([decoded[0]['lat'], decoded[0]['lng']], tooltip="Start").add_to(m)
            folium.Marker([decoded[-1]['lat'], decoded[-1]['lng']], tooltip="End").add_to(m)
            st_folium(m, width=700, height=500)

        with st.expander("📋 Step-by-Step Directions"):
            for i, step in enumerate(route.get("steps", []), 1):
                st.markdown(f"**{i}.** {strip_html_tags(step)}")

    if st.button("🔄 Clear View"):
        st.session_state.pop("load_fav_route", None)
        st.experimental_rerun()

    # --- Monitoring Feature ---
    refresh_interval = st.selectbox("Auto-refresh interval (seconds):", [15, 30, 60], index=1)

    if st.button("🛰️ Monitor This Route"):
        st.session_state["monitoring_route"] = {
            "origin": origin,
            "destination": destination,
            "mode": mode,
            "baseline_eta": convert_duration_to_minutes(route["duration"]),
            "route": route
        }
        st.success(f"✅ Monitoring started. Baseline ETA: {route['duration']}")

    if "monitoring_route" in st.session_state:
        st.markdown(f"### 🔄 Live Monitoring (every {refresh_interval}s)")
        st_autorefresh(interval=refresh_interval * 1000, key="auto_refresh_monitor")

        r = st.session_state["monitoring_route"]
        status, current_route = get_route_info(r["origin"], r["destination"], r["mode"], departure_time="now")

        if current_route:
            current_eta = convert_duration_to_minutes(current_route["duration"])
            baseline = r["baseline_eta"]

            if current_eta - baseline > 15:
                st.error(f"⚠️ Delay detected! ETA increased by {current_eta - baseline} mins.")
                alt_status, alt_route = get_fastest_route_summary(f"from {r['origin']} to {r['destination']}")
                if alt_route:
                    st.markdown(f"**{alt_status}**")
                    st.markdown(f"**Duration:** {alt_route['duration']}  \n**Distance:** {alt_route['distance']}")
                    with st.expander("📋 Step-by-Step Directions (Alternative Route)"):
                        for i, step in enumerate(alt_route["steps"], 1):
                            st.markdown(f"**{i}.** {strip_html_tags(step)}")
                    if st.button("✅ Select Alternative Route"):
                        r["route"] = alt_route
                        r["baseline_eta"] = convert_duration_to_minutes(alt_route["duration"])
                        st.success("✅ Switched to alternative route.")
                        st.experimental_rerun()
                else:
                    st.warning(alt_status)
            else:
                st.success(f"✅ ETA OK: {current_eta} mins (baseline: {baseline} mins)")

        st.markdown("### 🗺️ Current Monitored Route")
        route_to_display = st.session_state["monitoring_route"]["route"]
        st.markdown(f"**Duration:** {route_to_display['duration']}")
        st.markdown(f"**Distance:** {route_to_display['distance']}")
        with st.expander("📋 Step-by-Step Directions (Current Route)"):
            for i, step in enumerate(route_to_display["steps"], 1):
                st.markdown(f"**{i}.** {strip_html_tags(step)}")

        if st.button("🛑 Stop Monitoring"):
            st.session_state.pop("monitoring_route", None)
            st.success("Monitoring stopped.")
            st.experimental_rerun()

# Chatbot Prompt Section
st.markdown("---")
st.markdown("## 💬 Ask the Route Bot")

user_input = st.text_input("Ask something...", placeholder="e.g. from UM to KLCC using MRT")
date = st.date_input("Departure Date", value=datetime.date.today(), key="main_date")
time = st.time_input("Departure Time", value=datetime.datetime.now().time(), key="main_time")
departure_ts = int(datetime.datetime.combine(date, time).timestamp())

if st.button("Submit") or user_input:
    with st.spinner("Thinking..."):
        try:
            response = ask_transport_bot(user_input)
            st.success(response)

            if "from" in user_input and "to" in user_input:
                parts = user_input.lower().split("to")
                origin = parts[0].replace("from", "").strip()
                destination = parts[1].split("using")[0].strip()
                if "driving" in user_input: mode = "driving"
                elif "walking" in user_input: mode = "walking"
                elif "bicycling" in user_input: mode = "bicycling"
                else: mode = "transit"

                _, route = get_route_info(origin, destination, mode=mode, departure_time=departure_ts)
                if route:
                    directions = gmaps.directions(origin, destination, mode=mode, departure_time=departure_ts)
                    if directions and "overview_polyline" in directions[0]:
                        decoded = googlemaps.convert.decode_polyline(directions[0]['overview_polyline']['points'])
                        midpoint = decoded[len(decoded)//2]
                        m = folium.Map(location=[midpoint['lat'], midpoint['lng']], zoom_start=13)
                        folium.PolyLine([(p['lat'], p['lng']) for p in decoded], color="blue", weight=5).add_to(m)
                        folium.Marker([decoded[0]['lat'], decoded[0]['lng']], tooltip="Start").add_to(m)
                        folium.Marker([decoded[-1]['lat'], decoded[-1]['lng']], tooltip="End").add_to(m)
                        st.markdown("### 🗺️ Route Map")
                        st_folium(m, width=700, height=500)

                    with st.expander("📋 Step-by-Step Directions"):
                        for i, step in enumerate(route["steps"], 1):
                            st.markdown(f"**{i}.** {strip_html_tags(step)}")

                    with st.expander("💾 Save this route to favorites"):
                        fav_name = st.text_input("Name this route", key="save_name")
                        if st.button("Save Route"):
                            result = save_favorite_route(f"{fav_name}, {origin}, {destination}, {mode}")
                            st.success(result)
        except Exception as e:
            st.error(f"❌ Error: {e}")





