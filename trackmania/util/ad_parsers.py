"""
MIT License

Copyright (c) 2022-present Deepesh Nimma

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from typing import Dict

from ..structures.ad import Ad


def parse_ad(ad: Dict) -> Ad:
    """
    Parses an AD dict to an :class:`Ad` class object.

    :param ad: The ad data as a dict.
    :type ad: :class:`Dict`
    :return: The ad data as an :class:`Ad` object.
    :rtype: :class:`Ad`
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
