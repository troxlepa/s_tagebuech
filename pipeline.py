import pyvips
from PIL import Image
import cv2
import numpy as np
from skimage.morphology import skeletonize
import matplotlib.pyplot as plt
from potrace import Bitmap

from potrace import POTRACE_CORNER, Path
from horizont import get_horizont

from rectcrop import get_rect

import subprocess
import time

import random
import json

import os



def run_external(base_path,num,title_,subtitle_,fgcol_,bgcol_):
    nr = str(num).zfill(4)
    config = [nr,17,7,False,2,1,1,True,True,True,False,fgcol_]

    input_file = f'{base_path}/inputs/{nr.zfill(4)}.jpg'
    output_file = f'{base_path}/tmp/out.svg'
    output_file_png = f'{base_path}/tmp/out.png'
    output_file_pnm = f'{base_path}/tmp/out.pnm'
    output_file_svg = f'{base_path}/outputs/{nr.zfill(4)}.svg'
    mask_file = f'{base_path}/masks/tmp_mask.png'
    print(input_file)
    print(os.listdir('/app/static/inputs'))
    if not os.path.exists(input_file):
        print("ERROR: file not found")

    fns = [input_file,output_file,output_file_png,output_file_pnm,output_file_svg,mask_file]

    output_svg = run_pipeline(fns,config)
    pid = nr
    ts = int(time.time())
    title = title_
    subtitle = subtitle_
    data = {'sid':pid[:4],'id':pid,'timestamp':ts,'title':title,'subtitle':subtitle,'fgcol':fgcol_,'bgcol':bgcol_}
    return output_svg,data

def append_svg(image,path: Path,color):
    ret_code = ""
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
    ret_code += f'<path stroke="none" fill="{color}" style="filter: drop-shadow(-20px -20px 20px rgb(0 0 0 / 0.5))" fill-rule="evenodd" d="{"".join(parts)}"/>'
    return ret_code

def backend_svg(args, image, path: Path, include_drop_shadow = False):
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
        if include_drop_shadow:
            fp.write(
                '<path stroke="none" fill="%s" style="filter: drop-shadow(-10px -20px 15px rgb(0 0 0 / 0.5))" fill-rule="evenodd" d="%s"/>'
                % (args['color'], "".join(parts))
            )
        else:
            fp.write(
                '<path stroke="none" fill="%s" fill-rule="evenodd" d="%s"/>'
                % (args['color'], "".join(parts))
            )
        fp.write("</svg>")
def run_pipeline(fns,config):

    num,ada_thres,ada_size,rot,iterations,crop_l,crop_r,do_prep,do_mask,write_svg,show_plt,fgcol = config
    input_file,output_file,output_file_png,output_file_pnm,output_file_svg,mask_file = fns

    if do_prep:
        img = cv2.imread(input_file,0)
        scale_percent = 50 # percent of original size
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        dim = (int(1000 * width/height), 1000)
        if height > 1000:
            # resize image
            img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
        if rot:
            img = cv2.rotate(img,rotateCode=cv2.ROTATE_90_COUNTERCLOCKWISE)
        img = cv2.medianBlur(img,3)
        img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, ada_thres, ada_size)
        img = img[:, crop_l:-crop_r]
        #img = cv2.resize(img, (0,0), fx=0.5, fy=0.5) 
        image = Image.fromarray(img)
        if show_plt:
            plt.imshow(image)
            plt.show()
        bm = Bitmap(image, blacklevel=0.5)
        plist = bm.trace(alphamax=2,turdsize=2)
        args = {}
        args['output'] = output_file
        args['color'] = '#FFFFFF'
        backend_svg(args, image, plist)
        fp = open(args['output'],"r")
        svg_code = fp.read()
        image = pyvips.Image.new_from_file(args['output'], dpi=300)
        image.write_to_file(output_file_png)

    horizont = get_horizont(output_file_png,iterations)
    horizont = cv2.bitwise_not(horizont)
    if show_plt:
        plt.imshow(horizont)
        plt.show()
    plt.imsave(mask_file,horizont)
    bm = Bitmap(horizont, blacklevel=0.5)
    plist = bm.trace(alphamax=1,turdsize=0)
    args = {}
    args['output'] = 'temp.svg'
    args['color'] = '#000000'
    horizont = Image.fromarray(horizont)

    if write_svg:
        img = cv2.imread(output_file_png,0)
        skeleton_lee = skeletonize(img, method='lee')
        skeleton_lee = cv2.bitwise_not(skeleton_lee)
        width = img.shape[1]
        height = img.shape[0]
        cv2.imwrite(output_file_png,skeleton_lee)

        # convert png to pnm
        print(f"converting {output_file_png} to {output_file_pnm}")
        subprocess.run(["convert",output_file_png,output_file_pnm])
        time.sleep(3)
        print("running autotrace...")
        subprocess.run(["autotrace", "--centerline", f"--output-file={output_file_svg}", "--error-threshold=1", "--dpi=72", output_file_pnm])
        print("finished")
        time.sleep(8)
        fp = open(output_file_svg,"r")
        svg_code = fp.read()
        fp.close()
        idx = svg_code.find('<path')
        svg_code = svg_code[idx:]
        newheader = f'<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 20010904//EN" "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd"> <svg width="{width}" height="{height*1.1}" xmlns="http://www.w3.org/2000/svg">'
        style_code = '<style type="text/css"> path{stroke-width:20;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;}</style>'
        if do_mask:
            mask_code = append_svg(horizont,plist,fgcol)
        res_code = newheader + style_code + mask_code + svg_code 
        fpw = open(output_file_svg,"w")
        fpw.write(res_code)
        fpw.close()
        return res_code
    return ""

if __name__ == "__main__":
    num = random.randint(10,14)
    run_external(num,"Test","Subtest")