from typing import Dict

from ..structures.ad import Ad


def parse_ad(ad: Dict) -> Ad:
    """
    Parses an AD dict to an :class:`Ad` object.

    Parameters
    ----------
    ad : :class:`Dict`
        The ad data as a dict.

    Returns
    -------
    :class:`Ad`
        The ad data as an :class:`Ad` object.
    """
    ad_data = {
        "cp_image": ad["img64x10"],
        "display_format": ad["displayformat"],
        "image": ad["img16x9"],
        "media": ad["media"],
        "name": ad["name"],
        "type": ad["type"],
        "uid": ad["uid"],
        "url": ad["url"],
        "vertical_image": ad["img2x3"],
    }

    return Ad(**ad_data)
