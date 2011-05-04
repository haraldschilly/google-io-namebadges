#!/usr/bin/env python
# -*- encoding:utf-8 -*-

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
### SETTINGS

# input filename (csv)
# example content:
# name,email,... [remaining fields don't matter]
# "firstname1 name1","email@email.com",...
# ...
if len(sys.argv) != 2:
  print "USAGE: %s filename.csv" % sys.argv[0]
  print 
  print "example content (CSV file, with one header line):"
  print "name,email,... [remaining fields don't matter]"
  print '"firstname1 name1","email@email.com",...'
  sys.exit(1)
CSVFN = sys.argv[1]
# output filename common prefix
BASEFN = CSVFN.replace(".csv", "")

IOLOGO = "io-extended-logo.png" # TODO check for updates in 2012 and later
COLORSTRIP = "google-io-colorstrip.png"

# logo of the host
HOSTLOGO = "sektor5-logo.png"

# text at the bottom
FOOTER = "sektor5, vienna, may 10. &amp; 11., 2011"

def svg2pdf(n):
    """convert the n-th svg file to pdf"""
    os.system("inkscape --export-pdf=%s-%s.pdf %s-%s.svg" % (BASEFN, n, BASEFN, n))
    print "converted svg %d to pdf" % n

def post_hook():
  """
  this is called after everthing is done. it combines all PDFs into one using pdftk.
  """
  os.system("pdftk %s-*.pdf output %s.pdf" % (BASEFN, BASEFN))
  # this one is for convert, not tested
  #os.system("convert %s-*.pdf %s.pdf" % (BASEFN, BASEFN))
  print "collected all PDFs into %s.pdf" % BASEFN

# template for QR code, the data is a format scanner apps on smartphones understand as contact information
# chld=<ECC type (L (only 7% but not so fine structures), M, Q, H)> and after the | is the margin
QRtmpl = r'http://chart.apis.google.com/chart?cht=qr&chs=200x200&chld=M|0&chl=MECARD%3AN%3A{name}%3BEMAIL%3A{email}%3B%3B'

# in front of each name
PREFIX = "Hi, I'm"

# something to fill in ... 
TEASER = "I wish Google could ..."

# page dimensions (mm)
pdims = 297, 210  # A4 has height 297 mm x width 210 mm 

# margins on whole page [ top, right, bottom, left in mm]
pmargin = 10, 10, 10, 10

# how many on each page
rows = 4
cols = 2

# badge spacing in between [ height direction, width direction ]
bspace = 0, 0

# badge info (height and width)
bdims = float(pdims[0] - pmargin[0] - pmargin[2] - bspace[0] * (rows-1)) / rows,\
        float(pdims[1] - pmargin[3] - pmargin[1] - bspace[1] * (cols-1)) / cols 

#print bdims

unit = "mm" # used in SVG after each dimension value. 

from datetime import datetime
date = datetime.strftime(datetime.utcnow(), "%Y-%m-%d %H:%M:%S UTC")

from string import Template

SVG_intro = Template('''\
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!-- Created with google-io-badge-generator (http://code.google.com/p/google-io-namebadges/) -->

<svg
 xmlns:dc="http://purl.org/dc/elements/1.1/"
 xmlns:cc="http://creativecommons.org/ns#"
 xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
 xmlns:svg="http://www.w3.org/2000/svg"
 xmlns="http://www.w3.org/2000/svg"
 xmlns:xlink="http://www.w3.org/1999/xlink"
 width="$width"
 height="$height"
 version="1.1"
>
<title>Google I/O Namebadges</title>
<metadata>
 <rdf:RDF>
  <cc:Work rdf:about="">
   <dc:format>image/svg+xml</dc:format>
   <dc:type rdf:resource="http://purl.org/dc/dcmitype/StillImage" />
   <dc:title>Google I/O Namebadges</dc:title>
   <dc:date>$date</dc:date>
   <dc:creator>
    <cc:Agent>
     <dc:title>http://code.google.com/p/google-io-namebadges/</dc:title>
    </cc:Agent>
   </dc:creator>
  </cc:Work>
 </rdf:RDF>
</metadata>
<g id="papersheet">
''').substitute(date=date, width=("%s"+unit) % pdims[1], height=("%s"+unit) % pdims[0])

SVG_outro = r'''
</g>
</svg>
'''

### actual Code starts here

import csv, urllib2, os, sys
from hashlib import md5
from collections import namedtuple

# QR code images end up in qr. delete the whole dir to refresh them.
if not os.path.exists("qr"): os.mkdir("qr")

def save_svg(svg, n):
  """
  saves the n-th svg file from the string svg
  """
  SVGFN = "%s-%d.svg" % (BASEFN, n)
  with codecs.open(SVGFN, 'w', 'utf-8-sig') as svgfile:
    svgfile.write(svg)
    print "output svg written to", os.path.abspath(SVGFN)
    svg2pdf(n)

def svg_rect(x,y,dx,dy,col="#000000"):
  return u'''\
  <rect style="fill:none;fill-opacity:1;stroke:{col};stroke-opacity:1"
    width="{dx}{u}" height="{dy}{u}" x="{x}{u}" y="{y}{u}"
  />'''.format(x=x, y=y, dx=dx, dy=dy, u=unit, col=col)

def svg_img(x,y,dx,dy,link):
  return u'''\
  <image y="{y}{u}" x="{x}{u}" height="{dy}{u}" width="{dx}{u}" 
    xlink:href="{link}"
  />'''.format(x=x, y=y, dx=dx, dy=dy, u=unit, link=link)

def svg_text(x,y,text, **kwargs):
    return svg_text_impl([(x,y,text)], **kwargs)

def svg_text_impl(tokens, font="Bitstream Vera Sans Mono", col="#000000", variant="normal", weight = "normal", style="normal", size=10):
  """
  tokens is a list of tuples: [(x, y, text)]
  """
  t = u'\n'.join([ '<tspan x="%s%s" y="%s%s">%s</tspan>' % (_[0], unit, _[1], unit, _[2]) for _  in tokens])
  return u'''\
    <text xml:space="preserve"
     style="font-size:{size};
            font-style:{style};
            font-variant:{variant};
            font-weight:{weight};
            font-stretch:normal;
            text-align:start;
            line-height:100%;
            letter-spacing:0px;
            word-spacing:0px;
            writing-mode:lr;
            text-anchor:start;
            fill:{col};
            fill-opacity:1;
            stroke:none;
            font-family:{font};">\
     '''.format(size="%f%s"%(size,unit), style=style, variant=variant, weight=weight, col=col, font=font)  + t + "</text>"




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
svg = None  # svg file string content
n   = 0     # n-th page

longest_name = ""
longest_page = 0

# iterate over each named tuple Guest generated for each first 2 elements in csv list of lists
# if your CSV list doesn't start with name and email, you have to pick other columns
for cnt, g in enumerate(map(lambda x : Guest._make(x[:2]), content)):

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
       svg += SVG_outro
       save_svg(svg, n)
       n += 1
    svg = unicode()
    svg += SVG_intro

  # calc position on page, (x,y)
  offsetcnt = cnt % cols, (cnt % (rows*cols)) / cols 
  offset = pmargin[3] + offsetcnt[0] * (bdims[1] + bspace[1]),\
           pmargin[0] + offsetcnt[1] * (bdims[0] + bspace[0])

  # for testing the actual borders
  #svg += svg_rect(offset[0], offset[1], bdims[1], bdims[0], "#ccc")
  svg += svg_text(offset[0] + 5, offset[1] + 10, g.name.lower().decode("utf8"), size=5.8, weight="bold")
  #svg += svg_text(offset[0] + 4, offset[1] + 16, g.email.lower(),               size=4, col="#333")
  # Teaser
  svg += svg_text(offset[0] + 6, offset[1] + 13, TEASER, size=2, col="#ccc")
  # Logo Host (e.g. 242x242 original)
  hwidth = 15
  hheight = (hwidth/242.0) * 242.0
  svg += svg_img(offset[0] + 52,  offset[1] + bdims[0] - 16, hwidth, hheight, HOSTLOGO)
  # Logo IO
  lwidth = 40
  lheight = (lwidth/278.0)*79
  svg += svg_img(offset[0] + 6, offset[1] + bdims[0] - lheight - 2, lwidth, lheight, IOLOGO)
  # colorstrip
  svg += svg_img(offset[0], offset[1] + 3, 3, bdims[0] - 4, COLORSTRIP)
  # QR
  qrdim = 22
  svg += svg_img(offset[0] + bdims[1] - qrdim - 1, offset[1] + bdims[0] - qrdim - 1, qrdim, qrdim, qrpath)
  # Footer
  svg += svg_text(offset[0] + 5, offset[1] + bdims[0] - qrdim + 2, FOOTER, col="#333", variant="italic", size=3.05)

# close last page
svg += SVG_outro
save_svg(svg, n)

print "Longest Name:", longest_name, "on page", longest_page

post_hook()
