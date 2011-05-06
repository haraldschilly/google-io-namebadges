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

# This is a class for building SVG files. It's rather rough and only serves the
# purpose of building these badges.


class SVG(object):
  SVG_outro = r'</g> </svg>'

  def __init__(self, pdims, unit = "mm"):
    """
    args:
    
      - pdims: page dimensions tuple, height and width in [unit]s
      - unit: string for the units in SVG (e.g. "mm" or "px", default is "mm")
    """
    self.height = pdims[0]
    self.width = pdims[1]
    self.unit = unit
    self._svg = unicode()

    # creating date
    from datetime import datetime
    date = datetime.strftime(datetime.utcnow(), "%Y-%m-%d %H:%M:%S UTC")
    
    from string import Template
    self._svg += Template('''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
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
    ''').substitute(date=date, width="%s%s" % (pdims[1], unit), height="%s%s"% (pdims[0],unit))
    

  def __iadd__(self, string):
    self._svg += string + '\n'
    return self

  def line(self, start, end, col="#000000", width=None):
    if width==None:
      width = "0.1%s" % self.unit
    u = self.unit
    self._svg += '<line x1="%s%s" y1="%s%s" x2="%s%s" y2="%s%s" style="stroke:%s;stroke-width:%s"/>'\
                 %(start[0], u, start[1], u, end[0], u, end[1], u, col, width)

  def rect(self, x, y, dx, dy, col="#000000"):
    self._svg += u'''\
    <rect style="fill:none;fill-opacity:1;stroke:{col};stroke-opacity:1"
      width="{dx}{u}" height="{dy}{u}" x="{x}{u}" y="{y}{u}"
    />'''.format(x=x, y=y, dx=dx, dy=dy, u=self.unit, col=col)
  
  def image(self, x, y, dx, dy, link):
    self._svg += u'''\
    <image y="{y}{u}" x="{x}{u}" height="{dy}{u}" width="{dx}{u}" 
      xlink:href="{link}"
    />'''.format(x=x, y=y, dx=dx, dy=dy, u=self.unit, link=link)
  
  def text(self, x, y, text, **kwargs):
      self._text_impl([(x,y,text)], **kwargs)
  
  def _text_impl(self, tokens, font="Bitstream Vera Sans Mono", col="#000000", variant="normal", weight = "normal", style="normal", size=10):
    """
    tokens is a list of tuples: [(x, y, text)]
    """
    t = u'\n'.join([ '<tspan x="%s%s" y="%s%s">%s</tspan>' % (_[0], self.unit, _[1], self.unit, _[2]) for _  in tokens])
    self._svg += u'''\
      <text xml:space="preserve"\
       style="font-size:{size};\
              font-style:{style};\
              font-variant:{variant};\
              font-weight:{weight};\
              font-stretch:normal;\
              text-align:start;\
              line-height:100%;\
              letter-spacing:0px;\
              word-spacing:0px;\
              writing-mode:lr;\
              text-anchor:start;\
              fill:{col};\
              fill-opacity:1;\
              stroke:none;\
              font-family:{font};">
       '''.format(size="%s%s"%(size,self.unit), style=style, variant=variant, weight=weight, col=col, font=font)  + t + "</text>"


  def finalize(self):
    self._svg += self.SVG_outro
    return self._svg

