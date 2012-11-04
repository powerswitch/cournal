#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This file is part of Cournal.
# Copyright (C) 2012 Fabian Henze
# 
# Cournal is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Cournal is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Cournal.  If not, see <http://www.gnu.org/licenses/>.

from twisted.spread import pb
from twisted.python.failure import Failure

# 0 - none
# 1 - minimal
# 2 - medium
# 3 - maximal
DEBUGLEVEL = 3

class User(pb.Avatar):
    """
    A remote user.
    """
    def __init__(self, name, server):
        """
        Constructor
        
        Positional arguments:
        name -- Name of the user
        server -- A CournalServer object 
        """
        debug(1, _("New User connected: {}").format(name))
        self.name = name
        self.server = server
        self.remote = None
        self.documents = []
        
    def __del__(self):
        """Destructor. Called when the user disconnects."""
        debug(1, _("User disconnected: {}").format(self.name))
        
    def attached(self, mind):
        """
        Called by twisted, when the corresponding User connects. In our case, the
        user object does not exist without a connected user.
        
        Positional arguments:
        mind -- Reference to the remote pb.Referencable object. used for .callRemote()
        """
        self.remote = mind
       
    def detached(self, mind):
        """
        Called by twisted, when the corresponding User disconnects. This object
        should be destroyed after this method terminated.
        
        Positional arguments:
        mind -- Reference to the remote pb.Referencable object.
        """
        self.remote = None
        for document in self.documents:
            document.remove_user(self)
    
    def perspective_list_documents(self):
        """
        Return a list of all our documents.
        """
        debug(2, _("User {} requested document list").format(self.name))
        
        return list(self.server.documents.keys())
    
    def perspective_join_document(self, documentname):
        """
        Called by the user to join a document session.
        
        Positional arguments:
        documentname -- Name of the requested document session
        """
        debug(2, _("User {} started editing {}").format(self.name, documentname))
        
        document = self.server.get_document(documentname)
        if isinstance(document, Failure):
            return document
        document.add_user(self)
        self.documents.append(document)
        return document
    
    def perspective_ping(self):
        """Called by clients to verify, that the connection is still up."""
        return True
        
    def call_remote(self, method, *args):
        """
        Call a remote method of this user.
        
        Positional arguments:
        method -- Name of the remote method
        *args -- Arguments of the remote method
        """

        self.remote.callRemote(method, *args)

def debug(level, *args):
    """Helper function for debug output"""
    if level <= DEBUGLEVEL:
        print("HTTP:", *args)