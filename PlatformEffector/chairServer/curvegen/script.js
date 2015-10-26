var chart = new Highcharts.Chart({

    chart: {
        renderTo: 'container',
        animation: false,
        type: 'areaspline'
    },
    
    title: {
        text: ''
    },

    xAxis: {
        categories: [-1,-0.8,-0.6,-0.4,-0.2,0,0.2,0.4,0.6,0.8,1]
        //categories: [790 ,785 ,775 ,757 ,733 ,713 ,697 ,686 ,676 ,668 ,666]    
    },

    yAxis:{
        max:6000
    },

    plotOptions: {
        series: {
            point: {
                events: {

                    drag: function (e) {
                    },
                    drop: function () {                        
                        var rounded = Math.round(this.y/100)*100
     
                        chart.series[0].data[this.x].update({
                            y:rounded,
                            draggableY: true
                        }); 
                        
                     	$('#csv').html(chart.getCSV());
                        $('#download').attr('href',"data:application/octet-stream," + encodeURIComponent(chart.getCSV()));
                    }
                }
            },
            stickyTracking: false
        },
        column: {
            stacking: 'normal'
        },
        line: {
            cursor: 'ns-resize'
        }
    },
	tooltip:{
        enabled:true
    },
    series: [{
        name: "Pressure",
        data: [500  ,600 ,700,1100,2100,2600,3100,3600,4100,5600,6000],
        draggableY: true,
        minPointLength: 2,
        dragMinY: 0,
        color: '#ff0000'
    }]

});

$('#csv').html(chart.getCSV());

$('#preview2').html(encodeURIComponent(chart.getCSV()));

$('#download').attr('href',"data:application/octet-stream," + encodeURIComponent(chart.getCSV()));








function readSingleFile(evt) {
    //Retrieve the first (and only!) File from the FileList object
    var f = evt.target.files[0]; 

    if (f) {
      var r = new FileReader();
      r.onload = function(e) { 
	      var contents = e.target.result;  
          var lines = contents.split("\n");
          for (var i=1; i<lines.length; i++) { //start at 1, ignore header
            	var line = lines[i].split(",");
            	chart.series[0].data[i-1].update({
                	y:parseInt(line[1])
                });
          }
      }
      r.readAsText(f);
    } else { 
      alert("Failed to load file");
    }
  }

  document.getElementById('fileinput').addEventListener('change', readSingleFile, false);



$(document).on('change', '.btn-file :file', function() {
  var input = $(this),
      numFiles = input.get(0).files ? input.get(0).files.length : 1,
      label = input.val().replace(/\\/g, '/').replace(/.*\//, '');
  input.trigger('fileselect', [numFiles, label]);
});



