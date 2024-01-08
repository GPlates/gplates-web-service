import json
import logging
import os
import unittest
from pathlib import Path

import common
import requests
import urllib3


class OldTestCase(unittest.TestCase):
    def setUp(self):
        self.proxies = {"http": ""}

    def tearDown(self):
        self.logger.info("tearDown")

    @classmethod
    def setUpClass(cls):
        common.setup_logger(cls, Path(__file__).stem)

    @classmethod
    def tearDownClass(cls):
        cls.logger.info("tearDownClass")

    def test_old_cases(self):
        data = {"points": "95,54,142,-33", "time": 140}
        r = requests.get(
            self.SERVER_URL + "/reconstruct/reconstruct_points/",
            params=data,
            verify=False,
            proxies=self.proxies,
        )
        self.logger.info(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
        self.assertEqual(r.status_code, 200)

        r = requests.post(
            self.SERVER_URL + "/reconstruct/reconstruct_points/",
            data=data,
            verify=False,
            proxies=self.proxies,
        )
        self.logger.info(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
        self.assertEqual(r.status_code, 200)

        data = {"points": "95,54,-117.26,32.7,142,-33", "time": 140, "fc": ""}
        r = requests.post(
            self.SERVER_URL + "/reconstruct/reconstruct_points/",
            data=data,
            verify=False,
            proxies=self.proxies,
        )
        self.logger.info(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
        self.assertEqual(r.status_code, 200)

        r = requests.get(
            self.SERVER_URL + "/reconstruct/reconstruct_points/",
            params=data,
            verify=False,
            proxies=self.proxies,
        )
        self.logger.info(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
        self.assertEqual(r.status_code, 200)

        data = {
            "feature_collection": """{"type":"FeatureCollection",
                "features":[
                    {"type":"Feature",
                    "geometry":{
                        "type":"Polygon",
                        "coordinates":[[[128,-17],[133,-18],[138,-19],
                            [140,-23],[139,-27],[130,-27],[128,-24],
                            [127,-21],[127,-17],[128,-17]]]},
                        "properties":{
                            "id":123,
                            "waht":"345"
                        }},
                        
                        {"type":"Feature",
                        "geometry":
                        {
                            "type":"Point",
                            "coordinates":[51.0, 38.0]
                        },
                        "properties":{
                            "id":222
                        }
                        }
                
                        
                        ]}
            """,
            "geologicage": "140",
            "model": "SETON2012",
        }

        r = requests.get(
            self.SERVER_URL + "/reconstruct/reconstruct_feature_collection/",
            params=data,
            verify=False,
            proxies=self.proxies,
        )
        self.assertEqual(r.status_code, 200)
        self.logger.info(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))

        data["keep_properties"] = ""
        r = requests.get(
            self.SERVER_URL + "/reconstruct/reconstruct_feature_collection/",
            params=data,
            verify=False,
            proxies=self.proxies,
        )
        self.assertEqual(r.status_code, 200)
        self.logger.info(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))

        r = requests.post(
            self.SERVER_URL + "/reconstruct/reconstruct_feature_collection/",
            data=data,
            verify=False,
            proxies=self.proxies,
        )
        self.assertEqual(r.status_code, 200)
        self.logger.info(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))

    @unittest.skip("skip test_paleobiodb")
    def test_paleobiodb(self):
        r = requests.get(
            "http://paleobiodb.org/data1.1/occs/list.json?limit=all&interval_id=3001&show=coords,attr,loc,prot,time,strat,stratext,lith,lithext,geo,rem,ent,entname,crmod&showsource",
            proxies=self.proxies,
        )

        self.assertEqual(r.status_code, 200)
        self.logger.info(r.text)

        pbdb = json.loads(r.text)
        lons = []
        lats = []
        for record in pbdb["records"]:
            lons.append(record["lng"])
            lats.append(record["lat"])

        fc = {"type": "FeatureCollection"}
        fc["features"] = []
        for i, record in enumerate(pbdb["records"]):
            feature = {"type": "Feature"}
            feature["geometry"] = {}
            feature["geometry"]["type"] = "Point"
            feature["geometry"]["coordinates"] = [record["lng"], record["lat"]]
            feature["properties"] = {}
            feature["properties"]["Id"] = "tmp"
            fc["features"].append(feature)

        data = {"feature_collection": json.dumps(fc)}

        data["keep_properties"] = ""
        data["time"] = 120.0

        r = requests.post(
            self.SERVER_URL + "/reconstruct/reconstruct_feature_collection/",
            data=data,
            verify=False,
            proxies=self.proxies,
        )
        self.assertEqual(r.status_code, 200)
        self.logger.info(r.text)


if __name__ == "__main__":
    unittest.main()
