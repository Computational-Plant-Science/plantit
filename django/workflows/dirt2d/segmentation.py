import mahotas as m
import numpy as np
import scipy.ndimage

"""
    Extracted from the Masking module of https://github.com/Computational-Plant-Science/DIRT
    Updated to work with python3 and the latest numpy and scipy
"""

def threshold_adaptive(image, block_size, method='gaussian', offset=0,
                   mode='reflect', param=None):
    thresh_image = np.zeros(image.shape, 'double')
    if method == 'generic':
        scipy.ndimage.generic_filter(image, param, block_size,
            output=thresh_image, mode=mode)
    elif method == 'gaussian':
        if param is None:
            # automatically determine sigma which covers > 99% of distribution
            sigma = (block_size - 1) / 6.0
        else:
            sigma = param
        scipy.ndimage.gaussian_filter(image, sigma, output=thresh_image,
            mode=mode)
    elif method == 'mean':
        mask = 1. / block_size * np.ones((block_size,))
        # separation of filters to speedup convolution
        scipy.ndimage.convolve1d(image, mask, axis=0, output=thresh_image,
            mode=mode)
        scipy.ndimage.convolve1d(thresh_image, mask, axis=1,
            output=thresh_image, mode=mode)
    elif method == 'median':
        scipy.ndimage.median_filter(image, block_size, output=thresh_image,
            mode=mode)

    return image > (thresh_image - offset)

def calculateMask(img, mask_threshold=1):
    img = img.astype(np.uint8)

    if len(np.unique(img))<=2:
        idx1=np.where(img==np.unique(img)[0])
        idx2=np.where(img==np.unique(img)[1])
        img[idx1]=False
        img[idx2]=True
    else:
        T=m.otsu(img,ignore_zeros=False)
        T=T*mask_threshold
        img = threshold_adaptive(img, 80, 'gaussian',offset=-20,param=T)
        img = m.morph.open(img)

    img = m.morph.close(img)
    ''' just a quick fix of the dilation function that caused the binary image to consist of 0 and 2. Now It should be a real binary image '''
    idx1=np.where(img==np.unique(img)[0])
    idx2=np.where(img==np.unique(img)[1])
    img[idx1]=0
    img[idx2]=255

    w,h=img.shape
    img[0,:]=0
    img[:,0]=0
    img[w-1,:]=0
    img[:,h-1]=0
    
    return img.astype(np.uint8) * 255
