#!/usr/bin/python2.6 -W ignore::DeprecationWarning
# -*- coding: utf-8 -*-
# Author: Fernando Serboncini <fserb@fserb.com.br>

"""

"""

import sys
import os
import math
import shutil
import tempfile
from subprocess import Popen
from PIL import Image
import pyPdf
import base64
import StringIO

TARGET_WIDTH = 600

def dump_page_ppm(pdf, p):
  page = pdf.getPage(p)
  width = int(round(page.aspect*float(page.mediaBox[2] - page.mediaBox[0])))
  height = int(round(page.aspect*float(page.mediaBox[3] - page.mediaBox[1])))
  
  pdftoppm = Popen(["pdftoppm", 
                    "-f", str(p+1),
                    "-l", str(p+1),
                    "-scale-to-x", str(width),
                    "-scale-to-y", str(height),
                    pdf.stream.name,
                    "dump"])
  pdftoppm.communicate()

  np = int(math.ceil(math.log(pdf.numPages, 10)))
  ppmfile = "dump-%0*d.ppm" % (np, p+1)
  return Image.open(ppmfile)

def rescale_rect(page, rect):
  height = float(page.mediaBox[3] - page.mediaBox[1])
  return [ int(math.floor(float(rect[0])*page.aspect)),
           int(math.floor(height - float(rect[3]))*page.aspect),
           int(math.ceil(float(rect[2])*page.aspect)),
           int(math.ceil(height - float(rect[1]))*page.aspect) ]

def main(argv):
  if len(argv) != 3:
    print "Usage: %s [file.pdf] [output.html]"
    return 1
  pdf_file = os.path.abspath(argv[1])
  output_file = os.path.abspath(argv[2])

  cwd = os.getcwd()
  workdir = tempfile.mkdtemp()
  os.chdir(workdir)
  try:
    pdf = pyPdf.PdfFileReader(file(pdf_file, "rb"))
    out = file(output_file, 'wt')
    out.write(HTML_HEADER)

    for i in range(pdf.numPages):

      page = pdf.getPage(i)
      width = float(page.mediaBox[2] - page.mediaBox[0])
      page.aspect = 1.25*float(TARGET_WIDTH)/width
      if not '/Annots' in page:
        continue

      dump = None
      for io in page['/Annots']:
        o = pdf.getObject(io)
        subtype = o['/Subtype']

        if subtype in ['/Link']:
          continue

        if dump is None:
          out.write(HTML_PAGE_BEGIN.format(page=str(i+1)))
          dump = dump_page_ppm(pdf, i)

        if subtype == '/Highlight':
          f = StringIO.StringIO()
          r = rescale_rect(page, o['/Rect'])
          dump.crop(rescale_rect(page, o['/Rect'])).save(f, "PNG")
          high = base64.b64encode(f.getvalue()).strip()
          out.write(HTML_IMG_ANNOTATION.format(content=high))
        else:
          print subtype

      if dump is not None:
        out.write(HTML_PAGE_END)
    
    out.write(HTML_FOOTER)
    out.close()
  finally:
    os.chdir(cwd)
    shutil.rmtree(workdir)

HTML_HEADER = """
<!doctype html>
<html><head>
<title>PDF Annotations dump</title>
<style>
.an img {
  padding: 5px;
  border: 10px;
  border: 1px solid #ccc;
}

</style>
</head>
<body>
"""

HTML_FOOTER = """
</body></html>
"""

HTML_PAGE_BEGIN = """
<div class="page"><h2>{page}</h2>
"""

HTML_PAGE_END = """
</div>
"""

HTML_IMG_ANNOTATION = """
<div class="an"><img src="data:image/png;base64,{content}"></div>
"""

if __name__ == '__main__':
  sys.exit(main(sys.argv))

