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
