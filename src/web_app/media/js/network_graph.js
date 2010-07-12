if(network_graph==null)
{
    var network_graph={}    
}

network_graph.onresize = function()
{
    $(network_graph.div).attr("width","100%");
    $(network_graph.svg).attr("width","100%");    
    $(network_graph.svg).attr("height",465);    
}

network_graph.get_view_coordinates = function(e)
{
    return {X:(e.pageX - $(network_graph.div).offset().left),Y:(e.pageY - $(network_graph.div).offset().top)};
}

network_graph.get_svg_coordinates = function(e)
{
    return {X:(e.pageX - $(network_graph.svg).offset().left),Y:(e.pageY - $(network_graph.svg).offset().top)};
}


function log_str(str)
{
    $("#log").append("<div>"+ str + "</div>");
}

function logmouse(e)
{
    log_str("("+network_graph.get_view_coordinates(e).X + "," + network_graph.get_view_coordinates(e).Y+") ("+network_graph.get_svg_coordinates(e).X + "," + network_graph.get_svg_coordinates(e).Y+")");
}

network_graph.onmousedown = function(e)
{
    network_graph.state='down';
    network_graph.previous_coord = network_graph.get_view_coordinates(e);
}

network_graph.onmousemove = function(e)
{
    if (network_graph.state=='down')
    {
        //logmouse(e);
        cur_coord = network_graph.get_view_coordinates(e);
         
        var dif = {}
        dif.X = cur_coord.X-network_graph.previous_coord.X
        dif.Y = cur_coord.Y-network_graph.previous_coord.Y
        
        network_graph.previous_coord = cur_coord;
            
        var old_view = $(network_graph.svg).attr("viewBox").split(" ");
        var vx = parseFloat(old_view[0]);
        var vy = parseFloat(old_view[1]);
        var vw = parseFloat(old_view[2]);
        var vh = parseFloat(old_view[3]);
        
        var h = $(network_graph.svg).attr("height");
        var w = $(network_graph.svg).attr("width");
        
        ratio = h/vh;
        
        nx = vx - (dif.X)/ratio;    
        ny = vy - (dif.Y)/ratio;
        
        $(network_graph.svg).attr("viewBox", nx+" "+ny+" "+vw+" "+vh);
    }
    
}

network_graph.onmouseup = function(e)
{    
    network_graph.state='up'    
}

network_graph.onmousewheel = function(e,delta)
{
    if(delta >0)
    {  var mag = 1/(delta*1.2);   }
    else
    {  var mag = -1*(delta*1.2);  }    
    network_graph.zoom(e,mag);    
    return false;
}

network_graph.setup = function(div_id, svg_id, src_url)
{
    network_graph.div = div_id;
    network_graph.svg = svg_id;
    network_graph.src_url = src_url;
    
    network_graph.onresize();
    $(window).resize(network_graph.onresize);
    $(network_graph.div).mousedown(network_graph.onmousedown);
    $(network_graph.div).mousemove(network_graph.onmousemove);
    $(document).mouseup(network_graph.onmouseup);
    $(network_graph.div).mousewheel(network_graph.onmousewheel);
    
    $('#dialog').dialog({autoOpen:false,modal:true, minWidth:700,width:700, position: 'top'});         
}

network_graph.convert_from_view_to_canvas = function(x,y)
{
    var old_view = $(network_graph.svg).attr("viewBox").split(" ");
    var vx = parseFloat(old_view[0]);
    var vy = parseFloat(old_view[1]);
    var vw = parseFloat(old_view[2]);
    var vh = parseFloat(old_view[3]);
    
    var w = $(network_graph.svg).width();
    var h = $(network_graph.svg).height();
    
    return {x:vx+vw*x/w,y:vy+vh*y/h}
}

network_graph.zoom = function(e,mag)
{
    var old_view = $(network_graph.svg).attr("viewBox").split(" ");
    var x = parseFloat(old_view[0]);
    var y = parseFloat(old_view[1]);
    var w = parseFloat(old_view[2]);
    var h = parseFloat(old_view[3]);
    
    nw=w*mag;
    nh=h*mag;
    
    nx = x+w/2-nw/2;
    ny = y+h/2-nh/2;
    
    $(network_graph.svg).attr("viewBox", nx+" "+ny+" "+nw+" "+nh);
}

network_graph.update = function()
{
    $.ajax({url:network_graph.src_url,
            dataType: "xml",
            cache: false,
            success: function(data)
                     {
                       $(network_graph.svg+" > g").replaceWith($("svg > g",data));
                       $.unblockUI();
                     }
            });    
}

network_graph.send_and_refresh = function(url)
{
    $.get(url,function(data){network_graph.update()});    
}

network_graph.send_and_refresh_with_progress = function(url)
{
    $.blockUI();
    $.get(url,function(data){network_graph.update()});   
}

network_graph.refresh_form = function(data)
{   
    
    if(data=="success")
    {
        $('#dialog').dialog('close');
        network_graph.update();
    }
    else
    {
        $('#dialog').html(data);
        $('#dialog').dialog( "option", "title", $('#dialog-title').text());      
        $('#dialog-title').hide();
        $('#dialog form').ajaxForm({success:network_graph.refresh_form,cache: false});
    }
}

network_graph.open_form = function(url)
{
    $('#dialog').html("loading...");
    $('#dialog').dialog( "option", "title","loading...");    
    $('#dialog').dialog('open');
    $.ajax({url:url,success:network_graph.refresh_form,cache: false}); 
}
