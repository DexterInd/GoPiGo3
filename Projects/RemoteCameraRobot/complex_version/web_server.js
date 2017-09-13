// required packages
var express = require("express");
var net = require("net");

function getDateTime() {

    var date = new Date();
    var hour = date.getHours();
    hour = (hour < 10 ? "0" : "") + hour;
    var min  = date.getMinutes();
    min = (min < 10 ? "0" : "") + min;
    var sec  = date.getSeconds();
    sec = (sec < 10 ? "0" : "") + sec;
    var year = date.getFullYear();
    var month = date.getMonth() + 1;
    month = (month < 10 ? "0" : "") + month;
    var day  = date.getDate();
    day = (day < 10 ? "0" : "") + day;
    return year + ":" + month + ":" + day + ":" + hour + ":" + min + ":" + sec + " - ";

}

/********************************************/
/*  TCP client that connects to the robot   */
/*  server - used for actuating the GoPiGo3 */
/********************************************/

// creating a new socket

var client = new net.Socket()
var ADDR = "localhost"
var PORT = 5002

// connects to the robot TCP server
client.connect(PORT, ADDR, function() {
  console.log(getDateTime() + "connected to robot server at " + ADDR + ":" + PORT)
  client.write("stop")
  console.log(getDateTime() + "sent [stop] command")
})

// event for closing the connection to the TCP server
client.on("end", function() {
  console.log(getDateTime() + "disconnected from robot server")
  // exit if the robot is offline - makes sense
  process.exit(0)
})

// event for handling connection errors
client.on("error", function() {
  console.log(getDateTime() + "cannot connect to the robot server")
  // since the robot server is not reachable, we just exit the app
  process.exit(1)
})


/**********************************************/
/*  HTTP Server - dependent on the TCP Server */
/*  offers an UI for controlling the GoPiGo3  */
/**********************************************/

// creats a new HTTP server
var app = express();

// serves main page
app.get("/", function(req, res) {
  console.log(getDateTime() + "/index.html file requested")
  res.sendFile(__dirname + "/index.htm", fn = function(err) {
    if(err) {
      console.error(getDateTime() + "/index.html file not found");
      res.status(404).send();
    }
    else {
      res.status(200).send();
    }
  });
});

// serves all the commands for actuating the GoPiGo3
app.get("/command", function(req, res) {
  var gopigo3_command = req.query.gopigo3
  if(typeof(gopigo3_command) == "undefined") {
    console.log(getDateTime() + "received invalid command for GoPiGo3")
    res.status(400).send()
  }
  else {
    console.log(getDateTime() + "received [" + gopigo3_command + "] command for GoPiGo3")
    //client.write(gopigo3_command)
    res.status(200).send()
  }
})

// serves all the static files
app.get(/^(.+)$/, function(req, res) {
   console.log(getDateTime() + "static file request : " + req.params);
   res.sendFile( __dirname + req.params[0], fn = function(err) {
     if(err) {
       console.error(getDateTime() + "static file not found");
       res.status(404).send();
     } else {
       res.status(200).send();
     }
   });
});

// starts listening for http clients
var port = process.env.PORT || 5005;
app.listen(port, function() {
 console.log(getDateTime() + "listening on " + port);
});
