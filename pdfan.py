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

  width = int(round(page.aspect*float(page.cropBox[2] - page.cropBox[0])))
  height = int(round(page.aspect*float(page.cropBox[3] - page.cropBox[1])))
  
  pdftoppm = Popen(["pdftoppm", 
                    "-f", str(p+1),
                    "-l", str(p+1),
                    "-scale-to-x", str(width),
                    "-scale-to-y", str(height),
                    "-cropbox",
                    "-q",
                    pdf.stream.name,
                    "dump"])
  pdftoppm.communicate()

  np = int(math.ceil(math.log(pdf.numPages, 10)))
  ppmfile = "dump-%0*d.ppm" % (np, p+1)
  return Image.open(ppmfile)


def rescale_rect(page, rect):
  # Rescale to mediaBox, then back to cropBox.

  box = [ float(x) for x in page.cropBox ]
  r = [ float(x) for x in rect ]

  h = box[3] - box[1]
  w = box[2] - box[0]
  asp = page.aspect

  r = [ r[0] - box[0],
        r[1] - box[1],
        r[2] - box[0],
        r[3] - box[1] ]

  final = [ r[0]*asp,
            (h - r[3])*asp,
            r[2]*asp,
            (h - r[1])*asp ]

  final = [ int(math.floor(final[0])),
            int(math.floor(final[1])),
            int(math.ceil(final[2])),
            int(math.ceil(final[3])) ]

  return final

def has_annotation(pdf_file):
  pdf = pyPdf.PdfFileReader(file(pdf_file, "rb"))
  for i in range(pdf.numPages):
    page = pdf.getPage(i)
    if not '/Annots' in page:
      continue
    for io in page['/Annots']:
      o = pdf.getObject(io)
      if o['/Subtype'] in ['/Highlight']:
        return True
  return False

def make_annotation(pdf_file, output_file, title, author):
  cwd = os.getcwd()
  workdir = tempfile.mkdtemp()
  os.chdir(workdir)
  try:
    pdf = pyPdf.PdfFileReader(file(pdf_file, "rb"))
    out = file(output_file, 'wt')
    out.write(HTML_HEADER_BEGIN)
    out.write(HTML_HEADER_END.format(title=title,author=author))

    for i in range(pdf.numPages):

      page = pdf.getPage(i)
      width = float(page.cropBox[2] - page.cropBox[0])
      page.aspect = 1.25*float(TARGET_WIDTH)/width
      if not '/Annots' in page:
        continue


      dump = None
      for io in sorted(page['/Annots'], key=lambda io: -pdf.getObject(io)['/Rect'][3]):
        o = pdf.getObject(io)
        subtype = o['/Subtype']

        if subtype in ['/Link']:
          continue

        if dump is None:
          dump = dump_page_ppm(pdf, i)
          out.write(HTML_PAGE_BEGIN.format(page=str(i+1)))

        if subtype == '/Highlight':
          f = StringIO.StringIO()
          dump.crop(rescale_rect(page, o['/Rect'])).save(f, "PNG")
          high = base64.b64encode(f.getvalue()).strip()
          out.write(HTML_IMG_ANNOTATION.format(content=high))
        else:
          print subtype

      if dump:
        out.write(HTML_PAGE_END)
    
    out.write(HTML_FOOTER)
    out.close()
  finally:
    os.chdir(cwd)
    shutil.rmtree(workdir)


def main(argv):
  if len(argv) != 5:
    print "Usage: %s [file.pdf] [output.html] [title] [author]" % argv[0]
    return 1
  pdf_file = os.path.abspath(argv[1])
  output_file = os.path.abspath(argv[2])
  title = argv[3]
  author = argv[4]
  make_annotation(pdf_file, output_file, title, author)

HTML_HEADER_BEGIN = """<!doctype html>
<html><head>
<style>
body {
  font-family: verdana;
  background-color: #F0f0f0;
}

#header {
  margin: 20px 0 50px 100px;
  width: 600px;
}

#header h1 {
  font-size: 22px;
  margin: 0;
} 

#header h3 {
  font-size: 16px;
  margin: 10px 0 0 0;
}

.page {
  margin: 0 0 15px 0;
}

.page h2 {
  font-size: 18px;
  float: left;
  color: #FFF;
  margin: 0;
  padding: 2px;
  background-color: hsl(0,75%,50%);
  background: -webkit-gradient(linear, left top, right top, color-stop(0%,#f0f0f0),color-stop(20%,hsl(0,75%, 30%)), color-stop(80%,hsl(0,75%,40%)),color-stop(100%,#f0f0f0));
}

.page h2 p {
  margin: 0;
  padding: 0;
  border: 1px solid #EEE;
  padding: 2px 10px;
  width: 50px;
  text-align: right;
}

.an {
  margin: 0 0 5px 100px;
  
}

.an img {
  padding: 10px;
  border: 10px;
  background-color: #FFF;
  border: 1px solid #000;
  box-shadow: 2px 2px 2px #000;
  -moz-box-shadow: 3px 2px 4px #000;
  -webkit-box-shadow: 2px 2px 5px #000;
}
</style>"""

HTML_HEADER_END = """
<title>{title} - {author} [pdfan]</title>
</head>
<body>

<div id="header">
<h1>{title}</h1>
<h3>{author}</h3>
</div>
"""

HTML_FOOTER = """
</body></html>
"""

HTML_PAGE_BEGIN = """
<div class="page"><a name="{page}"><h2><p>{page}</p></h2></a>
"""

HTML_PAGE_END = """
</div>
"""

HTML_IMG_ANNOTATION = """
<div class="an"><img src="data:image/png;base64,{content}"></div>
"""

if __name__ == '__main__':
  sys.exit(main(sys.argv))

