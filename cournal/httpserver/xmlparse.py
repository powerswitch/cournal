#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Cournal: A collaborative note taking and journal application with a stylus.
# Copyright (C) 2012 Simon Vetter
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import xml.dom.minidom as dom
from cournal.document.stroke import Stroke 

class XmlParse:
    """
    XML parse class
    
    Parses XML given from the Cournal Web App
    """
    
    def __init__(self, server):
        """
        Constructor
        """
        self.server = server
        
    def parse(self, xml, user):
        d = dom.parseString(xml)
        #help(d)
        for node in d.childNodes:
            if node.nodeName == "insert":
                docname = node.getAttribute("name")
                docpage = int(node.getAttribute("page"))
                coords = []
                for stroke in node.childNodes:
                    if stroke.nodeName == "stroke":
                        c = 0
                        for t in stroke.firstChild.data.split(" "):
                            if c:
                                coords.append((int(x), int(t)))
                            else:
                                x = t
                            c = 1 - c

                #print(coords)
                newstroke = Stroke(None, (255,0,0,255), 5.5, coords)
                self.server.documents[docname].view_new_stroke(user, 0, newstroke)
                            