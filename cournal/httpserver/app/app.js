/**
 * Initialisation on load
 */
function init()
{
    //context = canvas.getContext('2d');
    //context.beginPath();
    //context.moveTo(0, 0);
    //context.strokeStyle = "#ff0000";
    //context.strokeStyle = "rgba(0,0,128,0.9)";
    tool = new Tool();
    this.strokes = new Array();
    tool.active = new Pen(this.strokes);
    mouse = new Mouse(tool);
    mouse.init();
    this.canvas = document.getElementById("drawarea");
    this.context = this.canvas.getContext('2d');
}

/**
 * Redraw context
 */
function redraw()
{
    this.context.clearRect(0,0,this.canvas.width,this.canvas.height);
}

window.onload = init();