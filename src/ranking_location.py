import csv
import os
import math
import time
import requests

#intal dependecies: requests

'''NOTE: You may need to change where the csv are being accessed, the current code
has it to where I stored it on my machine, in main() you can adjust this. Default is set to restuarants.csv
in the parameters of load_restuarants function
'''

'''The key is stored on my local machine, if you would like the key let me know so i can give you it or you can create a google cloud
acacount and enable only the google distance matrix api. -Yahir

Steps to get it working (assuming you now have a key)
1.Run on shell (i used bash, not sure if that changes anything): 
    export GOOGLE_KEY="<key>"
2. Check if it exists in the directory
    echo $GOOGLE_KEY
3. Do not change the what GOOGLE_KEY is assigned too, once you ran steps 1-2 then it should work.'''

GOOGLE_KEY = os.environ["GOOGLE_KEY"]

#this is for the function call to compute distance, not very good lol
EARTH_RADIUS_M = 6_371_000
METERS_TO_MILES = 0.000621371

#testing locations
test_location = {"latitude": 33.73987164838857, "longitude": -117.87770864776505}
CARPINTERIA_CENTRAL = {"latitude": 34.3989, "longitude":-119.5185}
CARPINTERIA_STATE_BEACH = {"latitude": 34.3953,"longitude": -119.5255}
CARPINTERIA_LINDEN_AVE = {"latitude": 34.3982,"longitude": -119.5179}


restaurants = []
restaurant_distances = []
#batch size is how many calls we can do at a time for the google api. MAX is 25, do not put anything higher
#will cause the api call to be rejected, I limited the data size from business csv file to 100 only
#I did this to avoid getting charged for the google api ussage.
#should keep it to small size while testing, maybe expand to a bigger size when doing final simulations
BATCH_SIZE = 25 #for how many to request at a time.


def load_restaurants(path="restaurants.csv"):
    max_data = 100
    out = []

    with open(path, newline="", encoding="utf-8") as f:
        for i, row in enumerate(csv.DictReader(f)):
            if i >= max_data: #to stop api calls from exceeding limit, testing purposes
                break

            out.append({
                "business_id": row["business_id"],
                "name": row["name"],
                "address": row["address"],
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),})

    return out

def chunked(lst, n): #just not to do all api calls at once
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

#check the inner comments for future reference about mode (Driving or something else)
def distance_matrix_etas(origin_lat, origin_lon, destinations, departure_time_epoch):
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    origin = f"{origin_lat},{origin_lon}"
    dest_str = "|".join(f"{d['latitude']},{d['longitude']}" for d in destinations)

    params = {
        "origins": origin,
        "destinations": dest_str,
        "mode": "driving", #assume driving for now, but can be changed, check api doc
        "departure_time": departure_time_epoch,
        "key": GOOGLE_KEY,
    }
    
    #debug
    #print("dest_str sample:", dest_str[:120])
    #print("destinations count:", len(destinations))
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    #debug again
    #print("status:", data.get("status"))
    #print("error_message:", data.get("error_message"))


    elements = data["rows"][0]["elements"]
    etas_sec = []
    for el in elements:
        if el.get("status") != "OK":
            etas_sec.append(None)
            continue
        # get what we can, use the traffic version if av, else get the other ones
        dur = el.get("duration_in_traffic") or el.get("duration")
        etas_sec.append(dur["value"])  # seconds
    return etas_sec


def haversine(lat1, lon1, lat2, lon2): #might replace later with a better lib, but no for now
    lat1, lon1 = math.radians(lat1), math.radians(lon1)
    lat2, lon2 = math.radians(lat2), math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2)**2 + \
        math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2

    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))


TAU_MIN = 10.0
def eta_decay(eta_minutes, tau=TAU_MIN): # use eta with decay that shows the 'closest' place 
    '''The tau is the threshold (in minutes)
    that the user is willing to travel. tau is the accepable amount, anything under 
    is better, over is worse. We can adjust depending on the survey we give users'''
    return math.exp(-eta_minutes / tau)
    
    
#testing
def main():
    # Hardcoded user location for testing
    user_lat, user_lon = CARPINTERIA_CENTRAL["latitude"], CARPINTERIA_CENTRAL["longitude"]

    restaurants = load_restaurants("csv_files/oc_business.csv")

    # using curr time
    departure_time = int(time.time()) + 60

    ranked = []
    #go thorugh each batch and prcoess the eta score
    for batch in chunked(restaurants, BATCH_SIZE):  # Batch Size is adjustable, read comments on it
        etas = distance_matrix_etas(user_lat, user_lon, batch, departure_time)
        for r, eta_sec in zip(batch, etas):
            if eta_sec is None:
                continue
            eta_min = eta_sec / 60.0
            r["eta_min"] = eta_min
            r["score"] = eta_decay(eta_min)
            ranked.append(r)

    ranked.sort(key=lambda x: x["score"], reverse=True)

    print("Test location: Central Point at ", user_lat,", ", user_lon)
    num = 1
    for r in ranked[:10]:
        print(
            f"#{num:2d} "
            f"{r['name']:<30} "
            f"ETA(min)={r['eta_min']:5.1f} "
            f"score={r['score']:7.4f} | "
            f"{r.get('address','')}"
        )
        num +=1

#testing        
#if __name__ == "__main__":
#    main()