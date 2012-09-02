/* !/usr/bin/env python3
 * -*- coding: utf-8 -*-

 * Cournal: A collaborative note taking and journal application with a stylus.
 * Copyright (C) 2012 Simon Vetter
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

/**
 * Downloads the current page and displays it
 * Features: * Loading icon after 300 ms
 *           * Error message
 */
function display_page()
{
    var xmlhttp;
    var interval;
    // Create AJAX Object
    if (window.XMLHttpRequest)
    {
        xmlhttp=new XMLHttpRequest();
    }
    else
    {
        xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
    }
    // Get page
    xmlhttp.open("GET","/svg/"+DOC_NAME+".svg?page="+page,true);
    
    // If page loading is done:
    xmlhttp.onreadystatechange=function()
    {
        if (xmlhttp.readyState==4)
        {
            // 200 = Downloaded correctly
            if (xmlhttp.status==200)
            {
                clearInterval(interval);
                document.getElementById("preview").innerHTML = xmlhttp.responseText.replace(/<\?xml[\w\d\s='\"\.\-]*\?>/, "");
                document.getElementById("svg_header").innerHTML = "Page "+page+" of "+MAX_PAGE;
            // Else: Display error message
            } else {
                clearInterval(interval);
                document.getElementById("preview").innerHTML = information_svg[0]
                document.getElementById("svg_header").innerHTML = "Error loading page "+page+" of "+MAX_PAGE+ " ["+xmlhttp.status+"]";
            }
        }
    }
    
    // Start page loading
    xmlhttp.send();
    interval = setInterval("page_loading();",300); // Set loading icon timeout interval
}

/**
 * Display a loading icon
 */
function page_loading()
{
    document.getElementById("svg_header").innerHTML = "Page "+page+" of "+MAX_PAGE+" (loading, please wait!)";
    content = document.getElementById("preview").innerHTML;
    content = content.replace(/<\/svg>/g, ""); // cut end of original svg
    // cut beginning of loading svg and merge
    content = content + information_svg[1].replace(/<\?xml[\w\d\s='\"\.\-]*\?>.*<svg[\r\n\t\f\w\d\s='\"\.\-\#\:\/]*/, "");
    //content = content + information_svg[1].replace(/<svg[\r\n\t\f\w\d\s='\"\.\-\#\:\/]*/, "");
    document.getElementById("preview").innerHTML = content;
}

/**
 * Set next page and display it
 */
function nextpage()
{
    if (page < MAX_PAGE)
    {
        page++;
        display_page();
    }    
}

/**
 * Set previous page and display it
 */
function prevpage()
{
    if (page > 1)
    {
        page--;
        display_page();
    }
}

/**
 * Load image into cache
 */
function load_image(path, nr)
{
    var xmlhttp_image;
    if (window.XMLHttpRequest)
    {
        xmlhttp_image=new XMLHttpRequest();
    }
    else
    {
        xmlhttp_image=new ActiveXObject("Microsoft.XMLHTTP");
    }
    xmlhttp_image.open("GET",path,true);
    xmlhttp_image.onreadystatechange=function()
    {
        if (xmlhttp_image.readyState==4 && xmlhttp_image.status==200)
        {
            information_svg[nr] = xmlhttp_image.responseText;
        }
    }
    xmlhttp_image.send();
}

/**
 * Check page time stamp and reload if nessesary
 */
function check_page()
{
    var timestamp;
    if (window.XMLHttpRequest)
    {
        timestamp=new XMLHttpRequest();
    }
    else
    {
        timestamp=new ActiveXObject("Microsoft.XMLHTTP");
    }
    timestamp.open("GET","/svg/"+DOC_NAME+".svg?timestamp="+page,true);
    timestamp.onreadystatechange=function()
    {
        if (timestamp.readyState==4)
        {
            if (timestamp.status==200)
            {
                if (timestamp.responseText != last_timestamp)
                {
                    last_timestamp = timestamp.responseText.replace(/<\?xml[\w\d\s='\"\.\-]*\?>/,"");
                    display_page();
                }
            } else {
                document.getElementById("preview").innerHTML = information_svg[0]
                document.getElementById("svg_header").innerHTML = "Error loading page "+page+" of "+MAX_PAGE+ " [t"+timestamp.status+"]";
            }
        }
    }
    timestamp.send();
}

/**
 * Global functions
 */

setInterval("check_page();",5000);
information_svg = new Array(2);
last_timestamp = 0;

load_image("/templates/default/image/error.svg", 0);
load_image("/templates/default/image/loading.svg", 1);
