"""
Plugins must have a register function that accepts **kwargs, (for forwards compatibility).
The value backends will be the dict of backends used by cli. A plugin *should* register
itself as a valid backend.
These are registered in the pip: setup.cfg
[options.entry_points]
cli.backends = SVG = cli.backend_svg:register
"""

import pkg_resources
from PIL import Image
import cv2

from potrace import Bitmap

from potrace import POTRACE_CORNER, Path


ada_thres = 17
ada_size = 21
rot = False
input_file = './img2.jpg'
output_file = './out2.svg'


def register(backends: dict, **kwargs):
    backends["svg"] = backend_svg
    backends["jagged-svg"] = backend_jagged_svg


def backend_svg(args, image, path: Path):
    with open(args['output'], "w") as fp:
        fp.write(
            '<svg version="1.1"' +
            ' xmlns="http://www.w3.org/2000/svg"' +
            ' xmlns:xlink="http://www.w3.org/1999/xlink"' +
            ' width="%d" height="%d"' % (image.width, image.height) +
            ' viewBox="0 0 %d %d">' % (image.width, image.height)
        )
        parts = []
        for curve in path:
            fs = curve.start_point
            parts.append("M%f,%f" % (fs.x, fs.y))
            for segment in curve.segments:
                if len(curve.segments) < 4: continue
                if segment.is_corner:
                    a = segment.c
                    parts.append("L%f,%f" % (a.x, a.y))
                    b = segment.end_point
                    parts.append("L%f,%f" % (b.x, b.y))
                else:
                    a = segment.c1
                    b = segment.c2
                    c = segment.end_point
                    parts.append("C%f,%f %f,%f %f,%f" % (a.x, a.y, b.x, b.y, c.x, c.y))
            parts.append("z")
        fp.write(
            '<path stroke="none" fill="%s" fill-rule="evenodd" d="%s"/>'
            % (args['color'], "".join(parts))
        )
        fp.write("</svg>")


def backend_jagged_svg(args, image, path):
    with open(args.output, "w") as fp:
        fp.write(
            '<svg version="1.1"' +
            ' xmlns="http://www.w3.org/2000/svg"' +
            ' xmlns:xlink="http://www.w3.org/1999/xlink"' +
            ' width="%d" height="%d"' % (image.width, image.height) +
            ' viewBox="0 0 %d %d">' % (image.width, image.height)
        )
        parts = []
        for curve in path:
            parts.append("M")
            for point in curve.decomposition_points:
                parts.append(" %f,%f" % (point.x, point.y))
            parts.append("z")
        fp.write(
            '<path stroke="none" fill="%s" fill-rule="evenodd" d="%s"/>'
            % (args.color, "".join(parts))
        )
        fp.write("</svg>")




img = cv2.imread(input_file,0)
if rot:
    img = cv2.rotate(img,rotateCode=cv2.ROTATE_90_COUNTERCLOCKWISE)
img = cv2.medianBlur(img,5)
img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, ada_thres, ada_size)
image = Image.fromarray(img)
bm = Bitmap(image, blacklevel=0.5)
plist = bm.trace(alphamax=2,turdsize=2)

args = {}
args['output'] = output_file
args['color'] = '#000000'
backend_svg(args, image, plist)