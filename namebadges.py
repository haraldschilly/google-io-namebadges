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
# Outputs a HTML file called HTMLFN with proper CSS for printing.
# You need a webbrowser that prints the pages as close to the given values as possible.
# Chrome 11&12 do a good job, Firefox adds header/footer without warning.


### SETTINGS

# input filename (csv, column 0 = name, column 1 = email)
CSVFN = u'Google I%2FO Extended RSVP.csv'
# output filename
HTMLFN = "google-io-2011-badges.html"

# template for QR code, the data is a format scanner apps on smartphones understand as contact information
QRtmpl = r'http://chart.apis.google.com/chart?cht=qr&chs=200x200&chl=MECARD%3AN%3A{name}%3BEMAIL%3A{email}%3B%3B'

# in front of each name
PREFIX = "Hi, I'm"

# something to fill in ... 
TEASER = "I wish Google could ..."

# page dimensions (mm)
pwidth = "190mm"  # A4 has width 210 mm
pheight = "250mm" # A4 has height 297 mm

# how many on each page
rows = 4
cols = 2

# badge info (mm)
bwidth = "96mm"
bheight = "48mm"

# badge spacing [ x mm, y mm ]
bspacing = "%smm %smm" % (1, 1)

# margins on whole page [ top, right, bottom, left in mm]
pmargin = "%smm %smm %smm %smm" % ( 0, 0, 0, 0)

from string import Template

HTML_intro = Template(r'''
<!doctype html>
<html>
<head><title>Google I/O Extended Namebadges</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>

<style type="text/css" media="all">
* { border: 0; margin: 0; padding: 0; }

img { border: 0; }

.page { 
   width: $pwidth;
   height: $pheight;
   _border: 1px solid blue;
   page-break-after: always; 
   table-layout: fixed;
   border-collapse: separate;
   border-spacing: $bspacing;
   margin: $pmargin;
}
.badge { 
   vertical-align: middle;
   horizontal-align: center;
   _border: 1px solid green;
}
.content {
   position: relative;
   width: $bwidth;
   height: $bheight;
   _border: 1px solid orange;
   overflow: hidden;
}
.iologo {
  position: absolute;
  width: 30mm;
  height: 8mm;
  bottom: 2mm;
  right: 2mm;
}
.name {
  _border: 1px solid red;
  position: absolute;
  top: 2mm;
  left: 2mm;
  width: 70mm;
  font-family: sans-serif;
  font-size: 4mm;
}
.teaser {
  position: absolute;
  top: 13mm;
  left: 2mm;
  color: #999;
  font-family: sans-serif;
  font-size: 2mm;
}
.background {
  position: absolute;
  top: -20mm;
  left: 0mm;
  font-family: sans-serif;
  font-size: 80mm;
  z-index: -10;
  color: #FAFAFA;
}
.qr {
  position: absolute;
  width: 25mm;
  height: 25mm;
  top: -2mm;
  right: -2mm;
  clip:rect(0mm 24mm 25mm 1mm);
}
</style>
</head>
<body>
<table class='page'>
''').substitute(locals())

HTML_outro = r'''
</body>
</html>
'''

### actual Code starts here

import csv, urllib2, os, sys
from collections import namedtuple

# QR code images end up in qr. delete the whole dir to refresh them.
if not os.path.exists("qr"): os.mkdir("qr")

# Datacontainer
Guest = namedtuple('Guest', ['name', 'email'])

import codecs
try:
  content = csv.reader(codecs.open(CSVFN, "rb"))
except IOError, msg:
  print "You need a CSV file '%s' (=CSVFN variable) in the current directory." % CSVFN
  print msg
  sys.exit(1)
content.next() # skip header

# html will contain the complete website in the end
html = unicode() + HTML_intro

# iterate over each named tuple Guest generated for each first 2 elements in csv list of lists
for cnt, g in enumerate(map(lambda x : Guest._make(x[:2]), content)):

  # use QRtmpl template from above to construct url
  url = QRtmpl.format(name=urllib2.quote(g.name), email=urllib2.quote(g.email))

  #print g.name, urllib2.quote(g.email), url

  # unique name for qr file
  qrname = g.email.replace("@", ".").strip()

  # where to write to
  qrpath = os.path.join("qr", qrname + ".png")

  # only if we not already have it
  if not os.path.exists(qrpath):
    print ">> downloading %s" % qrpath                        
    with open(qrpath, 'wb') as qrfile:
      qrdl = urllib2.urlopen(url)
      qrfile.write(qrdl.read())

  # do the html 
  if cnt > 1 and cnt % (cols*rows) == 0:
    html += '</table><table class="page">\n'
    

  badge = unicode()
  #print "cnt:", cnt, "% 2 =", cnt % 2
  if cnt % cols == 0:
    badge += "<tr>"
    
  badge += "<td class='badge'>\n"
  badge += "<div class='content'>"
  badge += u"<div class='name'>%s %s<br/>%s</div>" % (PREFIX, g.name.decode("utf8"), g.email)
  badge += "<img  class='qr' src='%s'></img>\n" % qrpath
  badge += "<img class='iologo' src='io-extended-logo.png'></img>\n"
  #badge += "<div class='background'>I/O</div>"
  badge += "<div class='teaser'>%s</div>" % TEASER
  badge += "</div>"
  badge += "</td>\n"

  if cnt % cols == cols - 1:
    badge += "</tr>"

  html += badge
    
#print "cnt: ", (cnt % (cols*rows))
# adding <tr>'s as remainder on last page
for i in range(-1, (cnt % (cols*rows)) % cols):
  html += '<tr><td class="badge"><div class="content"></div></td><td><div class="content"></div></td></tr>'
html += '</table>' + HTML_outro

with codecs.open(HTMLFN, 'w', 'utf-8-sig') as htmlfile:
  htmlfile.write(html)
  print "output html written to", os.path.abspath(HTMLFN)


