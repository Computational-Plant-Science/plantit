import io

import imageio

from .segmentation import calculateMask

def segment(imgFile,threshold):
    """
        Args:
            img (File like object): image to segment (Can be any format supported by imageio)
            threshold (float): the segmentation threshold as used by DIRT

        returns (io.BytesIO): segmented image
    """
    inImg = imageio.imread(imgFile, as_gray=True)
    outImg = io.BytesIO()

    imageio.imwrite(outImg,
                    calculateMask(inImg, mask_threshold=threshold),
                    format="JPEG-PIL")

    return outImg
