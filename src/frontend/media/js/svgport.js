if(svgport==null)
{
    var svgport={}    
}

svgport.onresize = function()
{
    $(svgport.svg).attr("width","100%");
    $(svgport.svg).attr("height",document.documentElement.clientHeight-$(svgport.svg).offset().top-2);        
    $(svgport.div).attr("width","100%");
    $(svgport.div).attr("height",document.documentElement.clientHeight-$(svgport.svg).offset().top-2);  
}

svgport.get_canvas_coordinates = function(e)
{
    return {X:(e.pageX - $(svgport.div).offset().left),Y:(e.pageY - $(svgport.div).offset().top)};
}

function log_str(str)
{
    $("#log").append("<div>"+ str + "</div>");
}

function logmouse(e)
{
    log_str(svgport.get_canvas_coordinates(e).X + "," + svgport.get_canvas_coordinates(e).Y) 
}

svgport.onmousedown = function(e)
{
    svgport.state='down';
    svgport.previous_coord = svgport.get_canvas_coordinates(e);
}

svgport.onmousemove = function(e)
{
    if (svgport.state=='down')
    {
        //logmouse(e);
        cur_coord = svgport.get_canvas_coordinates(e);
         
        var dif = {}
        dif.X = cur_coord.X-svgport.previous_coord.X
        dif.Y = cur_coord.Y-svgport.previous_coord.Y
        
        if(true)
        {
            svgport.previous_coord = cur_coord;
             
            var old_view = $(svgport.svg).attr("viewBox").split(" ");
            var vx = parseFloat(old_view[0]);
            var vy = parseFloat(old_view[1]);
            var vw = parseFloat(old_view[2]);
            var vh = parseFloat(old_view[3]);
            
            var h = $(svgport.svg).attr("height");
            var w = $(svgport.svg).attr("width");
            
            ratio = h/vh;
            
            nx = vx - (dif.X)/ratio;    
            ny = vy - (dif.Y)/ratio;
            
            $(svgport.svg).attr("viewBox", nx+" "+ny+" "+vw+" "+vh);
         }
    }
    
}

svgport.onmouseup = function(e)
{    
    svgport.state='up'    
}

svgport.onmousewheel = function(e,delta)
{
//    logmouse(e);
//    log_str(delta);
    
    if(delta <0)
    {
        var mag = -1/(delta*1.2);
    }
    else
    {
       var mag = (delta*1.2);    
    }
    
    svgport.zoom(e,mag);
    
    return false;
}

svgport.setup = function(div_id)
{
    svgport.div = div_id;
    svgport.svg = div_id+" > svg";
   
    svgport.onresize();        
    $(window).resize(svgport.onresize);
    $(svgport.div).mousedown(svgport.onmousedown);
    $(svgport.div).mousemove(svgport.onmousemove);
    $(document).mouseup(svgport.onmouseup);
    $(svgport.div).mousewheel(svgport.onmousewheel);     
}

svgport.zoom = function(e,mag)
{
    
    var old_view = $(svgport.svg).attr("viewBox").split(" ");
    var x = parseFloat(old_view[0]);
    var y = parseFloat(old_view[1]);
    var w = parseFloat(old_view[2]);
    var h = parseFloat(old_view[3]);
    
    nw=w*mag;
    nh=h*mag;
    
    var dx = svgport.get_canvas_coordinates(e).X;// - $(svgport.svg).attr("width")/2;
    var dy = svgport.get_canvas_coordinates(e).Y;// - $(svgport.svg).attr("height")/2;
    
    dif_mag = (Math.abs(mag)-1);
    if(mag<0){dif_mag*=-1;}
    
    
    dx = dx*dif_mag;
    dy = dy*dif_mag;
        
    nx = x + (w - nw)/2;    
    ny = y + (h - nh)/2;
    
    $(svgport.svg).attr("viewBox", nx+" "+ny+" "+nw+" "+nh);
}
