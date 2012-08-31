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

import cournal
import sys

class Html:
    """ HTTP header template"""
    header_template = """HTTP/1.1 {status}
Server: Cournal/{version}
Content-Length: {length}
Content-Language: en
Connection: keep-alive
Content-Type: {ctype}

{output}"""    
    
    def __init__(self, documents, transport):
        self.documents = documents
        self.transport = transport
        self.http_users = 0
    
    def HTML_SVG(self, documentname, svg, maxpage):
        """ Creates a page that displays a specific SVG file """
        #TODO: Create a reloading script, replace hardcoded svg with <object>
        output = """<h1>{documentname}</h1>
        <script type='application/javascript'>
            DOC_NAME='{documentname}';
            MAX_PAGE={maxpage};
            page=1;
            setInterval("setpage();",5000);
        </script>
        <script type='application/javascript' src='/script/svghandler.js'>
        </script>
        
        <div class='preview_area'>
            {navigation_bar}
            <div class='preview' id='preview'>
            {svg}
            </div>
        </div>
        <br /><br />"""
        
        if maxpage > 1:
            navigation_bar = """
            <div class='navbar'>
                <div class='svg_button' id='svg_prev' onclick='prevpage()'> &lt; </div>
                <div class='svg_button' id='svg_next' onclick='nextpage()'> &gt; </div>
                <div class='svg_header' id='svg_header'>Page 1 of {maxpage}</div>
                <div class='clear'></div>
            </div>""".format(maxpage=maxpage)
        else:
            navigation_bar = ""
        
        return output.format(
            documentname=documentname
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;'),
            svg=svg,
            navigation_bar=navigation_bar,
            maxpage=maxpage
            )
    
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
            http_users=0#http_users #FIXME: Argument me
            )

    def count_users(self):
        """ Count current cournal users """
        count = 0
        for document in self.documents:
            count += len(self.documents[document].users)
        return count

    def HTML_documents(self):
        """ Create a HTML page that displays all current cournal documents """
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
                        <a href='/svg/{documentname}.html'>
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
        for document in self.documents:
            output = output + row.format(
                documentname=document.replace('&', '&amp;')
                                     .replace('<', '&lt;')
                                     .replace('>', '&gt;')
            )
        output = output + "</div>"
        return output

    def send(self, output, ctype="text/html", status=200, version=0.1, binary=False):
        """
        Send HTTP data over the network connection
        
        Arguments:
        output -- output to be sent
        ctype -- MIME type of the content
        status -- HTTP status code
        version -- version of the HTTP server
        binary -- send binary data
        
        """
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
             with open(cournal.__path__[0]+"/httpserver/templates/default/top.html","r") as top:
                 template_top = top.read()
             with open(cournal.__path__[0]+"/httpserver/templates/default/bottom.html","r") as bottom:
                  template_bottom = bottom.read()
             output = template_top + output + template_bottom
         except IOError:
             print("Template error!", file=sys.stderr)
         return output
        