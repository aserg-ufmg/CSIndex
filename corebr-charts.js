google.charts.load('current', {'packages':['corechart']});

google.charts.setOnLoadCallback(drawChartConfs);
google.charts.setOnLoadCallback(drawChartDepts);
google.charts.setOnLoadCallback(drawChartProfs);

//corebr_area_prefix= "se";

var corebr_confs_file= "data/" + corebr_area_prefix + "-out-confs.csv";
var corebr_depts_file= "data/" + corebr_area_prefix + "-out-scores.csv";
var corebr_profs_file= "data/" + corebr_area_prefix + "-out-profs.csv";
    
function drawChartConfs() {
  $.get(corebr_confs_file, function(csvString) {
  var arrayData = $.csv.toArrays(csvString, {onParseValue: $.csv.hooks.castToScalar});
  var data= new google.visualization.DataTable();
  data.addColumn('string', 'Conferences');
  data.addColumn('number', 'Papers');
  data.addRows(arrayData);
      
  var view = new google.visualization.DataView(data);
  view.setColumns([0, 1,  
                   { calc: "stringify",
                     sourceColumn: 1,
                     type: "string",
                     role: "annotation" },
                  ]);

  var options = { 'width': 800,
                  'height': 500,
                  'fontSize': 13,
                  'legend': { position: "none" },
                  'chartArea': {left:40, top:30, right:30,  width:'80%',height:'65%'},
                  'hAxis': { slantedText:true, slantedTextAngle:45 }, 
                  'annotations': { alwaysOutside:true },
                  'titleTextStyle': { bold: false }
                };
                       
  //options ['title']= 'Score= A + (0.66 * B) + (0.33 * C), A= papers in top confs; B= papers in "below-the-fold" confs; C= papers in other confs',
                    
  var chart = new google.visualization.ColumnChart(document.getElementById('chart_confs'));
  chart.draw(view, options);
  });
}
  
function drawChartDepts() {
  $.get(corebr_depts_file, function(csvString) {
  var arrayData = $.csv.toArrays(csvString, {onParseValue: $.csv.hooks.castToScalar});
  var data= new google.visualization.DataTable();
  data.addColumn('string', 'Departments');
  data.addColumn('number', 'Score');
  data.addRows(arrayData);
      
  var view = new google.visualization.DataView(data);
  view.setColumns([0, 1,  
                   { calc: "stringify",
                     sourceColumn: 1,
                     type: "string",
                     role: "annotation" },
                  ]);

  var options = { 'width': 800,
                  'height': 500,
                  'fontSize': 13,
                  'legend': { position: "none" },
                  'chartArea': {left:40, top:30, right:30,  width:'80%',height:'65%'},
                  'hAxis': { slantedText:true, slantedTextAngle:45 }, 
                  'annotations': { alwaysOutside:true },
                  'titleTextStyle': { bold: false }
                };
                       
  //options ['title']= 'Score= A + (0.66 * B) + (0.33 * C), A= papers in top confs; B= papers in "below-the-fold" confs; C= papers in other confs',
                    
  var chart = new google.visualization.ColumnChart(document.getElementById('chart_depts'));
  chart.draw(view, options);
  });
}

function drawChartProfs() {
  $.get(corebr_profs_file, function(csvString) {
  var arrayData = $.csv.toArrays(csvString, {onParseValue: $.csv.hooks.castToScalar});
  var data= new google.visualization.DataTable();
  data.addColumn('string', 'Departments');
  data.addColumn('number', 'Profs');
  data.addRows(arrayData);
      
  var view = new google.visualization.DataView(data);
  view.setColumns([0, 1,  
                   { calc: "stringify",
                     sourceColumn: 1,
                     type: "string",
                     role: "annotation" },
                  ]);

  var options = { 'width': 800,
                  'height': 500,
                  'fontSize': 13,
                  'legend': { position: "none" },
                  'chartArea': {left:40, top:30, right:30,  width:'80%',height:'65%'},
                  'hAxis': { slantedText:true, slantedTextAngle:45 }, 
                  'annotations': { alwaysOutside:true },
                  'titleTextStyle': { bold: false }
                };
                       
  //options ['title']= 'Score= A + (0.66 * B) + (0.33 * C), A= papers in top confs; B= papers in "below-the-fold" confs; C= papers in other confs',
                    
  var chart = new google.visualization.ColumnChart(document.getElementById('chart_profs'));
  chart.draw(view, options);
  });
}
