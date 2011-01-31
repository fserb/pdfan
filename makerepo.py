#!/usr/bin/python2.6 -W ignore::DeprecationWarning
# -*- coding: utf-8 -*-
# Author: Fernando Serboncini <fserb@fserb.com.br>

import sys
import os
import pdfan

def run(pdf_file, htmldir):
  try:
    print pdf_file
    basename, ext = os.path.splitext(os.path.split(pdf_file)[-1])
    if ext != '.pdf':
      return
    try:
      author, title = basename.split(' - ', 1)
    except:
      author, title = '', basename
    html_file = os.path.join(htmldir, basename + ".html")
    if not pdfan.has_annotation(pdf_file):
      return
    print author, "-", title
    pdfan.make_annotation(pdf_file, html_file, title.strip(), author.strip())
  except:
    print "Error"
    import traceback
    traceback.print_exc()


def main(argv):
  if len(argv) != 3:
    print "usage: %s [pdfdir] [htmldir]" % argv[0]
    return 1
  pdfdir = os.path.abspath(argv[1])
  htmldir = os.path.abspath(argv[2])

  for l in os.listdir(pdfdir):
    if os.path.isdir(os.path.join(pdfdir, l)):
      for f in os.listdir(os.path.join(pdfdir, l)):
        run(os.path.join(pdfdir, l, f), htmldir)
    else:
      run(os.path.join(pdfdir, l), htmldir)


if __name__ == '__main__':
  sys.exit(main(sys.argv))
