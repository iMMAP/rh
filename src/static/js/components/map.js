let userLoc = L.latLng(0, 0); // Default coordinates

navigator.geolocation.getCurrentPosition(function(position) {
    userLoc = L.latLng(position.coords.latitude, position.coords.longitude);
}, function() {
    console.log("Unable to get location");
});

// config map
let config = {
  minZoom: 3,
  maxZoom: 18,
  zoomControl: false, // zoom control off
};
// magnification with which the map will start
const zoom = 5;

const map = L.map('map',config).setView(userLoc, zoom,{
    animate:true,
    pan:{
        duration:1
    }
});

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

L.control.zoom({ position: "bottomleft" }).addTo(map);

// Fetch target locations from the Django route
const locationList = document.querySelector(".location-select");
targetLocationUrl = document.getElementById("map").getAttribute('data-locations-url')

fetch(targetLocationUrl)
    .then(response => response.json())
    .then(data => {
        data.locations.forEach(loc=> {
            location_name = loc.district_name
            lat = loc.district_lat
            long = loc.district_long

            if (lat && long) {
                const marker = L.marker([lat, long])
                    .addTo(map)
                    .bindPopup(
                        L.popup({
                            maxWidth: 250,
                            minWidth: 100,
                            autoClose: false,
                            closeOnClick: false,
                            // className: `${tl.state}-marker`,
                        })
                    )

                    let popupContent = `
                        <ul> 
                            <strong>District: ${location_name} (${loc.district_code})</strong>
                            ${loc.target_locations.map(tl => (
                                `<li>Targeted in project <a href="/projects/${tl.project_id}"> ${tl.project_code}</a>${tl.facility_name ? ',Facility '+tl.facility_name : '' } in this <a href="target-locations/${tl.id}/update">Target Location</a></li>`
                            )).join('')}
                        </ul>
                    `

                    marker.setPopupContent(popupContent)
            }

            const template = `
                <li class="location-item font-medium cursor-pointer bg-gray-d1 px-2 py-1 rounded-full" data-tl-id="${loc.id}" data-lat="${lat}" data-long="${long}">
                    <span class="name">${location_name}</span>
                </li>
            `;

            return locationList.insertAdjacentHTML("beforeend", template);
        });
        
        // Adjust map view to fit all markers
        if (data.locations.length > 0) {
            const bounds = L.latLngBounds(data.locations.map(loc => [loc.district_lat, loc.district_long]));
            map.fitBounds(bounds);
        }
    }).then(()=>{
        clickOnItem();
    })
    .catch(error => console.error('Error fetching target locations:', error));



function clickOnItem() {
  const locationItems = document.querySelectorAll(".location-item");
  locationItems.forEach((item) => {
    item.addEventListener("click", (e) => {
        fk = e.target.closest(".location-item")
        const id = fk.dataset.tlId;
        const lat = fk.dataset.lat;
        const long = fk.dataset.long;

        loc = [lat,long]

         map.flyTo(loc, 10, {
            animate: true,
            duration: 1, // sec
        });

    });
  });
}

// obtaining coordinates after clicking on the map
map.on("click", function (e) {
  const markerPlace = document.querySelector(".marker-position");
  markerPlace.textContent = e.latlng;
});