#!/usr/bin/python2.6 -W ignore::DeprecationWarning
# -*- coding: utf-8 -*-
# Author: Fernando Serboncini <fserb@fserb.com.br>

import sys
import os
import pdfan

def main(argv):
  if len(argv) != 3:
    print "usage: %s [pdfdir] [htmldir]" % argv[0]
    return 1
  pdfdir = os.path.abspath(argv[1])
  htmldir = os.path.abspath(argv[2])

  for l in os.listdir(pdfdir):
    pdf_file = os.path.join(pdfdir, l)
    basename, ext = os.path.splitext(l)
    if ext != '.pdf':
      continue
    author, title = l.split(' - ', 1)
    html_file = os.path.join(htmldir, basename + ".html")
    print author, "-", title
    pdfan.make_annotation(pdf_file, html_file, title.strip(), author.strip())


if __name__ == '__main__':
  sys.exit(main(sys.argv))
