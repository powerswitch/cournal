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

#TODO: URI ENCODE AND DECODE

from twisted.internet import reactor, protocol
from twisted.protocols.basic import LineReceiver
from cournal.network import network
from cournal.document.document import Document
from cournal.document import xojparser
import sys
import cgi
import cournal
import urllib.parse

# 0 - none
# 1 - minimal
# 2 - medium
# 3 - maximal
DEBUGLEVEL = 3

http_users = 0

class Httpserver(LineReceiver):
    header_template = """HTTP/1.1 {status}
Server: Cournal/{version}
Content-Length: {length}
Content-Language: en
Connection: keep-alive
Content-Type: {ctype}

{output}"""

    whitelist = [
        "/templates/default/style.css",
        "/templates/default/image/cournal.svg",
        "/templates/default/image/download.png",
        "/templates/default/image/download_highlight.png",
        "/templates/default/image/preview.png",
        "/templates/default/image/preview_highlight.png",
        "/status.html",
        "/imprint.html",
        "/",
        "/index.html",
        "/documents.html"
    ]
    
    def HTML_status(self):
        """ Creates a status HTML page"""
        output = """<h1>Server status</h1>
        All servers are running.
        <h2>Users online</h2>
        <table border="0">
            <tr>
                <td>Cournal users:</td>
                <td>{cournal_users}</td>
            </tr>
            <tr>
                <td>HTTP users:</td>
                <td>{http_users}</td>
            </tr>
        </table>
        """
        return output.format(
            cournal_users=self.count_users(),
            http_users=http_users
        )

    def count_users(self):
        count = 0
        for document in self.realm.server.documents:
            count = count + len(self.realm.server.documents[document].users)
        return count
    
    def HTML_documents(self):
        output = "<h1>Documents</h1><div id='doclist'>"
        row = """<div class='dlrow'>
                    <div class='dlsymbols'>
                        <a href='/pdf/{documentname}.pdf'>
                            <img src='/templates/default/image/download.png'
                                 alt='[dwnld]'
                                 onmouseover="src='/templates/default/image/download_highlight.png'"
                                 onmouseout="src='/templates/default/image/download.png'"
                            />
                        </a>
                        <a href='/svg/{documentname}.pdf'>
                            <img src='/templates/default/image/preview.png'
                                 alt='[prvw]'
                                 onmouseover="src='/templates/default/image/preview_highlight.png'"
                                 onmouseout="src='/templates/default/image/preview.png'"
                            />
                        </a>
                    </div>
                    <div class='dlname'>
                        {documentname}
                    </div>
                    <div class='clear'></div>
                  </div>"""
        for document in self.realm.server.documents:
            output = output + row.format(
                documentname=document.replace('&', '&amp;')
                                     .replace('<', '&lt;')
                                     .replace('>', '&gt;')
            )
        output = output + "</div>"
        return output
        
    def send(self, output, ctype="text/html", status=200, version=0.1, binary=False):
        """ Send HTTP data over the network connection """
        if binary:
            header = self.header_template.format(
                length=len(output),
                ctype=ctype,
                status=status,
                version=version,
                output=""
            ).encode()
            header = header + output
        else:
            header = self.header_template.format(
                length=len(output),
                ctype=ctype,
                status=status,
                version=version,
                output=output
            ).encode()
            
        self.transport.write(header)

    def template(self, output):
        """ Put the specific output into the template """
        try:
            template_top = open(cournal.__path__[0]+"/httpserver/templates/default/top.html","r")
            template_bottom = open(cournal.__path__[0]+"/httpserver/templates/default/bottom.html","r")
            output = '{a}{b}{c}'.format(
                a=template_top.read(),
                b=output,
                c=template_bottom.read()
            )
        except IOError:
            print("Template error!", file=sys.stderr)
        return output
        
    def connectionLost(self, reason):
        """ What to do when the connection is closed """
        global http_users
        debug(3, "connection",http_users,"lost")
        http_users -= 1
    
    def connectionMade(self):
        """ What to do when a new connection is made """
        global http_users
        self.whitelist
        http_users += 1
        debug(3, "connection",http_users,"made")

        for document in self.realm.server.documents:
            self.whitelist.append("/pdf/"+document+".pdf")

    def on_connected(self):
        print("connected")

    def render_web_pdf(self):
        # Open a preview document
        # TODO: This is not, what I was looking for :( Need more time!
        document = Document(cournal.__path__[0]+"/httpserver/documents/webpreview.pdf")
        network.set_document(document)
        connection = network.connect("127.0.0.1", self.dport)
        document.export_pdf("output.pdf")
        readfile = open("output.pdf","rb")
        output = readfile.read()
        return output

        
    def lineReceived(self, data):
        """ If a readable line is received """
        binary = False;
        if data.decode().upper().find("GET") >= 0:
            getfile = data.decode().split(" ")[1]
            debug(3, "GET ", getfile)
            if urllib.parse.unquote(getfile) in self.whitelist:
                # Symlinks
                if getfile == "/" or getfile == "/index.html":
                    getfile = "/status.html"
                
                # Html building functions
                if getfile == "/status.html":
                    output = self.HTML_status() 
                    status = 200
                    ctype = "text/html; charset=utf-8"
                elif getfile == "/documents.html":
                    output = self.HTML_documents() 
                    status = 200
                    ctype = "text/html; charset=utf-8"
                # PDF
                elif getfile.find("/pdf/") >= 0: #TODO: Security bug

                    #TODO: look for it  in self.realm.server.documents
                    output = self.render_web_pdf()
                    status = 200
                    ctype = "application/pdf"
                    binary = True;
                    
                    #print(connection)
                    #d.addCallbacks(self.on_connected)
                    
                    #output = "No PDF creation implemented yet :("
                    #status = 404
                    #ctype = "text/plain; charset=utf-8"
                
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
                        if getfile.find(".css") >= 0:
                            ctype = "text/css; charset=utf-8"
                        elif getfile.find(".html") >= 0:
                            ctype = "text/html; charset=utf-8"
                        elif getfile.find(".svg") >= 0:
                            ctype = "image/svg+xml; charset=utf-8"
                        elif getfile.find(".png") >= 0:
                            ctype = "image/png"
                            binary = True
                        elif getfile.find(".xoj") >= 0:
                            ctype = "text/xml; charset=utf-8"
                        elif getfile.find(".pdf") >= 0:
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
                if getfile.find(".html") >= 0:
                    output = self.template(output)
                
                self.send(output,ctype=ctype,status=status,binary=binary)
            
            else:
                self.send(
                    self.template(
                        "<h1>404 - File not found</h1>This file was not found on the server"
                    ),
                    ctype="text/html; charset=utf-8",
                    status=404
                )
                
def debug(level, *args):
    """Helper function for debug output"""
    if level <= DEBUGLEVEL:
        print(*args)
                
def main():
    factory = protocol.ServerFactory()
    factory.protocol = Httpserver
    reactor.listenTCP(8000,factory)
    debug(3, "HTML backend ready!")
    reactor.run()

if __name__ == '__main__':
    main()

