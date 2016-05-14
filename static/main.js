var map;
var directionsDisplay;
var directionsService;

var INFO = {};

var getUserData = function(results) {
    // display the user data that was submitted and returned back from flask
    console.log("This is inside of getUserData " + results.lat + " " + results.lng);
    $('#get-user-data').html(results.lat + " " + results.lng);
};

var startDirections =  function(event){
    event.preventDefault(); // need this to prevent GET on form submit refresh
    INFO.latitude = document.getElementById('start-latitude').value;
    INFO.longitude = document.getElementById('start-longitude').value;
    
    // assemble a bunch of parameters for the json endpoint (in flask)
    var url = '/start-end.json?lat=' + INFO.latitude + "&lng=" + INFO.longitude;
    $.get(url, getUserData); // pass the values into the flask json endpoint

    calculateAndDisplayRoute(directionsService, directionsDisplay);

 };

function initMap() {

    var geocoder = new google.maps.Geocoder();
    var address = "new york";
    var center_lat, center_lng = 0;

    geocoder.geocode( { 'address': address}, function(results, status) {
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
            zoom: 8
        });


        // results is whatever is returned from the GET request, 
        // JSON in this case
        $.get('/crimes.json', function(results) {
              var heatmapData = [];
              var crimes_found = results.crimes; // a list of dictionaries

              // console.log("This is crimes_found lat " + crimes_found[0].latitude);
              // console.log("This is crimes_found lng" + crimes_found[0].longitude);

              // Loop through all of the crimes in the json
              for (var i = 0; i < crimes_found.length; i++) {
                  // set a new latLng based on json items
                  var latLng = new google.maps.LatLng(
                                        crimes_found[i].latitude,
                                        crimes_found[i].longitude);

                  heatmapData.push(latLng);
                  // set a new marker and place onto map
                  // var marker = new google.maps.Marker({
                  //     position: latLng,
                  //     map: map
                  // });
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
      var latLang1 = new google.maps.LatLng(INFO.latitude, INFO.longitude);
      var latLang2 = new google.maps.LatLng(44.540, -79);

      var selectedMode = "WALKING";

      directionsService.route({
          origin: latLang1,  // Point A
          destination: latLang2,  // Point B
          // Note that Javascript allows us to access the constant
          // using square brackets and a string value as its
          // "property."
          travelMode: google.maps.TravelMode[selectedMode] // walking only
      }, function(response, status) {
        if (status == google.maps.DirectionsStatus.OK) {
            directionsDisplay.setDirections(response);
        } else {
            window.alert('Directions request failed due to ' + status);
        }
    });
}
