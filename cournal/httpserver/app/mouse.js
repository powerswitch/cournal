function Mouse(tool) {
    this.tool = tool;
    /*this.down = new Array(3);
    this.down[0] = false;
    this.down[1] = false;
    this.down[2] = false*/
    this.down = [false, false, false]

    this.init = function()
    {
        this.canvas = document.getElementById("drawarea");
        this.canvas.addEventListener('mousemove', this.ev_mousemove, false);
        this.canvas.addEventListener('mousedown', this.ev_mousedown, false);
        this.canvas.addEventListener('mouseup', this.ev_mouseup, false);
        this.canvas.addEventListener('mouseout', this.ev_mouseout, false);
        this.canvas.addEventListener('mouseover', this.ev_mouseover, false);
        document.addEventListener('mousedown', this.doc_mousedown, false);
        document.addEventListener('mouseup', this.doc_mouseup, false);
    }
    
    /**
     * User clicked mouse button
     */
    this.doc_mousedown = function(ev)
    {
        var btn = ev.button;
        if ((btn > -1) && (btn < 3))
        {
            mouse.down[btn] = 1;
        }
    }

    /**
     * User released mouse button
     */
    this.doc_mouseup = function(ev)
    {
        var btn = ev.button;
        if ((btn > -1) && (btn < 3))
        {
            mouse.down[btn] = 0;
        }
    }

    /**
     * Mouse enters drawing area
     */
    this.ev_mouseover = function(ev)
    {
        if (mouse.down[0])
        {
            var m = mouse.ev_pos(ev)
            mouse.tool.active.mouse_down(m);
        }
    }

    /**
     * Mouse leaves drawing area
     */
    this.ev_mouseout = function(ev)
    {
        if (mouse.down[0])
        {
            var m = mouse.ev_pos(ev)
            m.y -= mouse.canvas.offsetTop - 83;
            mouse.tool.active.mouse_up(m);
        }
    }

    /**
     * User pressed mouse key on drawing area
     */
    this.ev_mousedown = function(ev)
    {
        if (ev.button == 0)
        {
            var m = mouse.ev_pos(ev);
            mouse.tool.active.mouse_down(m);
        }
    }   

    /**
     * User released mouse key on drawing area
     */
    this.ev_mouseup = function(ev)
    {
        if (ev.button == 0)
        {
            var m = mouse.ev_pos(ev);
            mouse.tool.active.mouse_up(m);
        }
    }

    /**
     * User moved mouse in drawing area
     */
    this.ev_mousemove = function(ev)
    {
        if (mouse.down[0] > 0)
        {
            var m = mouse.ev_pos(ev);
            mouse.tool.active.mouse_move(m);
        }
    }

    /**
     * Translate mouse postition
     */
    this.ev_pos = function(ev)
    {
        if (ev.layerX || ev.layerX == 0) { // Firefox
            x = ev.layerX;
            y = ev.layerY;
        } else if (ev.offsetX || ev.offsetX == 0) { // Opera
            x = ev.offsetX;
            y = ev.offsetY;
        }
        return {x: x, y: y};
    }    
}