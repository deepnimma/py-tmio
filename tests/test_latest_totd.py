import asyncio
import json
import unittest

from aioresponses import aioresponses

from trackmania import Client
from trackmania.managers import totd_manager


class TestLatestTOTD(unittest.TestCase):
    @aioresponses()
    def test_latest(self, mocked):
        Client.user_agent = "NottCurious#4351 | py-trackmania.io Testing Suite"
        with open("./tests/data/latest_totd.json", "r", encoding="UTF-8") as file:
            mocked.get("https://trackmania.io/api/totd/0", payload=json.load(file))

        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(totd_manager.totd())

        self.assertEqual(resp.campaign_id, 21912)
        self.assertEqual(resp.map_author_id, "711036bf-d90b-4fa4-9be5-964eb3912256")
        self.assertEqual(resp.map_name, "$sFrosty creek")
        self.assertEqual(resp.map_type, "TrackMania\TM_Race")

        self.assertEqual(resp.medal_times.bronze_score, 64000)
        self.assertEqual(resp.medal_times.silver_score, 51000)
        self.assertEqual(resp.medal_times.gold_score, 45000)
        self.assertEqual(resp.medal_times.author_score, 42051)

        self.assertEqual(resp.map_id, "f301c6e6-b608-4e20-a0ae-ed48aef8b29d")
        self.assertEqual(resp.map_uid, "E14e8D93S7QI2_xinrM6ZxWlSc")
        self.assertEqual(resp.timestamp, "2022-03-03T14:17:03+00:00")
        self.assertEqual(
            resp.file_url,
            "https://prod.trackmania.core.nadeo.online/storageObjects/583bb411-6e80-4cf0-8b76-954f72bf1cb7",
        )
        self.assertEqual(
            resp.thumbnail_url,
            "https://prod.trackmania.core.nadeo.online/storageObjects/ba5d860b-ef42-4115-a7d0-d53a2df4313a.jpg",
        )
        self.assertEqual(resp.week_day, 3)
        self.assertEqual(resp.month_day, 10)
        self.assertEqual(resp.leaderboard_uid, "5b520978-749c-45a9-824a-e42813edb5b6")
