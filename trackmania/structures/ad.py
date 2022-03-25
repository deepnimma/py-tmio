__all__ = ("Ad",)


class Ad:
    """
    The Maniapub.

    Parameters
    ----------
    cp_image : str
        The 64x10 image URL of this ad (shown on Start, CPs and Finish)
    display_format : str
        The display format of this screen (2x3 vertical image by default)
    image : str
        The 16x9 image URL of this ad (shown on the big screen)
    media : str
        The media of this ad (mostly the vertical image)
    name : str
        The name of this ad
    type : str
        The type of this ad
    uid : str
        The unique ID of this ad
    url : str
        The URL of this ad
    vertical_image : str
        The vertical image URL of this ad (shown on the vertical screen)

    Returns
    -------

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
        """Constructor."""
        self.cp_image = cp_image
        self.display_format = display_format
        self.image = image
        self.media = media
        self.name = name
        self.type = type
        self.uid = uid
        self.url = url
        self.vertical_image = vertical_image
