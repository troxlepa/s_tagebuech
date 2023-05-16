import cv2
import numpy as np

def get_horizont(input_file,iterations):
    img = cv2.imread(input_file,cv2.IMREAD_UNCHANGED)
    alpha_channel = img[:, :, 3]
    _, mask = cv2.threshold(alpha_channel, 254, 255, cv2.THRESH_BINARY)  # binarize mask
    color = img[:, :, :3]
    img = cv2.bitwise_not(cv2.bitwise_not(color), mask=mask)
    kernel = np.ones((9, 9), np.uint8)
    
    img_dilation = cv2.dilate(img, kernel, iterations=iterations)
    img_dilation.astype(np.uint8)
    cv2.floodFill(img_dilation, None, seedPoint=(100,100), newVal=128, loDiff=0, upDiff=0)

    rem_kernel = np.ones((2,2),np.uint8)

    mask = cv2.inRange(img_dilation, 128, 128)
    mask = cv2.erode(mask, rem_kernel, iterations=1)
    mask = cv2.dilate(mask, rem_kernel, iterations=1)
    mask = cv2.dilate(mask, kernel, iterations=iterations)
    mask = cv2.bitwise_not(mask)
    return mask

def run():
    input_file = './out4.png'
    mask = get_horizont(input_file,10)
    cv2.imshow('Dilation', mask)
    cv2.waitKey(0)

if __name__ == "__main__":
    run()
