import numpy as np
import cv2


def get_connections(image):
    alpha_channel = image[:, :, 3]
    _, mask = cv2.threshold(alpha_channel, 254, 255, cv2.THRESH_BINARY)  # binarize mask
    color = image[:, :, :3]
    image = cv2.bitwise_not(color, mask=mask)
    cv2.imshow('test',image)
    cv2.waitKey(0)
    l = image[:,4]
    r = image[:,-4]
    print(l.sum())
    return l.nonzero()[0],r.nonzero()[0]


def get_uni(arr):
    num = -1
    cnt = 0
    last = -1
    res = []
    for i in arr:
        if num == -1:
            num = 1
            cnt = i
            last = i
            continue
        if i <= last + 1:
            num += 1
            cnt += i
            last = i
        else:
            res.append(cnt // num)
            last = i
            num = 1
            cnt = i
    if num != -1: res.append(cnt // num)
    return res

if __name__ == "__main__":
    img = cv2.imread('./out2.png',cv2.IMREAD_UNCHANGED)
    left,right = get_connections(img)
    left = get_uni(left)
    right = get_uni(right)
    print(left,right)
