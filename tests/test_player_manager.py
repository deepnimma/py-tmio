import asyncio
import json
import unittest

from aioresponses import aioresponses

from trackmania import Client
from trackmania.managers import PlayerManager


class TestPlayerManager(unittest.TestCase):
    @aioresponses()
    def test_get(self, mocked):
        Client.user_agent = "NottCurious#4351 | py-trackmania.io Testing Suite"
        with open("./tests/data/player_get.json", "r", encoding="UTF-8") as file:
            mocked.get(
                "https://trackmania.io/api/player/b73fe3d7-a92a-4a6d-ab9d-49005caec499",
                payload=json.load(file),
            )

            loop = asyncio.get_event_loop()
            resp = loop.run_until_complete(
                PlayerManager.get("b73fe3d7-a92a-4a6d-ab9d-49005caec499")
            )

            self.assertEqual(resp.club_tag, "$F63W$F971$FCBS$FFFP")
            self.assertEqual(resp.first_login, "2021-02-12T11:04:02+00:00")
            self.assertEqual(resp.player_id, "b73fe3d7-a92a-4a6d-ab9d-49005caec499")
            self.assertEqual(resp.last_club_tag_change, "2022-03-06T15:35:59+00:00")
            self.assertEqual(resp.login, "NottCurious")
            self.assertEqual(resp.name, "NottCurious")
            self.assertEqual(resp.m3v3_data.matchmaking_type, "3v3")
            self.assertEqual(resp.m3v3_data.type_id, 2)
            self.assertEqual(resp.m3v3_data.progression, 2000)
            self.assertEqual(resp.m3v3_data.rank, 4717)
            self.assertEqual(resp.m3v3_data.division, 7)
            self.assertEqual(resp.m3v3_data.min_points, 2000)
            self.assertEqual(resp.m3v3_data.max_points, 2299)
            self.assertEqual(resp.royal_data.matchmaking_type, "Royal")
            self.assertEqual(resp.royal_data.type_id, 3)
            self.assertEqual(resp.royal_data.progression, 0)
            self.assertEqual(resp.royal_data.rank, 30913)
            self.assertEqual(resp.royal_data.division, 1)
            self.assertEqual(resp.royal_data.min_points, 0)
            self.assertEqual(resp.royal_data.max_points, 1)

            zone_strs = ("India", "Asia", "World")
            ranks = (8, 58, 4259)
            for i, zone in enumerate(resp.zone):
                self.assertEqual(zone.zone, zone_strs[i])
                self.assertEqual(zone.rank, ranks[i])
            self.assertEqual(resp.meta.display_url, None)
            self.assertEqual(resp.meta.in_nadeo, False)
            self.assertEqual(resp.meta.in_tmgl, False)
            self.assertEqual(resp.meta.in_tmio_dev_team, False)
            self.assertEqual(resp.meta.in_tmwc21, False)
            self.assertEqual(resp.meta.is_sponsor, False)
            self.assertEqual(resp.meta.sponsor_level, 0)
            self.assertEqual(resp.meta.twitch, "NottCurious")
            self.assertEqual(resp.meta.twitter, "nottcurious")
            self.assertEqual(resp.meta.youtube, "UCZV9i9_sgXwIdN6cy1uFkyw")
            self.assertEqual(resp.meta.vanity, None)
            self.assertEqual(resp.trophies.echelon, 6)
            self.assertEqual(resp.trophies.last_change, "2022-03-07T04:02:19+00:00")
            self.assertEqual(resp.trophies.points, 3290258)
            self.assertEqual(
                resp.trophies.trophies, [3378, 3868, 5482, 570, 163, 5, 0, 0, 0]
            )
            self.assertEqual(
                resp.trophies.player_id, "b73fe3d7-a92a-4a6d-ab9d-49005caec499"
            )


if __name__ == "__main__":
    Client.user_agent = "NottCurious#4351 | py-trackmania.io Testing Suite"
    unittest.main()
