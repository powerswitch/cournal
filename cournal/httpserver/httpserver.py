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

from twisted.internet import reactor, protocol
from twisted.protocols.basic import LineReceiver
from cournal.network import network
from cournal.document.document import Document
from cournal.document import xojparser
from cournal.httpserver.html import Html
from cournal.httpserver.whitelist import whitelist
from cournal.server.util import docname_to_filename
from gi.repository import Poppler, GLib
import sys
import cgi
import cournal
import urllib.parse
import signal
import cairo

# 0 - none
# 1 - minimal
# 2 - medium
# 3 - maximal
DEBUGLEVEL = 3

class Httpserver(LineReceiver):
    def __init__(self):
        self.html = Html(self.server.documents, self.transport)

    def connectionLost(self, reason):
        """ What to do when the connection is closed """
        debug(3, "connection",self.html.http_users,"lost")
        self.html.http_users -= 1
    
    def connectionMade(self):
        """ What to do when a new connection is made """
        self.html.http_users += 1
        debug(3, "connection {} made".format(self.html.http_users))
        self.html.transport = self.transport

        for document in self.server.documents:
            whitelist.append("/pdf/"+document+".pdf")
            whitelist.append("/svg/"+document+".svg")
            page_number = 0
            for page in self.server.documents[document].pages:
                page_number += 1;
                whitelist.append("/svg/"+document+".svg?page="+str(page_number));
            whitelist.append("/svg/"+document+".html")

    def render_web_pdf(self, document_name):
        # Open a preview document
        #try:
        #    #surface = cairo.PDFSurface(cournal.__path__[0]+"/httpserver/documents/webpreview2.pdf", 0, 0)
        #    surface = cairo.PDFSurface("output.pdf", 0, 0)
        #except IOError as ex:
        #    print("Error saving document:", ex)
        #    return
        #
        #for page in self.server.documents["Test"].pages:
        #    surface.set_size(595, 842) #page.width, page.height)
        #    context = cairo.Context(surface)
        #    
        #    #page.pdf.render_for_printing(context)
        #    
        #    for stroke in page.strokes:
        #        stroke.draw(context)
        #    
        #    surface.show_page() # aka "next page"
        #surface.finish()
        #document = Document(cournal.__path__[0]+"/httpserver/documents/webpreview.pdf")
        #document.export_pdf("output.pdf")
        #output = readfile.read()
        #return output

        save_name = "http_cache_"+docname_to_filename(document_name)+".pdf"
        #uri = GLib.filename_to_uri(cournal.__path__[0]+"/httpserver/documents/webpreview.pdf", None)
        #pdf = Poppler.Document.new_from_file(uri, None)

        # Open a preview document
        try:
            surface = cairo.PDFSurface(save_name, 595, 842) #TODO: get size!
        except IOError as ex:
            print("Error saving document:", ex)
            return

        for page in self.server.documents[document_name].pages:
            context = cairo.Context(surface)
            for stroke in page.strokes:
                stroke.draw(context)
            surface.show_page()
        surface.finish()
        readfile = open(save_name,"rb")
        output = readfile.read()
        return output

    def render_web_svg(self, document_name, page_number=0):
        save_name = "http_cache_"+docname_to_filename(document_name)+".svg"
        # Open a preview document
        try:
            surface = cairo.SVGSurface(save_name, 595, 842) #TODO: get size!
        except IOError as ex:
            print("Error saving document:", ex)
            return

        if page_number == 0:
            for page in self.server.documents[document_name].pages:
                context = cairo.Context(surface)
                for stroke in page.strokes:
                    stroke.draw(context)
                surface.show_page()
        else:
            page = self.server.documents[document_name].pages[page_number-1]
            context = cairo.Context(surface)
            for stroke in page.strokes:
                stroke.draw(context)
            surface.show_page()
        
        surface.finish()
        readfile = open(save_name,"r")
        output = readfile.read()
        return output

    def lineReceived(self, data):
        """ If a readable line is received """
        binary = False;
        if data.decode().upper().startswith("GET"):
            getfile = data.decode().split(" ")[1]
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
                # SVG
                elif getfile.startswith("/svg/"): #TODO: Security bug
                    if getfile.endswith(".html"):
                        output = self.html.HTML_SVG(
                            urllib
                                .parse
                                .unquote(getfile[5:-5]),
                            self.render_web_svg(urllib
                                .parse
                                .unquote(getfile[5:-5]),
                                page_number=1
                            ),
                            len(
                                self
                                .server
                                .documents[
                                    urllib
                                    .parse
                                    .unquote(getfile[5:-5])
                                ]
                                .pages
                            )

                        )
                        status = 200
                        ctype = "text/html; charset=utf-8"
                    elif getfile.find("?page=") >= 0:
                        argument_position = getfile.find("?page=")
                        output = self.render_web_svg(urllib
                            .parse
                            .unquote(getfile[5:argument_position-4]),
                            page_number=int(getfile[getfile.find("?page=")+6:])
                        )
                        status = 200
                        ctype = "image/svg+xml; charset=utf-8"
                    else:
                        #TODO: look for it  in self.server.documents
                        output = self.render_web_svg(urllib
                            .parse
                            .unquote(getfile[5:-4])
                        )
                        status = 200
                        ctype = "image/svg+xml; charset=utf-8"
                # PDF
                elif getfile.startswith("/pdf/"): #TODO: Security bug

                    #TODO: look for it  in self.server.documents
                    output = self.render_web_pdf(urllib
                        .parse
                        .unquote(getfile[5:-4])
                    )
                    status = 200
                    ctype = "application/pdf"
                    binary = True
               
                # try to open files
                else:
                    ''' Try to open the file '''
                    try:
                        if getfile[-4:] == ".png":
                            readfile = open(cournal.__path__[0]+"/httpserver"+getfile,"rb")
                        else:
                            readfile = open(cournal.__path__[0]+"/httpserver"+getfile,"r")
                        output = readfile.read()
                        status = 200
                        #ctype
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
            
            else:
                self.html.send(
                    self.html.template(
                        "<h1>404 - File not found</h1>This file was not found on the server"
                    ),
                    ctype="text/html; charset=utf-8",
                    status=404
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

