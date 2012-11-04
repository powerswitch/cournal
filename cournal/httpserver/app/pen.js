function Pen(strokelist) {
    this.strokelist = strokelist;
    this.stroke = "";
    this.coords = Array();
    this.canvas = document.getElementById("drawarea");
    this.context = this.canvas.getContext('2d');
    this.context.strokeStyle = "rgba(0,0,128,0.5)";
    this.context.beginPath();
    this.http=new XMLHttpRequest(); // older browsers would neither support XMLHttpRequest nor Canvas
    
    this.send = function()
    {
        console.log(this.stroke);
        this.http.open("POST", this.stroke, true);
        this.http.send();
    }
    
    this.mouse_down = function(mouse) {
        this.context.save();
        this.context.beginPath();
        this.context.moveTo(mouse.x, mouse.y);
        this.stroke = "<insert name=\""+documentname+"\" page=\"1\"><stroke>";
        this.stroke += mouse.x + " " + mouse.y + " ";
        this.coords.push(mouse.x);
        this.coords.push(mouse.y);
        // TODO: add linewidth and color
    }
    
    this.mouse_up = function(mouse) {
        if (this.stroke != "")
        {
            this.context.restore()
            this.context.lineTo(mouse.x, mouse.y);
            //this.context.quadraticCurveTo(0.5,0.5,mouse.x, mouse.y);
            //this.context.clearRect(0,0,this.canvas.width,this.canvas.height);
            this.context.stroke();
            this.context.moveTo(mouse.x, mouse.y);
            this.stroke += mouse.x + " " + mouse.y;
            this.stroke += "</stroke></insert>";
            this.send();
            this.stroke = "";
            this.coords.push(mouse.x);
            this.coords.push(mouse.y);
            this.strokelist.push(new Stroke("a", "b", "c", "d"));
        }
    }
    
    this.mouse_move = function(mouse) {
        //this.context.clearRect(0,0,this.canvas.width,this.canvas.height);
        this.context.lineTo(mouse.x, mouse.y);
        this.context.stroke();
        this.context.beginPath();
        this.context.moveTo(mouse.x, mouse.y);
        this.stroke += mouse.x + " " + mouse.y + " ";
        this.coords.push(mouse.x);
        this.coords.push(mouse.y);
    }
}