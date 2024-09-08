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
const zoom = 6;

const map = L.map('map',config).setView(userLoc, zoom,{
    animate:true,
    pan:{
        duration:1
    }
});

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    // maxZoom: 19,
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

                const marker = L.marker([lat, long],{
                    icon: L.divIcon({
                        className: "leaflet-marker-icon",
                        html: `<span>${loc.location_count}</span>`,
                        popupAnchor: [10, -7],
                    }),
                })
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
                        <ul class="space-y-2"> 
                            <span class="border-b font-semibold border-gray-d1 mb-2">District: ${location_name} (${loc.district_code})</span>
                            ${loc.target_locations.map(tl => (
                                `<li class="text-xs ">Targeted in project <a href="/projects/${tl.project_id}"> ${tl.project_code}</a>${tl.facility_name ? ',Facility '+tl.facility_name : '' } in this <a href="target-locations/${tl.id}/update">Target Location</a></li>`
                            )).join('')}
                        </ul>
                    `
                    marker.setPopupContent(popupContent)

                    marker.on("click", () => {
                        marker._icon.classList.add("animation");
                    });

                    // remove class when popup is closed
                    marker.on("popupclose", () => {
                        marker._icon.classList.remove("animation");
                    });
            }

            const template = `
                <div class="location-item px-2 font-medium border border-gray-f5 py-2 cursor-pointer " data-tl-id="${loc.id}" data-lat="${lat}" data-long="${long}">
                    <span class="flex-wrap">${location_name} <em>(${loc.district_code})</em></span>
                    <span class="rounded-full bg-gray-f5 px-2 py-1">${loc.location_count}</span>
                </div>
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
  markerPlace.textContent = `Lat: ${e.latlng.lat} | Lng:${e.latlng.lng}`;
});


// --------------------------------------------------
// sidebar
const menuItems = document.querySelectorAll(".menu-item");
const sidebar = document.querySelector(".sidebar");
const buttonClose = document.querySelector(".close-button");
const visulaMapContainer = document.querySelector(".visual-map-section");


menuItems.forEach((item) => {
  item.addEventListener("click", (e) => {
    const target = e.target;

    if (
      target.classList.contains("active-item") ||
      !document.querySelector(".active-sidebar")
    ) {
      visulaMapContainer.classList.toggle("active-sidebar");
    }

    // show content
    showContent(target.dataset.item);
    // add active class to menu item
    addRemoveActiveItem(target, "active-item");
  });
});

// close sidebar when click on close button
buttonClose.addEventListener("click", () => {
  closeSidebar();
});

// remove active class from menu item and content
function addRemoveActiveItem(target, className) {
  const element = document.querySelector(`.${className}`);
  target.classList.add(className);
  if (!element) return;
  element.classList.remove(className);
}

// show specific content
function showContent(dataContent) {
  const idItem = document.querySelector(`#${dataContent}`);
  addRemoveActiveItem(idItem, "active-content");
}

// --------------------------------------------------
// close when click esc
document.addEventListener("keydown", function (event) {
  if (event.key === "Escape") {
    closeSidebar();
  }
});

// close sidebar when click outside
// document.addEventListener("click", (e) => {
//   if (!e.target.closest(".sidebar")) {
//     closeSidebar();
//   }
// });

// --------------------------------------------------
// close sidebar

function closeSidebar() {
  visulaMapContainer.classList.remove("active-sidebar");
  const element = document.querySelector(".active-item");
  const activeContent = document.querySelector(".active-content");
  if (!element) return;
  element.classList.remove("active-item");
  activeContent.classList.remove("active-content");
}
