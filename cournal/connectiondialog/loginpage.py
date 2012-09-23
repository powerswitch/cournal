#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This file is part of Cournal.
# Copyright (C) 2012 Simon Vetter
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

from gi.repository import Gtk, GObject

import cournal
from cournal.network.multi_net import networks, current_network

class LoginPage(Gtk.Box):
    """
    A widget, which allows the user to browse and open remote documents.
    """
    __gsignals__ = {
        "logged_in": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
        "logging_in": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (str,)),
        "log_in_failed": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
    }

    def __init__(self, dialog):
        """
        Constructor.
        
        Positional arguments:
        dialog -- The parent GtkDialog widget.
        """
        Gtk.Box.__init__(self)
        self.dialog = dialog
        
        builder = Gtk.Builder()
        builder.set_translation_domain("cournal")
        builder.add_from_file(cournal.__path__[0] + "/user_login.glade")
        self.main_grid = builder.get_object("main_grid")
        self.username = builder.get_object("username")
        self.password = builder.get_object("password")
        self.message_text = builder.get_object("message_text")
        
        self.connect("map", self.on_map_event)
   
    def response(self, widget, response_id):
        """
        Called, when the user clicked on a button ('Connect' or 'Abort') or
        when the dialog is closed.
        If the user clicked on connect, we join a document session.
        
        Positional arguments:
        widget -- The widget, which triggered the response.
        response_id -- A Gtk.ResponseType indicating, which button the user pressed.
        """
        if response_id == Gtk.ResponseType.ACCEPT:
            d = networks[current_network].log_in(self.username.get_text(),self.password.get_text())
            d.addCallback(self.logged_in)
            self.emit("logging_in", self.username.get_text())
        else:
            networks[current_network].disconnect()
            self.dialog.destroy()            
    
    def logged_in(self, info):
        if networks[current_network].is_logged_in:
            self.emit("logged_in")
        else:
            self.emit("log_in_failed")
            self.message_text.show()
    
    def on_map_event(self, _):
        """
        Called, when the widget becomes visible.
        As this widget is so large, that all previous pages would look ugly, we
        add ourselves to the layout only when becoming visible.
        """
        if len(self.get_children()) == 0:
            self.add(self.main_grid)
            self.show_all()

