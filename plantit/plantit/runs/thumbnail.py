from imagekit import ImageSpec
from imagekit.processors import ResizeToFill


class Thumbnail(ImageSpec):
    processors = [ResizeToFill(35, 35)]
    format = 'JPEG'
    options = {'quality': 60}
