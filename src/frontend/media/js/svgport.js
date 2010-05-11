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

svgport.get_view_coordinates = function(e)
{
    return {X:(e.pageX - $(svgport.div).offset().left),Y:(e.pageY - $(svgport.div).offset().top)};
}

svgport.get_svg_coordinates = function(e)
{
    return {X:(e.pageX - $(svgport.svg).offset().left),Y:(e.pageY - $(svgport.svg).offset().top)};
}


function log_str(str)
{
    $("#log").append("<div>"+ str + "</div>");
}

function logmouse(e)
{
    log_str("("+svgport.get_view_coordinates(e).X + "," + svgport.get_view_coordinates(e).Y+") ("+svgport.get_svg_coordinates(e).X + "," + svgport.get_svg_coordinates(e).Y+")");
}

svgport.onmousedown = function(e)
{
    svgport.state='down';
    svgport.previous_coord = svgport.get_view_coordinates(e);
}

svgport.onmousemove = function(e)
{
    if (svgport.state=='down')
    {
        //logmouse(e);
        cur_coord = svgport.get_view_coordinates(e);
         
        var dif = {}
        dif.X = cur_coord.X-svgport.previous_coord.X
        dif.Y = cur_coord.Y-svgport.previous_coord.Y
        
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

svgport.onmouseup = function(e)
{    
    svgport.state='up'    
}

svgport.onmousewheel = function(e,delta)
{
    if(delta >0)
    {  var mag = 1/(delta*1.2);   }
    else
    {  var mag = -1*(delta*1.2);  }    
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

svgport.convert_from_view_to_canvas = function(x,y)
{
    var old_view = $(svgport.svg).attr("viewBox").split(" ");
    var vx = parseFloat(old_view[0]);
    var vy = parseFloat(old_view[1]);
    var vw = parseFloat(old_view[2]);
    var vh = parseFloat(old_view[3]);
    
    var w = $(svgport.svg).width();
    var h = $(svgport.svg).height();
    
    return {x:vx+vw*x/w,y:vy+vh*y/h}
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
    var m1 = svgport.convert_from_view_to_canvas(svgport.get_svg_coordinates(e).X,svgport.get_svg_coordinates(e).Y);

    nx = 0;//m1.x-nw/2;
    ny = 0;//m1.y-nh/2;
    log_str(m1.x+","+m1.y)
    $(svgport.svg).attr("viewBox", nx+" "+ny+" "+nw+" "+nh);
}
