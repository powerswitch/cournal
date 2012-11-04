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

# Known bugs:
#   * new created documents does not appear in whitelist

# To do:
#   * get document dimensions
#   * get time stamp

from twisted.internet import reactor, protocol
from twisted.protocols.basic import LineReceiver
from cournal.network import network
from cournal.document.document import Document
from cournal.document import xojparser
from cournal.httpserver.html import Html
from cournal.httpserver.whitelist import whitelist
from cournal.httpserver.xmlparse import XmlParse
from cournal.server.user import User
#from cournal.server.util import docname_to_filename
from gi.repository import Poppler, GLib
import sys
import cgi
import cournal
import urllib.parse
import signal
import cairo
import io
import random

# 0 - none
# 1 - minimal
# 2 - medium
# 3 - maximal
DEBUGLEVEL = 3

class Httpserver(LineReceiver):
    """
    HTTP server class
    
    Serves the cournal documents to any browser as PDF or SVG.
    """
    
    def __init__(self):
        """
        Constructor
        
        Creates a new HTML parser object
        """
        self.html = Html(self.server.documents, self.transport)
        self.xml = XmlParse(self.server)

    def connectionLost(self, reason):
        """
        What to do when the connection is closed
        Called by LineReceiver
        """
        debug(3, "connection",self.html.http_users,"lost")
        self.html.http_users -= 1
    
    def connectionMade(self):
        """
        What to do when a new connection is made
        Called by LineReceiver
        """
        self.html.http_users += 1
        debug(3, "connection {} made".format(self.html.http_users))
        self.html.transport = self.transport
        self.user = User("WebApp", self.server)

        for document in self.server.documents:
            if not "/pdf/"+document+".pdf" in whitelist:
                whitelist.append("/pdf/"+document+".pdf")
            if not "/svg/"+document+".svg" in whitelist:
                whitelist.append("/svg/"+document+".svg")
            if not "/app/"+document+".html" in whitelist:
                whitelist.append("/app/"+document+".html")
            page_number = 0
            for page in self.server.documents[document].pages:
                page_number += 1;
                if not "/svg/"+document+".svg?page="+str(page_number) in whitelist:
                    whitelist.append("/svg/"+document+".svg?page="+str(page_number));
                if not "/svg/"+document+".svg?timestamp="+str(page_number) in whitelist:
                    whitelist.append("/svg/"+document+".svg?timestamp="+str(page_number));
                if not "/app/"+document+".html?page="+str(page_number) in whitelist:
                    whitelist.append("/app/"+document+".html?page="+str(page_number));
            if not "/svg/"+document+".html" in whitelist:
                whitelist.append("/svg/"+document+".html")

    def render_web_pdf(self, document_name):
        """
        Render given document as pdf into memory
        
        Positional argument:
        document_name -- Name of the document to be rendered
        
        Return value:
        document pdf as byte string
        """
        memfile = io.BytesIO() # Create memory file
        try:
            surface = cairo.PDFSurface(memfile, 595, 842)  #TODO: get size!
        except IOError as ex:
            print("Error saving document:", ex)
            return

        # Render every page in document
        for page in self.server.documents[document_name].pages:
            context = cairo.Context(surface) # create new cairo context
            for stroke in page.strokes:      # draw every stroke
                stroke.draw(context)
            surface.show_page()              # next page
        surface.finish()                     # finish document
        memfile.seek(0)                      # rewind
        return memfile.read()                # return

    def render_web_svg(self, document_name, page_number=0):
        """
        Render given document as pdf into memory
        
        Positional argument:
        document_name -- Name of the document to be rendered
        
        Named argument:
        page_number   -- Page number to be rendered
        
        Return value:
        document svg as string
        """        
        memfile = io.BytesIO() # create new memory file
        try:
            surface = cairo.SVGSurface(memfile, 595, 842) #TODO: get size!
        except IOError as ex:
            print("Error saving document:", ex)
            return

        # Render selected page
        page = self.server.documents[document_name].pages[page_number-1]
        context = cairo.Context(surface) # create new cairo context
        for stroke in page.strokes:      # render every stroke
            stroke.draw(context)
        surface.show_page()              # finish page
        surface.finish()                 # finish document
        
        memfile.seek(0)                  # rewind
        return str(memfile.read(), "utf-8") # return

    def lineReceived(self, data):
        """
        If a readable line is received
        Called by LineReceiver
        
        Positional argument:
        data -- read line
        """
        binary = False; # If output is binary or string
        
        """ Client requested HTTP GET file """
        if data.decode().upper().startswith("GET"):
            getfile = data.decode().split(" ")[1] # get requested file name
            
            """ Check if requested file is in whitelist """
            if urllib.parse.unquote(getfile) in whitelist:
                # Symlinks
                if getfile == "/" or getfile == "/index.html":
                    getfile = "/status.html"
                
                # Html building functions
                if getfile == "/status.html":
                    output = self.html.HTML_status() 
                    status = 200
                    ctype = "text/html; charset=utf-8"
                elif getfile == "/documents.html":
                    output = self.html.HTML_documents() 
                    status = 200
                    ctype = "text/html; charset=utf-8"
                # APP
                elif getfile.startswith("/app/"):
                    # Get SVG preview HTML page
                    if getfile.endswith(".html"):
                        document_name = urllib.parse.unquote(getfile[5:-5])
                        output = self.html.HTML_APP(
                            document_name,
                            len(self.server.documents[document_name].pages)
                        )
                        status = 200
                        ctype = "text/html; charset=utf-8"
                    # app.js
                    elif getfile.endswith(".js"):
                        readfile = open(cournal.__path__[0]+"/httpserver"+getfile,"r")
                        output = readfile.read()
                        status = 200
                        ctype = "application/javascript; charset=utf-8"
                # SVG
                elif getfile.startswith("/svg/"):
                    # Get SVG preview HTML page
                    if getfile.endswith(".html"):
                        document_name = urllib.parse.unquote(getfile[5:-5]) # get document name
                        output = self.html.HTML_SVG( 
                            document_name,
                            self.render_web_svg(document_name,page_number=1),
                            len(self.server.documents[document_name].pages)
                        )
                        status = 200
                        ctype = "text/html; charset=utf-8"
                    # Get raw SVG of given page
                    elif getfile.find("?page=") >= 0:
                        argument_position = getfile.find("?page=")
                        output = self.render_web_svg(urllib
                            .parse
                            .unquote(getfile[5:argument_position-4]),
                            page_number=int(getfile[getfile.find("?page=")+6:])
                        )
                        status = 200
                        ctype = "image/svg+xml; charset=utf-8"
                    # Get timestamp of given SVG page
                    elif getfile.find("?timestamp=") >= 0:
                        # TODO: Create Timestamp / Version Number
                        #argument_position = getfile.find("?timestamp=")
                        output = str(random.randint(0,10000)) # FIXME
                        status = 200
                        ctype = "text/plain; charset=utf-8"
                    # Render SVG
                    else:
                        output = self.render_web_svg(urllib
                            .parse
                            .unquote(getfile[5:-4])
                        )
                        status = 200
                        ctype = "image/svg+xml; charset=utf-8"
                # PDF
                elif getfile.startswith("/pdf/"):
                    output = self.render_web_pdf(urllib
                        .parse
                        .unquote(getfile[5:-4])
                    )
                    status = 200
                    ctype = "application/pdf"
                    binary = True
               
                # try to open files
                else:
                    """ Try to open the file """
                    try:
                        if getfile[-4:] == ".png":
                            readfile = open(cournal.__path__[0]+"/httpserver"+getfile,"rb")
                        else:
                            readfile = open(cournal.__path__[0]+"/httpserver"+getfile,"r")
                        output = readfile.read()
                        status = 200
                        # filter ctype
                        if getfile.endswith(".css"):
                            ctype = "text/css; charset=utf-8"
                        elif getfile.endswith(".html"):
                            ctype = "text/html; charset=utf-8"
                        elif getfile.endswith(".svg"):
                            ctype = "image/svg+xml; charset=utf-8"
                        elif getfile.endswith(".png"):
                            ctype = "image/png"
                            binary = True
                        elif getfile.endswith(".xoj"):
                            ctype = "text/xml; charset=utf-8"
                        elif getfile.endswith(".pdf"):
                            ctype = "application/pdf"
                        elif getfile.endswith(".js"):
                            ctype = "application/javascript; charset=utf-8"
                        else:
                            ctype = "text/html; charset=utf-8"
                    except IOError:
                        """ Create 404 error page """
                        output = """<h1>404 - File not found</h1>
                                    This file should be on this server,
                                    but it could not be opened.<br />
                                    I'll send an automated error message to the maintainer
                                """
                        status = 404
                        ctype = "text/html; charset=utf-8"
                        print("Whitelist error! (", getfile, ")", file=sys.stderr)

                ''' Generate some HTML '''
                if getfile.endswith(".html"):
                    output = self.html.template(output)
                
                self.html.send(output,ctype=ctype,status=status,binary=binary)
            # Not in whitelist
            else:
                self.html.send(
                    self.html.template(
                        "<h1>404 - File not found</h1>This file was not found on the server"
                    ),
                    ctype="text/html; charset=utf-8",
                    status=404
                )
        # POST data from web app
        elif data.decode().upper().startswith("POST"):
            #getfile = data.decode().split(" ")[1] # get requested file name
            #print(urllib.parse.unquote(data.decode())[10:-9])
            self.xml.parse(urllib.parse.unquote(data.decode())[10:-9], self.user)
            self.html.send(
                "OK",
                ctype="text/plain",
                status=200
            )


                
def debug(level, *args):
    """Helper function for debug output"""
    if level <= DEBUGLEVEL:
        print("HTTP:", *args)
                
def main():
    factory = protocol.ServerFactory()
    factory.protocol = Httpserver
    reactor.listenTCP(8000,factory)
    debug(3, "HTML backend ready!")
    reactor.run()

if __name__ == '__main__':
    main()

