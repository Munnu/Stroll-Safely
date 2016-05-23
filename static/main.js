var map;
var directionsDisplay;
var directionsService;

var START = {};
var END = {};


var getUserData = function(results) {
    // retreive the assembled lat/lng from the flask JSON route
    START.lat = results.point_a.lat; // for beginning route
    START.lng = results.point_a.lng;

    END.lat = results.point_b.lat; // for end route
    END.lng = results.point_b.lng;

    // console.log for debugging, keeping these in for now
    console.log("This is START ");
    console.log(START);
    console.log("This is inside of getUserData START" + START.lat + " " + START.lng);
    console.log("This is inside of getUserData END" + END.lat + " " + END.lng);

    // display the user data that was submitted and returned back from flask
    // $('#get-user-data').html(results.point_a.lat + " " + results.point_a.lng);
    $('#parse-user-data').html("start: " + START.lat + " " + START.lng +
                              " end: " + END.lat + " " + END.lng);

    // now that we have the start coords, load up calculateAndDisplayRoute
    calculateAndDisplayRoute();
};

var showOptimalRoute = function(response) {
    console.log("showOptimalRoute response: ", response);
    //debugger;
};

var sendDirectionsResult = function(returnedDirectionsData) {
    // this function gets the directionsResults' response (an object {})
    // which is returned by the callback function of directionsService. 
    // This will go to a python flask route because we need it in order 
    // to analyze the legs of the trip.

    // assemble a url (this will be our flask route), so exciting...
    var url = '/directions-data.json';
    returnedDirectionsData = JSON.stringify(returnedDirectionsData);

    // this next step is to pass the values into the flask json endpoint
    $.post(url, returnedDirectionsData, showOptimalRoute); // success function is needed
};

var startDirections =  function(event){
    event.preventDefault(); // need this to prevent GET on form submit refresh
    alert("Inside of startDirections");

    // get the text field values inputted by the user
    start = document.getElementById('start-point').value;
    end = document.getElementById('end-point').value;
    
    // assemble a bunch of parameters for the json endpoint (in flask)
    var url = '/start-end.json?start=' + start + "&end=" + end;
    $.get(url, getUserData); // pass the values into the flask json endpoint

 };

// -- Needed for the onSubmit behavior
$('#route-me').submit(startDirections);
// ------------------------------------

function initMap() {

    var geocoder = new google.maps.Geocoder();
    var address = "central park new york";
    var center_lat, center_lng = 0;

    geocoder.geocode( {'address': address}, function(results, status) {
        //console.log(results);
        if (status == google.maps.GeocoderStatus.OK) {
              center_lat = results[0].geometry.location.lat();
              center_lng = results[0].geometry.location.lng();
          }

        // adding directions display and service variables
         directionsDisplay = new google.maps.DirectionsRenderer();
         directionsService = new google.maps.DirectionsService();

        // latitude and longitude stuff
        var centerPoint = new google.maps.LatLng(center_lat, center_lng);

        // ref to the div the map will be loaded into
        var mapDiv = document.getElementById('map');

        // create a new Google Maps object, 
        // takes in ref to the div the map will be loaded into
        // and options for the map
        map = new google.maps.Map(mapDiv, {
            center: centerPoint,
            zoom: 12
        });


        // results is whatever is returned from the GET request, 
        // JSON in this case
        $.get('/crimes.json', function(results) {
              var heatmapData = [];
              var crimes_found = results.crimes; // a list of dictionaries

              // Loop through all of the crimes in the json
              for (var i = 0; i < crimes_found.length; i++) {
                  // set a new latLng based on json items
                  var latLng = new google.maps.LatLng(
                                        crimes_found[i].latitude,
                                        crimes_found[i].longitude);

                  heatmapData.push(latLng);
              } // end for
              var heatmap = new google.maps.visualization.HeatmapLayer({
                data: heatmapData,
                dissipating: true,
                radius: 20,
                map: map
            }); //end heatmap declaration
        }); // end $.get

        // display the map
        directionsDisplay.setMap(map);
    }); // end geocoder
}

// display the map
google.maps.event.addDomListener(window, 'load', initMap);


function calculateAndDisplayRoute() {

      // try doing this: 40.673301, -73.780351
      // create two points: A and B
      console.log("Start Point", START);
      var latLangStart = new google.maps.LatLng(START.lat, START.lng);
      var latLangEnd = new google.maps.LatLng(END.lat, END.lng);

      var selectedMode = "WALKING";
      var directionsData;

      directionsService.route({
          origin: latLangStart,  // Point A
          destination: latLangEnd,  // Point B
          // Note that Javascript allows us to access the constant
          // using square brackets and a string value as its
          // "property."
          travelMode: google.maps.TravelMode[selectedMode], // walking only
          waypoints: [] // this is for later, I will need to pass in waypoints that python gives me
      }, function(response, status) {
        if (status == google.maps.DirectionsStatus.OK) {
            directionsDisplay.setDirections(response);
            // need to find a way to return to python this same exact response's 
            // route's array, something like: directions_data = response['routes']
            // so that I know the legs to my trip and can check which grids
            // does a leg pass through.
            // let's do the process of sending this data over to python, call it
            sendDirectionsResult(response['routes'][0]);
        } else {
            window.alert('Directions request failed due to ' + status);
        }
    });

      console.log("This is directionsData (directionsService and directionsResult)",
                  directionsData);
}
