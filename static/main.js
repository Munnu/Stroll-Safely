var map;
var directionsDisplay;
var directionsService;

var START = {};
var END = {};

var WAYPOINTS;


var getUserData = function(results) {
    // retreive the assembled lat/lng from the flask JSON route
    START.lat = results.point_a.lat; // for beginning route
    START.lng = results.point_a.lng;

    END.lat = results.point_b.lat; // for end route
    END.lng = results.point_b.lng;

    // display the user data that was submitted and returned back from flask
    // $('#get-user-data').html(results.point_a.lat + " " + results.point_a.lng);
    $('#parse-user-data').html("start: " + START.lat + " " + START.lng +
                              " end: " + END.lat + " " + END.lng);

    // now that we have the start coords, load up calculateAndDisplayRoute
    calculateAndDisplayRoute();
};

function calculateAndDisplayRoute() {

      // try doing this: 40.673301, -73.780351
      // create two points: A and B
      var latLangStart = new google.maps.LatLng(START.lat, START.lng);
      var latLangEnd = new google.maps.LatLng(END.lat, END.lng);

      var selectedMode = "WALKING";
      var directionsData;

      // !!!!!!!!!! Having trouble right here, Broken at waypoints construction
      directionsService.route({
          origin: latLangStart,  // Point A
          destination: latLangEnd,  // Point B
          // Note that Javascript allows us to access the constant
          // using square brackets and a string value as its
          // "property."
          travelMode: google.maps.TravelMode[selectedMode], // walking only
          waypoints: [] // pass in waypoints that python gives me
          // the hard-coded line below works, but the one above doesn't do anything, why?
          // waypoints: [{'location': {'lat': 40.75756, 'lng': -73.968781}, 'stopover': false}] // pass in waypoints that python gives me
      }, function(response, status) {
        if (status == google.maps.DirectionsStatus.OK) {
            directionsDisplay.setDirections(response);
            // need to find a way to return to python this same exact response's 
            // route's array, something like: directions_data = response['routes']
            // so that I know the legs to my trip and can check which grids
            // does a leg pass through.
            // let's do the process of sending this data over to python, call it
            console.log("This is the callback response from google maps api");
            console.log("that gives us the legs/steps to the journey");
            console.log("response['routes']", response['routes']);
            sendDirectionsResult(response['routes']);
        } else {
            window.alert('Directions request failed due to ' + status);
        }
    });
}


// !!!!!!!!! Problem area !!!!!!!!!
var showOptimalRoute = function(response) {
    // this will ultimately be the bearer of waypoints.
    console.log("----------------------------------------");
    console.log("showOptimalRoute response: ", response);
    console.log("showOptimalRoute response['waypoints']: ", response['waypoints']);
    // send waypoint data over to the part of the google api that needs it
    console.log("typeof(response)", typeof(response));
    console.log("This is response", response); // currently returns undefined
    // WAYPOINTS = jQuery.makeArray(response);
    // WAYPOINTS = JSON.parse(response); // Yields an: Uncaught SyntaxError: 
    // Unexpected token u
    // console.log("This is waypoints", WAYPOINTS);
    // console.log("typeof(WAYPOINTS)", WAYPOINTS);
    console.log("----------------------------------------");
    return WAYPOINTS;
};

var sendDirectionsResult = function(returnedDirectionsData) {
    // this function gets the directionsResults' response (an object {})
    // which is returned by the callback function of directionsService. 
    // This will go to a python flask route because we need it in order 
    // to analyze the legs of the trip.

    // assemble a url (this will be our flask route), so exciting...
    // the data parameter is needed and the json stringify or else it would be
    // nearly impossible to extract the data when attempting in flask
    var url = '/directions-data.json?data=' + JSON.stringify(returnedDirectionsData[0]);

    // this next step is to pass the values into the flask json endpoint
    // not passing in the data parameter because that's coming in as an argument
    $.get(url, success=showOptimalRoute); // success function is needed
};
// !!!!!!!! end problem area !!!!!!!!

var startDirections =  function(event){
    /* gets the user's input and sends it over to the flask json endpoint */

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
    /* Initializes Google Maps API stuff */

    var geocoder = new google.maps.Geocoder();
    var address = "central park new york";
    var center_lat, center_lng = 0;

    geocoder.geocode( {'address': address}, function(results, status) {
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