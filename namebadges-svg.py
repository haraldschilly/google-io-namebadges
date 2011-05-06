#!/usr/bin/env python
# -*- encoding:utf-8 -*-
#
# Copyright 2011 Harald Schilly <harald@gtug.at>
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
# http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

### DOCUMENTATION
#
# Input
# this program takes a csv list (download/export from google docs) where column 0 is 
# the name and column 1 is the email adress. it also discards the header line.

# Output
# Creates a directory qr, fills it with QR codes downloaded from the Google Visualizaion API.
# Outputs a SVG file called SVGFN with proper formatting for printing (default A4)
# you can either print the SVG directly (e.g. inkscape) or use inkscape to render a beautiful PDF (default).

import sys

# input filename (csv)
# example content:
# name,email,... [remaining fields don't matter]
# "firstname1 name1","email@email.com",...
# ...
if len(sys.argv) <= 1:
  print "USAGE: %s filename.csv [settings.ini]" % sys.argv[0]
  print 
  print "example content (CSV file, with one header line):"
  print "name,email,... [remaining fields don't matter]"
  print '"firstname1 name1","email@email.com",...'
  print
  print "you can optionally specify a settings file as second argument"
  sys.exit(1)
CSVFN = sys.argv[1]
# output filename common prefix
BASEFN = CSVFN.replace(".csv", "")

# settings file as optional second argument
SETTINGSFN = "settings.ini"
if len(sys.argv) >= 3:
  SETTINGSFN = sys.argv[2]
 
### READING SETTINGS
from ConfigParser import ConfigParser
C = ConfigParser()
C.read(SETTINGSFN)

IOLOGO = C.get("pix", "IOLOGO")
COLORSTRIP = C.get("pix", "COLORSTRIP")
HOSTLOGO = C.get("pix", "HOSTLOGO")
FOOTER = C.get("badge", "FOOTER")
TEASER = C.get("badge", "TEASER")
QRtmpl = C.get("badge", "QRtmpl")
pdims = [ C.getfloat("page", _) for _ in ["pdimheight", "pdimwidth"] ]
pmargin = [ C.getfloat("page", "pmargin%s"%_) for _ in ["top", "right", "bottom", "left" ]]
rows = C.getint("page", "rows")
cols = C.getint("page", "cols")
bspace = C.getfloat("page", "bspaceheight"), C.getfloat("page", "bspacewidth")
unit = C.get("page", "unit")
name_idx = C.getint("csv", "name_index")
email_idx = C.getint("csv", "email_index")

# calculating badge size info (height and width)
bdims = float(pdims[0] - pmargin[0] - pmargin[2] - bspace[0] * (rows-1)) / rows,\
        float(pdims[1] - pmargin[3] - pmargin[1] - bspace[1] * (cols-1)) / cols 

# utility functions
def svg2pdf(n):
    """convert the n-th svg file to pdf"""
    # if you change the filepattern, you also have to change it in other spots
    os.system("inkscape --export-pdf=%s-%s.pdf %s-%s.svg" % (BASEFN, n, BASEFN, n))
    print "converted svg %d to pdf" % n

def save_svg(svg, n):
  """
  saves the n-th svg file from the string svg
  """
  # if you change SVGFN, you also have to change the delete pattern above
  SVGFN = "%s-%d.svg" % (BASEFN, n)
  draw_cutmarks(svg)
  draw_info(svg, n)
  svg = svg.finalize()
  with codecs.open(SVGFN, 'w', 'utf-8-sig') as svgfile:
    svgfile.write(svg)
    print "output svg written to", os.path.abspath(SVGFN)
  svg2pdf(n)


### actual Code starts here

import csv, urllib2, os, sys
from hashlib import md5
from collections import namedtuple

# QR code images end up in qr. delete the whole dir to refresh them.
if not os.path.exists("qr"): os.mkdir("qr")

# delete existing files
from glob import glob
for pat in ["%s-*.pdf", "%s-*.svg"]:
  for f in glob(pat % BASEFN):
    os.remove(f)

# SVG specific functions
from svg import SVG



def draw_badge(svg, cnt, g, qrpath):
  # calc position on page, (x,y)
  offsetcnt = cnt % cols, (cnt % (rows*cols)) / cols 
  offset = pmargin[3] + offsetcnt[0] * (bdims[1] + bspace[1]),\
           pmargin[0] + offsetcnt[1] * (bdims[0] + bspace[0])

  # for testing the actual borders
  #svg += svg_rect(offset[0], offset[1], bdims[1], bdims[0], "#ccc")
  # name
  svg.text(offset[0] + 5, offset[1] + 11, g.name.lower().decode("utf8"), size=6, weight="bold")
  #svg += svg_text(offset[0] + 4, offset[1] + 16, g.email.lower(),               size=4, col="#333")
  # Teaser
  svg.text(offset[0] + 6, offset[1] + 14, TEASER, size=2, col="#b0b0b0")
  # Logo Host (e.g. 242x242 original)
  hwidth = 15
  hheight = (hwidth/242.0) * 242.0
  svg.image(offset[0] + 51,  offset[1] + bdims[0] - 16, hwidth, hheight, HOSTLOGO)
  # Logo IO
  lwidth = 40
  lheight = (lwidth/278.0)*79
  svg.image(offset[0] + 6, offset[1] + bdims[0] - lheight - 2, lwidth, lheight, IOLOGO)
  # colorstrip
  svg.image(offset[0], offset[1] + 3, 3, bdims[0] - 4, COLORSTRIP)
  # QR
  qrdim = 22
  svg.image(offset[0] + bdims[1] - qrdim - 2, offset[1] + bdims[0] - qrdim - 1, qrdim, qrdim, qrpath)
  # Footer
  svg.text(offset[0] + 5, offset[1] + bdims[0] - qrdim + 2, FOOTER, col="#333", variant="italic", size=3.20)

def draw_cutmarks(svg):
  # top and bottom
  for c in range(cols + 1):
    x = pmargin[3] + c * (bdims[1] + bspace[1]) - bspace[1] / 2.0 - 1
    svg.line((x, 0),                                     (x, pmargin[0] - bspace[0]))
    svg.line((x, pdims[0] - pmargin[2] + bspace[1] + 2), (x, pdims[0]))
  for r in range(rows + 1):
    y = pmargin[0] + r * (bdims[0] + bspace[0]) - bspace[0] / 2.0 + 1
    svg.line((0, y),                                     (pmargin[3] - bspace[1] - 2, y))
    svg.line((pdims[1] - pmargin[1] + bspace[0] , y), (pdims[1], y))

def draw_info(svg, n):
  from datetime import datetime
  date = datetime.strftime(datetime.utcnow(), "%Y-%m-%d %H:%M:%S UTC")
  svg.text(pmargin[3], pmargin[0] - 1, "%s - %s - %s" % (CSVFN, n, date), size=2)



# primitive datacontainer
Guest = namedtuple('Guest', ['name', 'email'])

import codecs
try:
  content = csv.reader(codecs.open(CSVFN, "rb"))
except IOError, msg:
  print "You need a CSV file '%s' (=CSVFN variable) in the current directory." % CSVFN
  print msg
  sys.exit(1)

content.next() # skip header

# initialized and used in the for loop
svg = None # svg file content
n   = 0    # n-th page

longest_name = ""
longest_page = 0

# iterate over each named tuple Guest generated for selected elements in CSV's line list
data = map(lambda _ : Guest._make([_[name_idx], _[email_idx]]), content)

# iterate over sorted list by surname. names like "  name   surname  " are fine.
for cnt, g in enumerate(sorted(data, key = lambda _:_.name.strip().split(" ")[-1])):

  # use QRtmpl template from above to construct url
  url = QRtmpl.format(name=urllib2.quote(g.name), email=urllib2.quote(g.email))

  #print g.name, urllib2.quote(g.email), url
  if len(g.name) > len(longest_name):
    longest_name = g.name
    longest_page = n

  # unique name for qr file (add name, some have no email!)
  qrname = md5()
  qrname.update(g.name)
  qrname = qrname.hexdigest()
  qrname += "-%s" % g.email.replace("@", ".").strip()

  # where to write to
  qrpath = os.path.join("qr", qrname + ".png")

  # only if we not already have it
  if not os.path.exists(qrpath):
    print ">> downloading %s" % qrpath                        
    with open(qrpath, 'wb') as qrfile:
      qrdl = urllib2.urlopen(url)
      qrfile.write(qrdl.read())

  # check if we start a new page
  if cnt % (rows * cols) == 0:
    if svg != None:
       # save the file
       save_svg(svg, n)
       n += 1
    svg = SVG(pdims, unit)

  draw_badge(svg, cnt, g, qrpath)


# close last page
save_svg(svg, n)

print "Check longest name'", longest_name, "'on page", longest_page, "for clipping."

# this is for after everthing is done. it combines all PDFs into one using pdftk.
# if you change the filepattern, you also have to change it in other spots
os.system("pdftk %s-*.pdf output %s.pdf" % (BASEFN, BASEFN))
# this one is for convert, not tested
#os.system("convert %s-*.pdf %s.pdf" % (BASEFN, BASEFN))
print "Collected all PDFs into %s.pdf" % BASEFN
