// Chuyển đổi chuỗi JSON thành đối tượng JavaScript
// var jsonData = {{ json_data | tojson | safe }};
// var jsonData = {{ json_data | safe }};
        
// Hiển thị thông tin từ đối tượng JSON
// console.log(jsonData.message);
// console.log(jsonData.value);

function updateClock() {
    const now = new Date();

    const hours = now.getHours();
    const minutes = now.getMinutes();
    const seconds = now.getSeconds();

    const formattedTime = `${padZero(hours)} : ${padZero(minutes)} : ${padZero(seconds)}`;

    document.querySelector('.dashboard-clock').innerText = formattedTime;
}

function padZero(num) {
    return num < 10 ? `0${num}` : num;
}

const eventSource = new EventSource('/update');

        eventSource.addEventListener('message', (event) => {
            const formattedTime = event.data;
            document.querySelector('.dashboard-clock').innerText = formattedTime;
        });

// Update the clock every second
setInterval(updateClock, 1000);

// Initial update
updateClock();



async function updateStatus(){
    const healthUrls = [
        "https://httpstat.us/500",
        "https://httpstat.us/200",
        "https://httpstat.us/500",
    ];
    const servers =
       document.querySelectorAll(".server");
    for (const server of Array.from(servers)) {
        const url = healthUrls[
            Math.floor(Math.random() * healthUrls.length)
        ];
        const { status } = await fetch(url);
        if (status == 200) {
            server.classList.remove('has-failed');
            server
               .querySelector('.signal')
               .innerText = 'ONLINE';
        } else {
            server.classList.add('has-failed');
            server
               .querySelector('.signal')
               .innerText = 'OFFLINE'
        }
    }
    setTimeout (
        async () => {
            await updateStatus();
        },
        5000,
    );

}
setInterval (
    updateTime,
    900,
);
updateStatus();





// Vue.component("dashboard-header", {
//     props: ["title"],
//     template: `
//     <header class="dashboard-header">
//         <h1 class="dashboard-title">{{title}}</h1>
//         <slot></slot>
//     </header>
//     `
// });

// Vue.component("server-list", {
//     template: '<div class="server-list"><slot></slot></div>'
// });

// Vue.component("server", {
//     props: ["type"],
//     template: `
//     <div class="server">
//         <div class="server-icon fa" 
//             :class="'fa-' + (type === 'database' ? 'tasks' : 'globe')">
//         </div>
//         <ul class="server-details">
//             <li>Hostname:<slot name="name"></slot></li>                         
//             <li>Status:<slot name="status"></slot></li>
//             <li>Address:<slot name="adr"></slot></li>
//         </ul>
//     </div>`
// });

// //Vue.use(Vuex);
// const dashboard = new Vue({
//     el: "dashboard",
//     data: () => {
//         return {
//             servers: store.state.servers
//         };
//     },
//     methods: {
//         updateServerStatus(server) {
//             store.dispatch("serverStatus", server);
//         }
//     },
//     mounted() {
//         setInterval(
//             () =>
//                 store.dispatch(
//                     "serverStatus",
//                     Math.floor(Math.random() * (this.servers.length - 0) + 0)
//                 ),
//             5000
//         );
//     }
// });
