import cv2
import numpy as np

# Gray Level Transform
## Linear gray level transformation
def linear_gray_level_transformation(img, alpha, beta):
    new_img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
    return new_img

## Piecewise_linear_transformation
def piecewise_linear_transformation(img, threshold, low_slope, high_slope, intercept_low=0, intercept_high=0):
    new_img = img.copy()
    lower_mask = new_img < threshold
    higher_mask = new_img >= threshold
    new_img[lower_mask] = np.clip(low_slope * img[lower_mask] + intercept_low, 0, 255)
    new_img[higher_mask] = np.clip(high_slope * img[higher_mask] + intercept_high, 0, 255)
    return new_img

## Logarit
def logarithmic_transformation(img, constant=1):
     # Adding 1 to the image to avoid log(0)
    img = np.float32(img) + 1  # Convert to float to avoid overflow issues during log computation

    # Apply the logarithmic transformation
    log_image = constant * np.log(img)

    # Normalize the output to ensure it lies in the range 0-255
    log_image = cv2.normalize(log_image, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    return log_image

## Gamma
def adjust_gamma(img, gamma=1.0):
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    
    gamma_corrected = cv2.LUT(img, table)
    return gamma_corrected

# Histogram
## HE
def hist_equalization(img):
    """ Normal Histogram Equalization

    Args:
        img : image input with single channel

    Returns:
        : Equalized Image
    """
    array = np.asarray(img)
    bin_cont = np.bincount(array.flatten(), minlength=256)
    pixels = np.sum(bin_cont)
    bin_cont = bin_cont / pixels
    cumulative_sumhist = np.cumsum(bin_cont)
    map = np.floor(255 * cumulative_sumhist).astype(np.uint8)
    arr_list = list(array.flatten())
    eq_arr = [map[p] for p in arr_list]
    arr_back = np.reshape(np.asarray(eq_arr), array.shape)
    return arr_back

## AHE
def apply_ahe(img, tile_grid_size=(8, 8)):
    # Function to apply AHE on a single channel
    def ahe_channel(channel):
        height, width = channel.shape
        x_tiles = int(np.ceil(width / tile_grid_size[0]))
        y_tiles = int(np.ceil(height / tile_grid_size[1]))
        output_channel = np.zeros_like(channel)

        for y in range(y_tiles):
            for x in range(x_tiles):
                start_x = x * tile_grid_size[0]
                start_y = y * tile_grid_size[1]
                end_x = min(start_x + tile_grid_size[0], width)
                end_y = min(start_y + tile_grid_size[1], height)

                tile = channel[start_y:end_y, start_x:end_x]
                equalized_tile = cv2.equalizeHist(tile)
                output_channel[start_y:end_y, start_x:end_x] = equalized_tile

        return output_channel

    # Check if the image is grayscale or color
    if len(img.shape) == 2:
        # Grayscale image
        return ahe_channel(img)
    elif len(img.shape) == 3:
        # Color image, apply AHE to each channel
        channels = cv2.split(img)
        equalized_channels = [ahe_channel(channel) for channel in channels]
        return cv2.merge(equalized_channels)
    
## CLAHE
def apply_clahe(img, clip_limit=2.0, tile_grid_size=(8, 8)):
    # Check if the image is grayscale; if not, convert to grayscale
    if len(img.shape) > 2 and img.shape[2] == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Create a CLAHE object
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)

    # Apply CLAHE to the grayscale image
    clahe_img = clahe.apply(img)

    return clahe_img

# Retinex
## SSR
def single_scale_retinex(img, sigma):
    retinex = cv2.log(cv2.add(np.float64(img), 1.0)) - cv2.log(cv2.GaussianBlur(np.float64(img), (0, 0), sigma) + 1.0)
    retinex_normalized = ((retinex - retinex.min()) / (retinex.max() - retinex.min())) * 255.0
    return retinex_normalized.astype(np.uint8)

## MSR
def multi_scale_retinex(img, sigma_list):
    retinex = np.zeros_like(np.float64(img))
    for sigma in sigma_list:
        retinex += single_scale_retinex(img, sigma)
    retinex = ((retinex - retinex.min()) / (retinex.max() - retinex.min())) * 255.0
    return retinex.astype(np.uint8)

## MSRCR
def simplest_color_balance(img, low_clip, high_clip):
    total = img.shape[0] * img.shape[1]
    for i in range(img.shape[2]):
        unique, counts = np.unique(img[:, :, i], return_counts=True)
        current = 0
        for u, c in zip(unique, counts):
            if current < low_clip * total:
                low_val = u
            if current < high_clip * total:
                high_val = u
            current += c
        img[:, :, i] = np.maximum(np.minimum(img[:, :, i], high_val), low_val)
    return img

def MSRCR(img, sigma_list):
    img = np.float64(img) + 1.0
    img_retinex = multi_scale_retinex(img, sigma_list)
    img_color = simplest_color_balance(img_retinex, 0.01, 0.99)
    for i in range(img.shape[2]):
        img_color[:, :, i] = (img_color[:, :, i] - np.min(img_color[:, :, i])) / (np.max(img_color[:, :, i]) - np.min(img_color[:, :, i])) * 255
    img_color = np.uint8(np.minimum(np.maximum(img_color, 0), 255))
    return img_color

