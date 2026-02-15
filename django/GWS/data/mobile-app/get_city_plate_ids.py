import json

import requests

with open("cities.json", "r", encoding="utf-8") as file:
    data = json.load(file)
    lons = []
    lats = []
    for key in data["coords"].keys():
        lon, lat, _ = data["coords"][key]
        lons.append(lon)
        lats.append(lat)
    print("lons:", ",".join(str(lon) for lon in lons))
    print("lats:", ",".join(str(lat) for lat in lats))


url = "https://gws.gplates.org/reconstruct/assign_points_plate_ids"
params = {
    "lons": ",".join(str(lon) for lon in lons),
    "lats": ",".join(str(lat) for lat in lats),
    "model": "ZAHIROVIC2022",
}
response = requests.get(url, params=params)
print(response.text)
