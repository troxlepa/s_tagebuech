import cv2
import numpy as np
def get_rect(input_file):
    img = cv2.imread(input_file)
    scale_percent = 50 # percent of original size
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (int(1000 * width/height), 1000)
    if height > 1000:
        # resize image
        img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

    img_gray=cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    ret, thresh = cv2.threshold(img_gray, 100, 255, 0)

    img_hsv=cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    #cv2.imshow("img_hsv", img_hsv)

    # define range of blue color in HSV
    lower_blue = np.array([110,50,50])
    upper_blue = np.array([130,255,255])

    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(img_hsv, lower_blue, upper_blue)



    kernel1 = np.ones((7,7)) 
    kernel1[1:6,1:6] = -10
    
    #mask = cv2.medianBlur(mask, 9)

    filtered = cv2.filter2D(src=mask, ddepth=-1, kernel=kernel1)
    filtered = filtered & thresh
    filtered_rgb = cv2.cvtColor(filtered,cv2.COLOR_GRAY2RGB)


    circles = cv2.HoughCircles(filtered, cv2.HOUGH_GRADIENT, 1, filtered.shape[0] / 8,
                                param1=50, param2=15,
                                minRadius=5, maxRadius=20)

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            center = (i[0], i[1])
            # circle center
            cv2.circle(filtered_rgb, center, 1, (0, 100, 100), 3)
            # circle outline
            radius = i[2]
            cv2.circle(filtered_rgb, center, radius, (255, 0, 255), 3)
    print(circles)
    if len(circles[0]) != 4:
        print(f"ERROR: detected {len(circles)} points")
    circles = circles[0]
    ccc = circles[:,:2]
    xx, yy = zip(*ccc)
    min_x = min(xx); min_y = min(yy); max_x = max(xx); max_y = max(yy)
    bbox = [(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)]
    return bbox,filtered_rgb

def run():
    input_file = './img5.jpg'
    bbox,img = get_rect(input_file)

    #img = cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
    """
    print(x,y,w,h)
    tl = circles[0][:2]
    br = circles[3][:2]
    for circle in circles:
        tl[0] = max(tl[0],circle[0])
        tl[1] = max(tl[1],circle[1])
    """
    cv2.rectangle(img, bbox[0], bbox[2], (255,0,0), 3)
    
    cv2.imshow("detected circles", img)
    cv2.waitKey(0)

if __name__ == "__main__":
    run()