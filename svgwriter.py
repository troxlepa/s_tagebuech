import os
import numpy as np
import matplotlib.pyplot as plt
import random
import drawsvg as draw

scales = [0.8,1,4]
amp = [0.4,0.8,1.6]
for i in scales:
    arr = np.arange(0,10,0.1)
    #mat = np.repeat(range,len(scales))
    mat = arr * i
    lst = np.sin(mat)
    lst *= amp[random.randint(0,2)]
    plt.plot(range(100),lst)
plt.show()