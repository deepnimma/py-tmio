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

__all__ = ("MedalTimes",)


class MedalTimes:
    """Represents the MedalTimes of a map."""

    def __init__(
        self, bronze_score: int, silver_score: int, gold_score: int, author_score: int
    ):
        """
        Constructor for the class.
        """
        self.bronze_score = bronze_score
        self.silver_score = silver_score
        self.gold_score = gold_score
        self.author_score = author_score

    def _format_seconds(self, score: int) -> str:
        """
        Formats the number from milliseconds to minute:sec:millisecond format.

        :param score: The number in milliseconds.
        :type score: int
        :return: The number formatted.
        :rtype: str
        """
        sec, millisecond = divmod(score, 1000)
        minute, sec = divmod(sec, 60)

        return "%01d:%02d.%03d" % (minute, sec, millisecond)

    def bronze_string(self) -> str:
        """
        Gets the bronze medal time as a string.

        :return: The bronze score as a string.
        :rtype: str
        """
        return self._format_seconds(self.bronze_score)

    def silver_string(self) -> str:
        """
        Gets the silver medal time as a string.

        :return: The silver score as a string.
        :rtype: str
        """
        return self._format_seconds(self.silver_score)

    def gold_string(self) -> str:
        """
        Gets the gold medal time as a string.

        :return: The gold score as a string.
        :rtype: str
        """
        return self._format_seconds(self.gold_score)

    def author_string(self) -> str:
        """
        Gets the author medal time as a string.

        :return: The author score as a string.
        :rtype: str
        """
        return self._format_seconds(self.author_score)
