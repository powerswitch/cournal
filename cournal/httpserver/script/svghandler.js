function setpage()
{
    var xmlhttp;
    var interval;
    if (window.XMLHttpRequest)
    {
        xmlhttp=new XMLHttpRequest();
    }
    else
    {
        xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
    }
    xmlhttp.open("GET","/svg/"+DOC_NAME+".svg?page="+page,true);
    xmlhttp.onreadystatechange=function()
    {
        if (xmlhttp.readyState==4)
        {
            if (xmlhttp.status==200)
            {
                clearInterval(interval);
                document.getElementById("preview").innerHTML = xmlhttp.responseText.replace(/<\?xml[\w\d\s='\"\.\-]*\?>/, "");
                document.getElementById("svg_header").innerHTML = "Page "+page+" of "+MAX_PAGE;
            } else {
                clearInterval(interval);
                document.getElementById("preview").innerHTML = information_svg[0]
                document.getElementById("svg_header").innerHTML = "Error loading page "+page+" of "+MAX_PAGE+ " ["+xmlhttp.status+"]";
            }
        }
    }
    xmlhttp.send();
    interval = setInterval("page_loading();",300);
}

function page_loading()
{
    document.getElementById("svg_header").innerHTML = "Page "+page+" of "+MAX_PAGE+" (loading, please wait!)";
    content = document.getElementById("preview").innerHTML;
    content = content.replace(/<\/svg>/g, "");
    content = content + information_svg[1].replace(/<\?xml[\w\d\s='\"\.\-]*\?>.*<svg[\r\n\t\f\w\d\s='\"\.\-\#\:\/]*/, "");
    content = content + information_svg[1].replace(/<svg[\r\n\t\f\w\d\s='\"\.\-\#\:\/]*/, "");
    document.getElementById("preview").innerHTML = content;
}

function nextpage()
{
    if (page < MAX_PAGE)
    {
        page++;
        setpage();
    }    
}

function prevpage()
{
    if (page > 1)
    {
        page--;
        setpage();
    }
}

setInterval("check_page();",5000);
information_svg = new Array(2);
last_timestamp = 0;

load_image("/templates/default/image/error.svg", 0);
load_image("/templates/default/image/loading.svg", 1);

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
                    setpage();
                }
            } else {
                document.getElementById("preview").innerHTML = information_svg[0]
                document.getElementById("svg_header").innerHTML = "Error loading page "+page+" of "+MAX_PAGE+ " [timestamp error]";
            }
        }
    }
    timestamp.send();
}