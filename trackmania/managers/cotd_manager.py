import json
from contextlib import suppress
from typing import List, Dict

import redis

import logging

from ..api import APIClient
from ..config import Client
from ..constants import TMIO
from ..structures.cotd import PlayerCOTD, _BestData, _COTDStats, COTD

_log = logging.getLogger(__name__)


async def get_player_cotd(player_id: str, page: int = 0) -> PlayerCOTD:
    """
    .. versionadded:: 0.2.1

    Gets the player cotd data. Function will sleep for 120s if it uses too many requests.

    Parameters
    ----------
    player_id: str
        The player id.
    page : int, optional
        Which page of cotd data to get.
        defaults to 0

    Returns
    -------
    :class:`PlayerCOTD`
        The COTD Data as a :class:`PlayerCOTD` object.

    Raises
    ------
    ValueError
        If the given page is invalid.
    """
    cache_client = redis.Redis(
        host=Client.REDIS_HOST,
        port=Client.REDIS_PORT,
        db=Client.REDIS_DB,
        password=Client.REDIS_PASSWORD,
    )

    if page < 0:
        raise ValueError("Page must be greater than or equal to 0")

    with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
        if cache_client.exists(f"{player_id}|cotd|{page}"):
            _log.debug(f"{player_id} page: {page} was cached.")
            if page != -1:
                return PlayerCOTD(
                    **_parse_cotd(
                        json.loads(cache_client.get(f"{player_id}|cotd|{page}"))
                    )
                )

    api_client = APIClient()

    _log.debug(
        f"Sending GET request to {TMIO.build([TMIO.TABS.PLAYER, player_id, TMIO.TABS.COTD, str(page)])}"
    )
    cotd_page_resp = await api_client.get(
        TMIO.build([TMIO.TABS.PLAYER, player_id, TMIO.TABS.COTD, str(page)])
    )

    with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
        cache_client.set(f"{player_id}|cotd|{page}", json.dumps(cotd_page_resp))
        _log.debug(f"Cached {player_id} page: {page}")

    await api_client.close()
    return PlayerCOTD(**_parse_cotd(cotd_page_resp))


def _parse_cotd(cotd_page_data: Dict) -> Dict:
    """
    .. versionadded:: 0.2.0

    Parses a COTD JSON File into a proper Kwargs Dict for a :class:`PlayerCOTD` object.

    Parameters
    ----------
    cotd_page_data: Dict
        The COTD Page data.

    Returns
    -------
    Dict
        The kwargs formatted Dict.
    """
    cotds = __parse_cotd_list(cotd_page_data["cotds"])
    stats = __parse_cotd_stats(cotd_page_data["stats"])

    return {"cotds": cotds, "stats": stats}


def __parse_cotd_list(cotd_list: List[Dict]) -> List[COTD]:
    cotds = list()

    for cotd in cotd_list:
        kwargs = {
            "cotd_id": cotd["id"],
            "timestamp": cotd["timestamp"],
            "name": cotd["name"],
            "div": cotd["div"],
            "rank": cotd["rank"],
            "div_rank": cotd["divrank"],
            "score": cotd["score"],
            "total_players": cotd["totalplayers"],
        }

        cotds.append(COTD(**kwargs))

    return cotds


def __parse_cotd_stats(cotd_stats: Dict) -> _COTDStats:
    best_primary = __parse_best(cotd_stats["bestprimary"])
    best_overall = __parse_best(cotd_stats["bestoverall"])

    kwargs = {
        "best_primary": best_primary,
        "best_overall": best_overall,
        "total_wins": cotd_stats["totalwins"],
        "total_div_wins": cotd_stats["totaldivwins"],
        "avg_rank": cotd_stats["avgrank"],
        "avg_div_rank": cotd_stats["avgdivrank"],
        "avg_div": cotd_stats["avgdiv"],
        "win_streak": cotd_stats["winstreak"],
        "div_win_streak": cotd_stats["divwinstreak"],
    }

    return _COTDStats(**kwargs)


def __parse_best(best_data: Dict) -> _BestData:
    kwargs = {
        "best_rank": best_data["bestrank"],
        "best_rank_time": best_data["bestranktime"],
        "best_rank_div_rank": best_data["bestrankdivrank"],
        "best_div": best_data["bestdiv"],
        "best_div_time": best_data["bestdivtime"],
        "best_rank_in_div": best_data["bestrankindiv"],
        "best_rank_in_div_time": best_data["bestrankindivtime"],
        "best_rank_in_div_div": best_data["bestrankindivdiv"],
    }

    return _BestData(**kwargs)
