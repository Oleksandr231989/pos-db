<!DOCTYPE html>
<html>
<head>
    <title>Leaflet Polygons with Names</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet.draw/1.0.4/leaflet.draw.css" />
    <style>
        #map { height: 100vh; }
    </style>
</head>
<body>
    <div id="map"></div>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet.draw/1.0.4/leaflet.draw.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@turf/turf@6.5.0/turf.min.js"></script>
    <script>
        // Initialize the map
        var map = L.map('map').setView([50.4501, 30.5234], 12); // Centered on Kyiv

        // Add a base layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);

        // Create a feature group to store drawn polygons
        var drawnItems = new L.FeatureGroup();
        map.addLayer(drawnItems);

        // Add drawing controls
        var drawControl = new L.Control.Draw({
            edit: { featureGroup: drawnItems },
            draw: { polygon: true, polyline: false, rectangle: false, circle: false, marker: false }
        });
        map.addControl(drawControl);

        // Handle polygon creation
        map.on('draw:created', function (e) {
            var layer = e.layer; // Get the created layer
            var polygonName = prompt("Enter a name for this polygon:"); // Ask for polygon name
            if (polygonName) {
                // Bind the name as a popup
                layer.bindPopup("Polygon Name: " + polygonName);

                // Optionally, store the name in the layer's properties for export
                layer.feature = { properties: { name: polygonName } };
            }

            // Add the polygon to the drawn items group
            drawnItems.addLayer(layer);
        });

        // Example: Click on any polygon to see its name
        drawnItems.on('click', function (e) {
            e.layer.openPopup(); // Show popup when clicked
        });
    </script>
</body>
</html>
