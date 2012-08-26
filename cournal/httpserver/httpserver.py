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
import sys
import cgi
import cournal
import urllib.parse
import signal

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

    def render_web_pdf(self):
        # Open a preview document
        # TODO: This is not, what I was looking for :( Need more time!
        document = Document(cournal.__path__[0]+"/httpserver/documents/webpreview.pdf")
        document.export_pdf("output.pdf")
        readfile = open("output.pdf","rb")
        output = readfile.read()
        network.disconnect()
        return output

    def render_web_svg(self, document_name):
        # Open a preview document
        # TODO: This is not, what I was looking for :( Need more time!
        document = Document(cournal.__path__[0]+"/httpserver/documents/webpreview.pdf")
        document.export_svg("output.svg")
        readfile = open("output.svg","r")
        output = readfile.read()
        network.disconnect()
        return output

    def lineReceived(self, data):
        """ If a readable line is received """
        binary = False;
        if data.decode().upper().startswith("GET"):
            getfile = data.decode().split(" ")[1]
            debug(3, "GET ", getfile)
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

                    #TODO: look for it  in self.server.documents
                    output = self.html.template(
                        "<h1>"+
                        urllib
                            .parse
                            .unquote(getfile[5:-4])
                            .replace('&', '&amp;')
                            .replace('<', '&lt;')
                            .replace('>', '&gt;')+
                        "</h1>"+
                        self.render_web_svg(urllib
                            .parse
                            .unquote(getfile[5:-4])
                            .replace('&', '&amp;')
                            .replace('<', '&lt;')
                            .replace('>', '&gt;')
                        )
                    )
                    status = 200
                    #ctype = "image/svg+xml; charset=utf-8"
                    ctype = "text/html; charset=utf-8"
                # PDF
                elif getfile.startswith("/pdf/"): #TODO: Security bug

                    #TODO: look for it  in self.server.documents
                    output = self.render_web_pdf()
                    status = 200
                    ctype = "application/pdf"
                    binary = True;
               
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

