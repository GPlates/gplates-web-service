import json
import time
import unittest
from pathlib import Path

import requests
from common import get_server_url, setup_logger

# python3 -m unittest -vv test_paleobiodb.py


class PaleobiodbTestCase(unittest.TestCase):
    def setUp(self):
        self.proxies = {"http": ""}

    @classmethod
    def setUpClass(cls):
        setup_logger(cls, Path(__file__).stem)
        get_server_url(cls)

    @classmethod
    def tearDownClass(cls):
        cls.logger.info("tearDownClass")

    @unittest.skip("skip test_paleobiodb")
    def test_paleobiodb(self):
        # time.sleep(1)
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
