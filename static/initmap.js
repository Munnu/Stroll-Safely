var map;
function initMap() {
    // adding directions display and service variables
    var directionsDisplay = new google.maps.DirectionsRenderer;
    var directionsService = new google.maps.DirectionsService;

    // latitude and longitude stuff
    var centerPoint = new google.maps.LatLng(44.540, -78.546);

    // ref to the div the map will be loaded into
    var mapDiv = document.getElementById('map');

    // create a new Google Maps object, 
    // takes in ref to the div the map will be loaded into
    // and options for the map
    var map = new google.maps.Map(mapDiv, {
      center: centerPoint,
      zoom: 8
    });

    // display the map
    directionsDisplay.setMap(map);

    calculateAndDisplayRoute(directionsService, directionsDisplay);
}


function calculateAndDisplayRoute(directionsService, directionsDisplay) {

    // create two points: A and B
    var latLang1 = new google.maps.LatLng(44.540, -78.546);
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
