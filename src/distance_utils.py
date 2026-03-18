import math
import requests
import os

GOOGLE_KEY = os.environ["GOOGLE_KEY"]
TAU_MIN = 10.0

def distance_matrix_etas(origin_lat, origin_lon, destinations):
    if origin_lat is None or origin_lon is None:
        return [None] * len(destinations)

    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    dest_str = "|".join(f"{d['latitude']},{d['longitude']}" for d in destinations)
    params = {
        "origins": f"{origin_lat},{origin_lon}",
        "destinations": dest_str,
        "mode": "driving",
        "departure_time": "now",
        "key": GOOGLE_KEY,
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    rows = data.get("rows", [])
    if not rows:
        return [None] * len(destinations)

    etas = []
    for el in rows[0]["elements"]:
        if el.get("status") != "OK":
            etas.append(None)
            continue
        dur = el.get("duration_in_traffic") or el.get("duration")
        etas.append(dur["value"] / 60.0)
    return etas


def commute_etas(home_lat, home_lon, work_lat, work_lon, destinations):
    """
    Call 1: home -> each restaurant
    Call 2: each restaurant -> work
    Returns total commute time through each restaurant
    """
    if not all([home_lat, home_lon, work_lat, work_lon]):
        return [None] * len(destinations)

    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    dest_str = "|".join(f"{d['latitude']},{d['longitude']}" for d in destinations)
    orig_str = "|".join(f"{d['latitude']},{d['longitude']}" for d in destinations)

    # Call 1: home -> all restaurants
    params1 = {
        "origins": f"{home_lat},{home_lon}",
        "destinations": dest_str,
        "mode": "driving",
        "departure_time": "now",
        "key": GOOGLE_KEY,
    }
    # Call 2: all restaurants -> work
    params2 = {
        "origins": orig_str,
        "destinations": f"{work_lat},{work_lon}",
        "mode": "driving",
        "departure_time": "now",
        "key": GOOGLE_KEY,
    }

    resp1 = requests.get(url, params=params1, timeout=10)
    resp2 = requests.get(url, params=params2, timeout=10)
    resp1.raise_for_status()
    resp2.raise_for_status()

    rows1 = resp1.json().get("rows", [])
    rows2 = resp2.json().get("rows", [])

    if not rows1 or not rows2:
        return [None] * len(destinations)

    home_elements = rows1[0]["elements"]       # home -> each restaurant
    work_elements = [r["elements"][0] for r in rows2]  # each restaurant -> work

    totals = []
    for home_el, work_el in zip(home_elements, work_elements):
        if home_el.get("status") != "OK" or work_el.get("status") != "OK":
            totals.append(None)
            continue
        home_dur = home_el.get("duration_in_traffic") or home_el.get("duration")
        work_dur = work_el.get("duration_in_traffic") or work_el.get("duration")
        totals.append((home_dur["value"] + work_dur["value"]) / 60.0)
    print("HOME:", home_lat, home_lon)
    print("WORK:", work_lat, work_lon)
    print("rows1 length:", len(rows1))
    print("rows2 length:", len(rows2))
    print("sample home element:", rows1[0]["elements"][0])
    print("sample work element:", rows2[0]["elements"][0])
    return totals


def eta_decay(eta_minutes, tau=TAU_MIN):
    return math.exp(-eta_minutes / tau)