#!/usr/bin/env python3
import json
import unittest
from pathlib import Path

from common import (
    add_server_url_to_docstring,
    get_server_url,
    get_test_flag,
    send_get_request,
    setup_logger,
)

# python3 -m unittest -vv test_magnetic_picks.py

ENDPOINT = "/earth/get_magnetic_picks/"

REGIONS = ["atlantic", "indian", "pacific", "marginal_backarc_basins"]


class MagneticPicksParameterCase(unittest.TestCase):
    """Parameter validation. These cases do not need the picks to be loaded
    into the database, because the endpoint rejects bad parameters before it
    queries anything."""

    @classmethod
    def setUpClass(cls):
        setup_logger(cls, Path(__file__).stem + "-parameters")
        get_server_url(cls)

    def _expect_400(self, name, params):
        r = send_get_request(self.SERVER_URL + ENDPOINT, params=params)
        msg = ""
        if r.request.url:
            msg += r.request.url + "\n"
        msg += r.text + "\n"
        self.logger.info(
            f"######### {name} ###########\n\n{msg}\n########## end ##########\n"
        )
        self.assertEqual(r.status_code, 400)

    @add_server_url_to_docstring()
    def test_unknown_region(self):
        """-   testing {}/earth/get_magnetic_picks/?region=mediterranean   (unknown region)"""
        self._expect_400("test_unknown_region", {"region": "mediterranean"})

    def test_end_index_not_greater_than_start_index(self):
        """-   testing /earth/get_magnetic_picks/ with end_index <= start_index"""
        self._expect_400(
            "test_end_index_not_greater_than_start_index",
            {"start_index": 100, "end_index": 100},
        )

    def test_negative_start_index(self):
        """-   testing /earth/get_magnetic_picks/ with a negative start_index"""
        self._expect_400("test_negative_start_index", {"start_index": -1})

    def test_range_too_large(self):
        """-   testing /earth/get_magnetic_picks/ with a range larger than the maximum page size"""
        self._expect_400(
            "test_range_too_large", {"start_index": 0, "end_index": 500000}
        )

    def test_invalid_start_index(self):
        """-   testing /earth/get_magnetic_picks/ with a start_index which is not an integer"""
        self._expect_400("test_invalid_start_index", {"start_index": "abc"})

    def test_invalid_min_age(self):
        """-   testing /earth/get_magnetic_picks/ with a min_age which is not a number"""
        self._expect_400("test_invalid_min_age", {"min_age": "ten"})

    def test_min_age_greater_than_max_age(self):
        """-   testing /earth/get_magnetic_picks/ with min_age > max_age"""
        self._expect_400(
            "test_min_age_greater_than_max_age", {"min_age": 50, "max_age": 10}
        )


@unittest.skipIf(
    get_test_flag("GWS_TEST_DB_QUERY") is not True,
    "GWS_TEST_DB_QUERY environment variable is not set to true.",
)
class MagneticPicksQueryCase(unittest.TestCase):
    """Queries against the loaded data. Needs "manage.py load_magnetic_picks"
    to have been run against the server's database."""

    @classmethod
    def setUpClass(cls):
        setup_logger(cls, Path(__file__).stem)
        get_server_url(cls)

    def _get(self, params):
        r = send_get_request(self.SERVER_URL + ENDPOINT, params=params)
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.text)
        self.logger.info(
            f"{r.request.url}\n"
            f"returned={data.get('returned')} total_matched={data.get('total_matched')}\n"
        )
        return data

    def _check_feature_collection(self, data):
        self.assertEqual(data["type"], "FeatureCollection")
        self.assertIn("features", data)
        self.assertEqual(len(data["features"]), data["returned"])
        for feature in data["features"]:
            self.assertEqual(feature["type"], "Feature")
            self.assertEqual(feature["geometry"]["type"], "Point")
            lon, lat = feature["geometry"]["coordinates"]
            self.assertGreaterEqual(lon, -180.0)
            self.assertLessEqual(lon, 180.0)
            self.assertGreaterEqual(lat, -90.0)
            self.assertLessEqual(lat, 90.0)
            self.assertIn("pick_index", feature["properties"])
            self.assertIn("region", feature["properties"])

    @add_server_url_to_docstring()
    def test_default_query(self):
        """-   testing {}/earth/get_magnetic_picks/"""
        data = self._get({})
        self._check_feature_collection(data)
        self.assertEqual(data["region"], "all")
        self.assertGreater(data["total_matched"], 0)
        # the default page size caps the response
        self.assertLessEqual(data["returned"], 10000)

    def test_small_range(self):
        """-   testing /earth/get_magnetic_picks/?start_index=0&end_index=10"""
        data = self._get({"start_index": 0, "end_index": 10})
        self._check_feature_collection(data)
        self.assertEqual(data["returned"], 10)
        indices = [f["properties"]["pick_index"] for f in data["features"]]
        self.assertEqual(indices, sorted(indices))

    def test_ranges_are_stable_and_contiguous(self):
        """-   testing that start_index/end_index page through the picks without gaps or overlaps"""
        first = self._get({"start_index": 0, "end_index": 50})
        second = self._get({"start_index": 50, "end_index": 100})
        whole = self._get({"start_index": 0, "end_index": 100})

        paged = [f["properties"]["pick_index"] for f in first["features"]] + [
            f["properties"]["pick_index"] for f in second["features"]
        ]
        self.assertEqual(
            paged, [f["properties"]["pick_index"] for f in whole["features"]]
        )
        self.assertEqual(len(set(paged)), len(paged))

    def test_each_region(self):
        """-   testing /earth/get_magnetic_picks/?region=... for every region"""
        region_totals = {}
        for region in REGIONS:
            data = self._get({"region": region, "end_index": 100})
            self._check_feature_collection(data)
            self.assertEqual(data["region"], region)
            self.assertGreater(data["total_matched"], 0)
            region_totals[region] = data["total_matched"]
            for feature in data["features"]:
                self.assertEqual(feature["properties"]["region"], region)

        # the four regions partition the whole data set
        everything = self._get({"end_index": 1})
        self.assertEqual(sum(region_totals.values()), everything["total_matched"])

    def test_region_alias(self):
        """-   testing /earth/get_magnetic_picks/?region=AtlanticOcean   (a GSFML file name as the region)"""
        data = self._get({"region": "AtlanticOcean", "end_index": 10})
        self.assertEqual(data["region"], "atlantic")
        for feature in data["features"]:
            self.assertEqual(feature["properties"]["region"], "atlantic")

    def test_age_range(self):
        """-   testing /earth/get_magnetic_picks/?min_age=10&max_age=20"""
        data = self._get({"min_age": 10, "max_age": 20, "end_index": 500})
        self._check_feature_collection(data)
        self.assertGreater(data["returned"], 0)
        for feature in data["features"]:
            age = feature["properties"]["geek2007"]
            self.assertIsNotNone(age)
            self.assertGreaterEqual(age, 10.0)
            self.assertLessEqual(age, 20.0)

    def test_age_range_narrows_the_result(self):
        """-   testing that an age range returns fewer picks than no age range"""
        unfiltered = self._get({"end_index": 1})
        filtered = self._get({"min_age": 10, "max_age": 20, "end_index": 1})
        self.assertLess(filtered["total_matched"], unfiltered["total_matched"])
        self.assertGreater(filtered["total_matched"], 0)

    def test_region_and_age_range_together(self):
        """-   testing /earth/get_magnetic_picks/?region=pacific&min_age=0&max_age=5"""
        data = self._get(
            {"region": "pacific", "min_age": 0, "max_age": 5, "end_index": 200}
        )
        self._check_feature_collection(data)
        for feature in data["features"]:
            self.assertEqual(feature["properties"]["region"], "pacific")
            self.assertLessEqual(feature["properties"]["geek2007"], 5.0)

    def test_start_index_past_the_end(self):
        """-   testing a start_index beyond the last pick returns an empty feature collection"""
        everything = self._get({"end_index": 1})
        total = everything["total_matched"]
        data = self._get({"start_index": total + 10, "end_index": total + 20})
        self.assertEqual(data["returned"], 0)
        self.assertEqual(data["features"], [])
        self.assertEqual(data["total_matched"], total)


if __name__ == "__main__":
    unittest.main()
