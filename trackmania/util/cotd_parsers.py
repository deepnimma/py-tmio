from typing import Dict, List

from ..structures.cotd import COTD, _BestData, _COTDStats


def parse_cotd(cotd_page_data: Dict) -> Dict:
    """
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
    cotds = _parse_cotd_list(cotd_page_data["cotds"])
    stats = _parse_cotd_stats(cotd_page_data["stats"])

    return {"cotds": cotds, "stats": stats}


def _parse_cotd_list(cotd_list: List[Dict]) -> List[COTD]:
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


def _parse_cotd_stats(cotd_stats: Dict) -> _COTDStats:
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
