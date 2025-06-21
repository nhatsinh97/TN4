// Check latest version
// https://firebase.google.com/support/release-notes/js 

import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-app.js";
import { getDatabase, ref, onValue } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-database.js";

// Your web app's Firebase configuration
// Thay đổi cấu hình này cho phù hợp với webapp của bạn
const firebaseConfig = {
  apiKey: "AIzaSyA60XyWnId7purPGY6fNAdA5z1ijoJ9yrk",
  authDomain: "esp32-5be65.firebaseapp.com",
  databaseURL: "https://esp32-5be65-default-rtdb.firebaseio.com",
  projectId: "esp32-5be65",
  storageBucket: "esp32-5be65.appspot.com",
  messagingSenderId: "775781221966",
  appId: "1:775781221966:web:5f1e34b8e80289c836e51f"
};
let polyline;
let currentMarker;
let latlngs = [];
// // Initialize Firebase
var map = L.map('map').setView([11.347438, 105.885121], 13); 
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 25,
  attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);
// Tạo một layer group để chứa tất cả các marker
let markerGroup = L.layerGroup().addTo(map);
const app = initializeApp(firebaseConfig);
// Initialize Realtime Database and get a reference to the service
const database = getDatabase(app);
// Read data form Realtime Database
const starCountRef = ref(database, 'location');
onValue(starCountRef, (snapshot) => {
  const data = snapshot.val();
  if (polyline) polyline.remove(map);
  if (currentMarker) currentMarker.remove(map);
  // Xóa tất cả các marker
  markerGroup.clearLayers();
  latlngs = [];
  console.log(data);
  if (data) {
    data.forEach((item, index) => {
      let out = convert_data(item);
      // console.table(out)
      latlngs.push([out.lat, out.lng]);
      L.circleMarker([out.lat, out.lng], { radius: 8, color: 'blue', fillOpacity: 1, fillColor: 'blue' }).bindPopup(
        `<b>Time:</b> ${out.time}<br>
                <b>Date:</b> ${out.date}<br>
                <b>Speed:</b> ${out.speed} km/h<br>
                <b>Lat:</b> ${out.lat}<br>
                <b>Long:</b> ${out.lng}`)
        .bindTooltip(`${index + 1}`, {
          permanent: true,
          direction: 'center',
          opacity: 1,
          className: "label_marker"
        })
        .addTo(markerGroup);
    });
    polyline = L.polyline(latlngs, { color: 'blue', dashArray: '8, 10' }).addTo(map);
    map.setView(latlngs[latlngs.length - 1]);
    currentMarker = L.marker(latlngs[latlngs.length - 1]).addTo(map);
  }
});
function convert_data(input) {
  let output = {};
  output.time = (input.time == "undefine") ? "undefine" :
    `${input.time[0]}${input.time[1]}:${input.time[2]}${input.time[3]}:${input.time[4]}${input.time[5]}${input.time.slice(6)} (UTC)`;
  output.date = (input.date == "undefine") ? "undefine" :
    `${input.date[0]}${input.date[1]}/${input.date[2]}${input.date[3]}/${input.date[4]}${input.date[5]}`;
  output.speed = input.speed;
  // lat
  if (input.lat != "undefine") {
    let lat_data = input.lat.split(','); // lat_data[0] => lat, lat_data[1] => direction
    output.lat = (Number(lat_data[0].slice(0,2)) + (Number(lat_data[0].slice(2,9))/60)).toFixed(6);
    if (lat_data[1] === 'S') output.lat = -output.lat;
  }
  // lng
  if (input.lng != "undefine") {
    let lng_data = input.lng.split(','); // lng_data[0] => lng, lng_data[1] => direction
    output.lng = (Number(lng_data[0].slice(0,3)) + (Number(lng_data[0].slice(3,10))/60)).toFixed(6);
    if (lng_data[1] === 'W') output.lng = -output.lng;
  }
  return output;
}