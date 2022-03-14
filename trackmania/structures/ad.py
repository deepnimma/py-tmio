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

__all__ = ("Ad",)


class Ad:
    """
    The Maniapub.

    :param cp_image: The 64x10 image URL of this ad (shown on Start, CPs and Finish)
    :type cp_image: str
    :param display_format: The display format of this screen (2x3 vertical image by default)
    :type display_format: str
    :param image: The 16x9 image URL of this ad (shown on the big screen)
    :type image: str
    :param media: The media of this ad (mostly the vertical image)
    :type media: str
    :param name: The name of this ad
    :type name: str
    :param type: The type of this ad
    :type type: str
    :param uid: The unique ID of this ad
    :type uid: str
    :param url: The URL of this ad
    :type url: str
    :param vertical_image: The vertical image URL of this ad (shown on the vertical screen)
    :type vertical_image: str
    """

    def __init__(
        self,
        cp_image: str,
        display_format: str,
        image: str,
        media: str,
        name: str,
        type: str,
        uid: str,
        url: str,
        vertical_image: str,
    ):
        self.cp_image = cp_image
        self.display_format = display_format
        self.image = image
        self.media = media
        self.name = name
        self.type = type
        self.uid = uid
        self.url = url
        self.vertical_image = vertical_image
