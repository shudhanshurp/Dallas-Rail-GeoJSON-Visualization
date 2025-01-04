var mymap = L.map("map").setView([32.7767, -96.797], 11);
L.tileLayer(
    "https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}",
    {
        attribution:
            'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
        maxZoom: 18,
        id: "mapbox/streets-v11",
        tileSize: 512,
        zoomOffset: -1,
        accessToken: MAPBOX_CONFIG.accessToken,
    }
).addTo(mymap);

const lines = ["Blue", "Green", "Orange", "Red"];
const colors = {
    Blue: "#3074F3",
    Green: "#3FBF3F",
    Orange: "#FF8C00",
    Red: "#FF0000",
};
const layerControl = L.control
    .layers(null, null, { collapsed: false })
    .addTo(mymap);
const lineLayers = {};
const lineVisibility = {
    Blue: true,
    Green: true,
    Orange: true,
    Red: true,
};

lines.forEach((line) => {
    fetch(`/static/data/${line.toLowerCase()}_line.json`)
        .then((response) => response.json())
        .then((data) => {
            const lineLayer = L.geoJSON(data, {
                style: {
                    color: colors[line],
                    weight: 5,
                    opacity: 0.7,
                },
                onEachFeature: onEachFeature,
            }).addTo(mymap);
            lineLayers[line] = lineLayer;
            layerControl.addOverlay(lineLayer, `${line} Line`);

            // Add event listeners for layer toggling
            mymap.on("overlayremove", function (e) {
                if (e.name === `${line} Line`) {
                    lineVisibility[line] = false;
                    if (line === "Blue") clearMarkers(mapMarkersBlue);
                    if (line === "Green") clearMarkers(mapMarkersGreen);
                    if (line === "Orange") clearMarkers(mapMarkersOrange);
                    if (line === "Red") clearMarkers(mapMarkersRed);
                }
            });

            mymap.on("overlayadd", function (e) {
                if (e.name === `${line} Line`) {
                    lineVisibility[line] = true;
                }
            });
        });
});

function onEachFeature(feature, layer) {
    layer.on({
        click: zoomToFeature,
    });
}

function highlightFeature(e) {
    var layer = e.target;
    layer.setStyle({
        weight: 7,
        color: "#666",
        dashArray: "",
        fillOpacity: 0.7,
    });
    if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
        layer.bringToFront();
    }
}

function resetHighlight(e) {
    var layer = e.target;
    var line = layer.feature.properties.line;
    layer.setStyle({
        color: colors[line],
        weight: 5,
    });
}

function zoomToFeature(e) {
    mymap.fitBounds(e.target.getBounds());
}

var mapMarkersBlue = [];
var mapMarkersGreen = [];
var mapMarkersOrange = [];
var mapMarkersRed = [];

var source = new EventSource("/topic/geodata_line");
source.addEventListener(
    "message",
    function (e) {
        console.log("Message received");
        var obj = JSON.parse(e.data);
        console.log(obj);

        if (obj.busline == "Blue Line" && lineVisibility.Blue) {
            clearMarkers(mapMarkersBlue);
            mapMarkersBlue.push(
                addMarker([obj.latitude, obj.longitude], mymap, "#3074F3")
            );
        }

        if (obj.busline == "Green Line" && lineVisibility.Green) {
            clearMarkers(mapMarkersGreen);
            mapMarkersGreen.push(
                addMarker([obj.latitude, obj.longitude], mymap, "#3FBF3F")
            );
        }

        if (obj.busline == "Orange Line" && lineVisibility.Orange) {
            clearMarkers(mapMarkersOrange);
            mapMarkersOrange.push(
                addMarker([obj.latitude, obj.longitude], mymap, "#FF8C00")
            );
        }

        if (obj.busline == "Red Line" && lineVisibility.Red) {
            clearMarkers(mapMarkersRed);
            mapMarkersRed.push(
                addMarker([obj.latitude, obj.longitude], mymap, "#FF0000")
            );
        }
    },
    false
);

function clearMarkers(markers) {
    for (var i = 0; i < markers.length; i++) {
        mymap.removeLayer(markers[i]);
    }
    markers.length = 0;
}

function addMarker(coords, map, color) {
    return L.circleMarker(coords, {
        radius: 8,
        fillColor: color,
        color: "#000",
        weight: 1,
        opacity: 1,
        fillOpacity: 0.8,
    }).addTo(map);
}
