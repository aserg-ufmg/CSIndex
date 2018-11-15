var fs = require('fs');
var assert = require('assert');
var $ = jQuery = require('jQuery');
require('./jquery.csv.js');

function cvstest(csvfile, csvtypes) {
  console.log ("Testing " + csvfile);
  var t1 = csvtypes.length;
  fs.readFile(csvfile, 'UTF-8', function (err, csv) {
      $.csv.toArrays(csv, {}, function (err, data) {
          for (var i = 0, len = data.length; i < len; i++) {
              t2 = data[i].length;
              assert.equal(t1,t2, "Incorrect number of columns in row " + i);
              for (var j = 0; j < t1; j++) {
                 if (csvtypes[j] === "number") {
                    x = Number(data[i][j]);
                    assert(!isNaN(x), "is not a number: row " + i + ", column " + j);
                 }
              }
          }
      });
  });
}

function test(file) {
   if ( file.endsWith("-out-confs.csv") ||
        file.endsWith("-out-journals.csv") ||
        file.endsWith("-out-scores.csv") ||
        file.endsWith("-out-profs.csv")) {
      cvstest(file, [ "string", "number"]); }

   if ( file.endsWith("-out-papers.csv") ||
        (file === "trending.csv") ) {
      cvstest(file, ["number", "string", "string", "string", "string",
                     "string", "string", "string", "string", "number"]) ;
   }

   if ( file.endsWith("-out-stats.csv") ) {
      cvstest(file, ["string", "string", "number", "number", "number",
                     "number", "string", "number"]) ;
   }

   if ( file.endsWith("-out-stats-journals.csv") ) {
      cvstest(file, ["string", "string", "number", "number", "string",
                     "number"]) ;
   }
}

process.argv.forEach(function (val, index, array) {
  val = val.replace("data/", "")
  test(val);
});
