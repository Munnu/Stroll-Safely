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
    // $('#parse-user-data').html("start: " + START.lat + " " + START.lng +
    //                           " end: " + END.lat + " " + END.lng);

    // now that we have the start coords, load up calculateAndDisplayOriginalRoute
    calculateAndDisplayOriginalRoute();
};

function crimesAroundArea(results) {
      console.log("This is crimesAroundArea results", results);

      // results is whatever is returned from the GET request, 
      // JSON in this case
      var heatmapData = [];
      var crimeData = [];
      var crimes_found = results.crimes; // a list of dictionaries

      // Loop through all of the crimes in the json
      for (var i = 0; i < crimes_found.length; i++) {
          // set a new latLng based on json items
          var latLng = new google.maps.LatLng(
                                crimes_found[i].latitude,
                                crimes_found[i].longitude);
          var totalCrimes = crimes_found[i].total_crimes;

          crimeData.push(totalCrimes);
          heatmapData.push(latLng);
      } // end for
      var heatmap = new google.maps.visualization.HeatmapLayer({
        data: heatmapData,
        dissipating: true,
        radius: 5,
        weight: 10,
        map: map
    }); //end heatmap declaration
}

function calculateAndDisplayOriginalRoute() {

      // try doing this: 40.673301, -73.780351
      // create two points: A and B
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
          waypoints: [] // empty waypoints for now: non-modified route
      }, function(response, status) {
        if (status == google.maps.DirectionsStatus.OK) {
            directionsDisplay.setOptions({
              polylineOptions: {
                strokeColor: "red",
                strokeOpacity: 0.5,
                strokeWeight: 5
              }
            });
            directionsDisplay.setDirections(response);
            // sends python this same exact response's so that I know the legs 
            // to my trip and can check which grids does a leg pass through.
            // let's do the process of sending this data over to python, call it

            // console.log statements galore
            console.log("This is the callback response from google maps api");
            console.log("that gives us the legs/steps to the journey");
            console.log("response['routes']", response['routes']);

            // python stuff here
            window.setTimeout(
              function() {
                sendDirectionsResult(response['routes']);
              }, 1000
            ); // create a delay here so we can see the before and after route
        } else {
            window.alert('Directions request failed due to ' + status);
        }
    });
}


var showOptimalRoute = function(response) {
    // this will ultimately be the bearer of waypoints.
    // send waypoint data over to the part of the google api that needs it

    console.log("----------------------------------------");
    console.log("showOptimalRoute response: ", response);
    console.log("showOptimalRoute response['waypoints']: ", response['waypoints']);
    console.log("typeof(response)", typeof(response));
    console.log("This is response", response);
    console.log("----------------------------------------");

    // we do this section again because this is the 'after' effect, the first
    // time got the unmodified route, this is now the modified via python

    selectedMode = 'WALKING';
    directionsService.route({
        origin: response['data']['start'],  // Point A
        destination: response['data']['end'],  // Point B
        travelMode: google.maps.TravelMode[selectedMode], // walking only
        waypoints: response['data']['waypoints']
    }, function(response, status) {
      if (status == google.maps.DirectionsStatus.OK) {
          directionsDisplay.setOptions({
              polylineOptions: {
                strokeColor: "#4D90FE",
                strokeOpacity: 0.8,
                strokeWeight: 5
              }
          });
          directionsDisplay.setDirections(response);
      } else {
          window.alert('Directions request failed due to ' + status);
      }
  });
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

    // for an added bonus, let's also get all the crimes in the area
    // assemble a bunch of parameters for the json endpoint (in flask)
    var crimesUrl = '/crimes.json?start_lat=' + START.lat + "&start_lng=" +
                    START.lng + "&end_lat=" + END.lat + "&end_lng=" + END.lng;

    $.get(crimesUrl, crimesAroundArea); // pass the values into the flask json endpoint
};

var startDirections =  function(event){
    /* gets the user's input and sends it over to the flask json endpoint */

    event.preventDefault(); // need this to prevent GET on form submit refresh
    //alert("Inside of startDirections");

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
    var start = document.getElementById('start-point');
    var end = document.getElementById('end-point');
    var route_button = document.getElementById('route-button');

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

        // push the input boxes to the map screen
        map.controls[google.maps.ControlPosition.TOP_LEFT].push(start);
        map.controls[google.maps.ControlPosition.TOP_LEFT].push(end);
        // map.controls[google.maps.ControlPosition.TOP_LEFT].push(route_button);

        // autocomplete stuff, this line generates the autocompletion
        var start_autocomplete = new google.maps.places.Autocomplete(start);
        start_autocomplete.bindTo('bounds', map);

        var end_autocomplete = new google.maps.places.Autocomplete(end);
        end_autocomplete.bindTo('bounds', map);

        // // results is whatever is returned from the GET request, 
        // // JSON in this case
        // $.get('/crimes.json', function(results) {
        //       var heatmapData = [];
        //       var crimes_found = results.crimes; // a list of dictionaries

        //       // Loop through all of the crimes in the json
        //       for (var i = 0; i < crimes_found.length; i++) {
        //           // set a new latLng based on json items
        //           var latLng = new google.maps.LatLng(
        //                                 crimes_found[i].latitude,
        //                                 crimes_found[i].longitude);

        //           heatmapData.push(latLng);
        //       } // end for
        //       var heatmap = new google.maps.visualization.HeatmapLayer({
        //         data: heatmapData,
        //         dissipating: true,
        //         radius: 5,
        //         weight: 0.5,
        //         map: map
        //     }); //end heatmap declaration
        // }); // end $.get

        // display the map
        directionsDisplay.setMap(map);
    }); // end geocoder
}

// display the map
google.maps.event.addDomListener(window, 'load', initMap);