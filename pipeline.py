import pyvips
from PIL import Image
import cv2
from skimage.morphology import skeletonize
import matplotlib.pyplot as plt
from potrace import Bitmap

from potrace import POTRACE_CORNER, Path
from horizont import get_horizont

import subprocess
import time
import os

def run_external(base_path,num,title_,subtitle_,fgcol_,bgcol_,description_,invert_text_,ada_hi_,ada_lo_,iterations_,hscale_,blur_,strokewidth_):
    nr = str(num).zfill(4)
    config = [int(ada_hi_),int(ada_lo_),int(iterations_),fgcol_,hscale_,blur_,strokewidth_]

    input_file = f'{base_path}/tmp/tmpx.jpg'
    output_file = f'{base_path}/tmp/out.svg'
    output_file_png = f'{base_path}/tmp/out.png'
    output_file_pnm = f'{base_path}/tmp/out.pnm'
    output_file_svg = f'{base_path}/tmp/outtmpx.svg'
    mask_file = f'{base_path}/tmp/tmp_mask.png'

    if not os.path.exists(input_file):
        print("ERROR: file not found")

    fns = [input_file,output_file,output_file_png,output_file_pnm,output_file_svg,mask_file]

    output_svg = run_pipeline(fns,config)
    pid = nr
    ts = int(time.time())
    title = title_
    subtitle = subtitle_
    data = {'sid':pid[:4],'id':pid,'timestamp':ts,'title':title,'subtitle':subtitle,'fgcol':fgcol_,'bgcol':bgcol_,'description':description_,'invert_text':invert_text_}
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

def backend_svg(file, color, image, path: Path, include_drop_shadow = False):
    with open(file, "w") as fp:
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
                % (color, "".join(parts))
            )
        else:
            fp.write(
                '<path stroke="none" fill="%s" fill-rule="evenodd" d="%s"/>'
                % (color, "".join(parts))
            )
        fp.write("</svg>")
def run_pipeline(fns,config):

    ada_thres,ada_size,iterations,fgcol,hscale,blur,strokewidth = config
    input_file,output_file,output_file_png,output_file_pnm,output_file_svg,mask_file = fns

    img = cv2.imread(input_file,0)
    hscale = int(hscale)
    aspect = img.shape[1] / img.shape[0]
    wscale = int(hscale * aspect)
    print(img.shape[0],img.shape[1],wscale,hscale)
    img = cv2.resize(img, (wscale,hscale), interpolation = cv2.INTER_AREA)
    img = cv2.medianBlur(img,int(blur))
    img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, ada_thres, ada_size)

    image = Image.fromarray(img)
    bm = Bitmap(image, blacklevel=0.5)
    plist = bm.trace(alphamax=2,turdsize=2)
    color = '#FFFFFF'
    backend_svg(output_file, color, image, plist)
    pyvips.cache_set_max(0)
    image = pyvips.Image.new_from_file(output_file, dpi=300,access="sequential")
    image.write_to_file(output_file_png)
    print('written to',output_file_png)
    horizont = get_horizont(output_file_png,iterations)
    horizont = cv2.bitwise_not(horizont)

    plt.imsave(mask_file,horizont)
    bm = Bitmap(horizont, blacklevel=0.5)
    plist = bm.trace(alphamax=1,turdsize=0)
    horizont = Image.fromarray(horizont)

    img = cv2.imread(output_file_png,0)
    skeleton_lee = skeletonize(img, method='lee')
    skeleton_lee = cv2.bitwise_not(skeleton_lee)
    width = img.shape[1]
    height = img.shape[0]
    cv2.imwrite(output_file_png,skeleton_lee)

    # convert png to pnm
    print(f"converting {output_file_png} to {output_file_pnm}")
    subprocess.run(["convert",output_file_png,output_file_pnm])
    time.sleep(4)
    print("running autotrace...")
    subprocess.run(["autotrace", "--centerline", f"--output-file={output_file_svg}", "--error-threshold=1", "--dpi=72", output_file_pnm])
    print("finished")
    time.sleep(8)
    fp = open(output_file_svg,"r")
    svg_code = fp.read()
    fp.close()
    idx = svg_code.find('<path')
    svg_code = svg_code[idx:]
    newheader = f'<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 20010904//EN" "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd"> <svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">'
    style_code = '<style type="text/css"> path{stroke-width:'+str(int(strokewidth))+';stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;}</style>'

    mask_code = append_svg(horizont,plist,fgcol)
    res_code = newheader + style_code + mask_code + svg_code 
    fpw = open(output_file_svg,"w")
    fpw.write(res_code)
    fpw.close()
    del img
    del image
    del bm
    return res_code