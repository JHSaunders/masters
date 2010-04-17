 Event.observe(document, 'dom:loaded', function() {

    HumbleFinance.trackFormatter = function (obj) {
       
        var x = Math.floor(obj.x);
        var data = jsonData[x];
        var text = data.date + " Price: " + data.close + " Vol: " + data.volume;
       
        return text;
    };
   
    HumbleFinance.yTickFormatter = function (n) {
       
        if (n == this.axes.y.max) {
            return false;
        }
       
        return 'R'+n;
    };
   
    HumbleFinance.xTickFormatter = function (n) {
       

        if (n == 0 || n == Math.round(n)) {
            return false;
        }
        n = Math.round(n)
        var date = jsonData[n].date;
//        date = date.split(' ');
//        date = date[2];
       
        return date;
    }
    
    function load_data_and_init(priceData, volumeData, summaryData)
    {
        HumbleFinance.init('market-history', priceData, volumeData, summaryData);
       
        var xaxis = HumbleFinance.graphs.summary.axes.x;
        var prevSelection = HumbleFinance.graphs.summary.prevSelection;
        var xmin = xaxis.p2d(prevSelection.first.x);
        var xmax = xaxis.p2d(prevSelection.second.x);
       
    //    $('dateRange').update(jsonData[xmin].date + ' - ' + jsonData[xmax].date);
       
    //    Event.observe(HumbleFinance.containers.summary, 'flotr:select', function (e) {
    //       
    //        var area = e.memo[0];
    //        xmin = Math.floor(area.x1);
    //        xmax = Math.ceil(area.x2);
    //       
    //        var date1 = jsonData[xmin].date;
    //        var date2 = jsonData[xmax].date;
    //       
    //        $('dateRange').update(jsonData[xmin].date + ' - ' + jsonData[xmax].date);
    //    });
    }
    load_data_and_init(market_data.priceData, market_data.volumeData, market_data.summaryData);    
}); 
