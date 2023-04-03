import cv2
import numpy as np
from skimage.morphology import skeletonize
import matplotlib.pyplot as plt
 
image = cv2.imread('out2.png',cv2.IMREAD_UNCHANGED)
alpha_channel = image[:, :, 3]
_, mask = cv2.threshold(alpha_channel, 254, 255, cv2.THRESH_BINARY)  # binarize mask
color = image[:, :, :3]
img = cv2.bitwise_not(color, mask=mask)

skeleton = skeletonize(img)
print("half")
skeleton_lee = skeletonize(img, method='lee')

print(skeleton_lee)

fig, axes = plt.subplots(1, 3, figsize=(8, 4), sharex=True, sharey=True)
ax = axes.ravel()

ax[0].imshow(img, cmap=plt.cm.gray)
ax[0].set_title('original')
ax[0].axis('off')

ax[1].imshow(skeleton, cmap=plt.cm.gray)
ax[1].set_title('skeletonize')
ax[1].axis('off')

ax[2].imshow(skeleton_lee, cmap=plt.cm.gray)
ax[2].set_title('skeletonize (Lee 94)')
ax[2].axis('off')

fig.tight_layout()
plt.show()
plt.imsave('./skel.png',skeleton_lee)


######

"""
img = cv2.imread('./skel.png', 0)
img = cv2.bitwise_not(img)

plt.imshow(img)
plt.show()

result_fill = np.ones(img.shape, np.uint8) * 255
result_borders = np.zeros(img.shape, np.uint8)

# the '[:-1]' is used to skip the contour at the outer border of the image
contours,hy = cv2.findContours(img, cv2.RETR_LIST,
                            cv2.CHAIN_APPROX_SIMPLE)
print(contours)
# fill spaces between contours by setting thickness to -1
cv2.drawContours(result_borders, contours, -1, 0, 1)

# xor the filled result and the borders to recreate the original image
result = result_fill ^ result_borders

# prints True: the result is now exactly the same as the original
print(np.array_equal(result, img))

cv2.imwrite('contours.png', result)
"""