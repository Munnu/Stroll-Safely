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

var startDirections =  function(event){
    event.preventDefault(); // need this to prevent GET on form submit refresh

    // get the text field values inputted by the user
    start = document.getElementById('start-point').value;
    end = document.getElementById('end-point').value;
    
    // assemble a bunch of parameters for the json endpoint (in flask)
    var url = '/start-end.json?start=' + start + "&end=" + end;
    $.get(url, getUserData); // pass the values into the flask json endpoint

 };

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

        // original start(40.760385 -73.9766736) end(40.7539472 -73.9811953)
        // (40.760385, -73.9811953) (40.7539472, -73.9766736)
        // playing around with markers again to see if bound square works
        var marker = new google.maps.Marker({ // added 0.005 to lat, 0.02 lng
                          position: {lat: 40.765385, lng: -73.9966736},
                          map: map,
                          title: 'Top Left'
                        });

        var marker = new google.maps.Marker({ // added 0.005 to lat, 0.02 lng
                          position: {lat: 40.7489472, lng: -73.9611953},
                          map: map,
                          title: 'Bottom Right'
                        });

        // var marker = new google.maps.Marker({
        //                   position: {lat: 40.766385, lng: -73.9851953},
        //                   map: map,
        //                   title: 'Top Left prime'
        //                 });

        // var marker = new google.maps.Marker({
        //                   position: {lat: 40.7506472, lng: -73.9716736},
        //                   map: map,
        //                   title: 'Bottom Right prime'
        //                 });

        // {
        //   north: 40.7539472,
        //   south: 40.760385,
        //   east: -73.9766736,
        //   west: -73.9811953
        // }
        // northeast and southwest needed to generate rectangle
        var latlng_bounds = new google.maps.LatLngBounds(
                                 new google.maps.LatLng(40.765385, -73.9966736),
                                 new google.maps.LatLng(40.7489472, -73.9611953));

        var rectangle = new google.maps.Rectangle({
                              strokeColor: '#000000',
                              strokeOpacity: 0.8,
                              strokeWeight: 2,
                              fillColor: '#000000',
                              fillOpacity: 0.35,
                              map: map,
                              bounds: latlng_bounds
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
      console.log("Wut?");
      console.log(START);
      var latLangStart = new google.maps.LatLng(START.lat, START.lng);
      var latLangEnd = new google.maps.LatLng(END.lat, END.lng);

      var selectedMode = "WALKING";

      directionsService.route({
          origin: latLangStart,  // Point A
          destination: latLangEnd,  // Point B
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
