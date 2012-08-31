function setpage()
{
    var xmlhttp;
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
    if (xmlhttp.readyState==4 && xmlhttp.status==200)
        {
            document.getElementById("preview").innerHTML = xmlhttp.responseText;
            document.getElementById("svg_header").innerHTML = "Page "+page+" of "+MAX_PAGE;
        }
    }
    xmlhttp.send();
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