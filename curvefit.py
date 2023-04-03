import cv2
import numpy as np
from skimage.morphology import skeletonize
import matplotlib.pyplot as plt
from scipy.ndimage.measurements import label
from scipy.special import comb

def bernstein_poly(i, n, t):
    """
     The Bernstein polynomial of n, i as a function of t
    """

    return comb(n, i) * ( t**(n-i) ) * (1 - t)**i


def bezier_curve(points, nTimes=1000):
    """
       Given a set of control points, return the
       bezier curve defined by the control points.

       points should be a list of lists, or list of tuples
       such as [ [1,1], 
                 [2,3], 
                 [4,5], ..[Xn, Yn] ]
        nTimes is the number of time steps, defaults to 1000

        See http://processingjs.nihongoresources.com/bezierinfo/
    """

    nPoints = len(points)
    xPoints = np.array([p[0] for p in points])
    yPoints = np.array([p[1] for p in points])

    t = np.linspace(0.0, 1.0, nTimes)

    polynomial_array = np.array([ bernstein_poly(i, nPoints-1, t) for i in range(0, nPoints)   ])

    xvals = np.dot(xPoints, polynomial_array)
    yvals = np.dot(yPoints, polynomial_array)

    return xvals, yvals
if __name__ == "__main__":
    img = cv2.imread('skel.png',0)
    labeled, ncomponents = label(img, np.ones((3,3)).astype(np.uint8))

    #indices = np.indices(img.shape).T[:,:,[1, 0]]
    #print(indices[labeled == 1])
    pts = np.argwhere(labeled == 6)

    nPoints = pts.shape[0]
    points = pts
    xpoints = [p[0] for p in points]
    ypoints = [p[1] for p in points]

    xvals, yvals = bezier_curve(points, nTimes=1000)
    plt.plot(xvals, yvals)
    plt.plot(xpoints, ypoints, "ro")
    """
    for nr in range(len(points)):
        plt.text(points[nr][0], points[nr][1], nr)
    """

    plt.show()

"""
for i in ncomponents:
    print(np.argwhere(labeled == 1))
"""