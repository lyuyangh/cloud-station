var browserSocket = new WebSocket(
    'ws://' + window.location.host +
    '/ws/flightmonitor/');
document.querySelector('#telemetry-log').value += ('Successfully connected to server.\n');

browserSocket.onmessage = function (e) {
    var data = JSON.parse(e.data);
    var message = data['message'];
    document.querySelector('#telemetry-log').value += (message + '\n');
    var temp = JSON.parse(data['message']);
    try{
        updateDroneLoactionGeoJson(temp["longitude"], temp["latitude"]);
    }
    catch(e) {}
    try{
        updateInfo(temp);
    }
    catch (e) {
        console.log("info pack wrong");
    }
};
function updateInfo(infopack) {
    try {
        updateLocations(infopack['altitude'], infopack['longitude'], infopack['latitude']);

    }
    catch (e) {
        console.log("update location!")
    }

    try{
        updateTel(infopack['yaw'], infopack['roll'], infopack['pitch'])
    }
    catch (e) {
        console.log("update tel!")
    }

  // $("#altitude").text(infopack['altitude']);
  // $("#groundspeed").text(infopack['groundspeed']);
  // $("#Roll").text(infopack['roll']);
  // $("#Yaw").text(infopack['yaw']);
  // $("#DistoDest").text(infopack['DistoDest']);
  // $("#Pitch").text(infopack['pitch']);
  // $("#Longitude").text(infopack['longitude']);
  // $("#Latitude").text(infopack['latitude']);

  // console.log("www");
}
function updateLocations(al, long, lat){
    $("#altitude").text(al);
    $("#longitude").text(long);
    $("#latitude").text(lat);
    // console.log(long);

}
function updateTel(yaw, roll, pit){
    $("#Yaw").text(yaw);
    $("#Roll").text(roll);
    $("#Pitch").text(pit);
}

browserSocket.onclose = function (e) {
    document.querySelector('#telemetry-log').value += ('Error: connection to server has been disconnected\n');
};


document.querySelector('#vehicleID').focus();
document.querySelector('#vehicleID').onkeyup = function (e) {
    if (e.keyCode === 13) {  // enter, return
        document.querySelector('#connectbtn').click();
    }
};

function connectVehicle() {
    var message = document.getElementById("vehicleID").value;
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function () {
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
            document.querySelector('#telemetry-log').value += (xmlHttp.responseText + '\n');
    };
    var url = '/flight_data_collect/connect/' + message + '/';
    xmlHttp.open("GET", url, true); // true for asynchronous
    xmlHttp.send(null);
}

function disconnectVehicle() {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function () {
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
            document.querySelector('#telemetry-log').value += (xmlHttp.responseText + '\n');
    };
    var url = '/flight_data_collect/disconnect/';
    xmlHttp.open("GET", url, true); // true for asynchronous 
    xmlHttp.send(null);
}