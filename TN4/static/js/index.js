// Hàm xử lý tải nội dung mới thông qua AJAX
function loadContent(url) {
    $.get(url, function(data) {
        $('.right_col').html(data); 
    }).fail(function() {
        alert('Không thể tải nội dung. Vui lòng thử lại sau.');
    });
}

// Hàm thiết lập CSRF token cho tất cả yêu cầu AJAX
function setupCsrfToken() {
    var csrf_token = "{{ csrf_token() }}";
    $.ajaxSetup({
        headers: {
            "X-CSRFToken": csrf_token
        }
    });
}

// Hàm xử lý sự kiện form submit để lọc dữ liệu
function setupFormSubmit() {
    $('form').on('submit', function(event){
        event.preventDefault(); // Ngăn hành vi mặc định của form

        // Lấy giá trị từ form
        var start_date = $('#start_date').val();
        var end_date = $('#end_date').val();

        // Gửi yêu cầu AJAX đến server
        $.ajax({
            url: '/access_history',
            method: 'POST',
            data: {
                start_date: start_date,
                end_date: end_date
            },
            success: function(response) {
                updateTable(response); // Cập nhật bảng
            },
            error: function() {
                alert('Lỗi xảy ra khi gửi yêu cầu.');
            }
        });
    });
}

// Hàm cập nhật bảng lịch sử truy cập
function updateTable(data) {
    $('tbody').empty(); // Xóa bảng cũ

    data.forEach(function(entry) {
        $('tbody').append(
            `<tr>
                <td>${formatTimestamp(entry.timestamp)}</td> <!-- Thêm hàm định dạng timestamp -->
                <td>${entry.username}</td>
                <td>${entry.ip}</td>
            </tr>`
        );
    });
}

// Hàm định dạng lại thời gian
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    
    // Lấy các thành phần của ngày và giờ
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0'); // Tháng trong JavaScript bắt đầu từ 0
    const year = date.getFullYear();

    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    
    // Trả về chuỗi theo định dạng dd/mm/yyyy hh:mm:ss
    return `${day}/${month}/${year} ${hours}:${minutes}:${seconds}`;
}

// Hàm vẽ biểu đồ sử dụng dữ liệu từ file JSON
let myChart;

function drawChartFromJSON(data) {
    const labels = [];
    const datasets = [];

    for (let idchip in data) {
        const deviceData = data[idchip];
        const timestamps = deviceData.map(entry => formatTimestamp(entry.timestamp)); // Định dạng lại timestamp
        const values = deviceData.map(entry => entry.request_count);

        if (labels.length === 0) {
            labels.push(...timestamps);
        }

        datasets.push({
            label: idchip,
            data: values,
            borderColor: getRandomColor(),
            fill: false
        });
    }

    if (myChart) {
        myChart.destroy(); // Xóa biểu đồ cũ trước khi tạo lại
    }

    const ctx = document.getElementById('myChart').getContext('2d');
    myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            elements: {
                line: {
                    tension: 0.4  // Làm mượt đường
                }
            },
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: '#fff',
                        font: {
                            size: 14
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'category',  // Đổi thành 'category' vì dùng chuỗi đã định dạng lại
                    title: {
                        display: true,
                        text: 'Thời gian',
                        color: '#fff',
                        font: {
                            size: 16
                        }
                    },
                    ticks: {
                        color: '#fff',
                        font: {
                            size: 12
                        }
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Số lượng Request',
                        color: '#fff',
                        font: {
                            size: 16
                        }
                    },
                    ticks: {
                        color: '#fff',
                        font: {
                            size: 12
                        }
                    }
                }
            }
        }
    });
}

// Hàm tạo màu ngẫu nhiên
function getRandomColor() {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

// Hàm xử lý load dữ liệu dựa theo mốc thời gian (Live, 1h, 6h, v.v.)
function loadData(timeFrame) {
    fetch(`/get-request-history?timeframe=${timeFrame}`)  // Gọi API với tham số thời gian
        .then(response => response.json())
        .then(data => {
            drawChartFromJSON(data);  // Vẽ lại biểu đồ với dữ liệu mới
        })
        .catch(error => console.error('Error loading request history:', error));
}

// Gọi hàm tải dữ liệu lần đầu (Live)
window.onload = function() {
    loadData('live');
};

$(document).ready(function() {
    $('#filterBtn').on('click', function() {
        // Gọi API để lấy dữ liệu lịch sử
        const device = $('#deviceFilter').val();
        const status = $('#statusFilter').val();

        $.ajax({
            url: '/api/get-history', // Đường dẫn API
            method: 'GET',
            data: {
                device: device,
                status: status
            },
            success: function(response) {
                // Xóa bảng cũ
                $('#historyTable').empty();

                // Đổ dữ liệu mới vào bảng
                response.data.forEach(function(item, index) {
                    const statusClass = item.status === 'COMPLETE' ? 'status-complete' : 'status-incomplete';
                    const row = `<tr>
                        <td>${index + 1}</td>
                        <td>${item.farm}</td>
                        <td>${item.location}</td>
                        <td>${item.device}</td>
                        <td>${item.date}</td>
                        <td>${item.start_time}</td>
                        <td>${item.end_time}</td>
                        <td>${item.minutes}</td>
                        <td>${item.total}</td>
                        <td><span class="badge ${statusClass}">${item.status}</span></td>
                    </tr>`;
                    $('#historyTable').append(row);
                });
            },
            error: function() {
                alert('Không thể tải dữ liệu. Vui lòng thử lại sau.');
            }
        });
    });
});
        // Hàm lấy tổng số request của tất cả thiết bị
        function getTotalRequests() {
            $.ajax({
                url: '/total_requests',
                method: 'GET',
                success: function (data) {
                    $('#totalRequests').text(data.total_requests);
                },
                error: function (err) {
                    console.error("Error fetching total requests: ", err);
                }
            });
        }

        // Hàm lấy số request của thiết bị cụ thể
        function getDeviceRequests() {
            const deviceId = $('#deviceId').val();
            if (!deviceId) {
                alert("Vui lòng nhập idchip của thiết bị");
                return;
            }

            $.ajax({
                url: '/device_requests',
                method: 'GET',
                data: {
                    idchip: deviceId
                },
                success: function (data) {
                    $('#deviceRequests').text(data.total_requests_today);
                },
                error: function (err) {
                    console.error("Error fetching device requests: ", err);
                }
            });
        }

        // Gọi hàm này mỗi 5 giây để cập nhật tổng số request
        setInterval(getTotalRequests, 10000);

        let doughnutChart; // Khai báo biến doughnutChart toàn cục để có thể sử dụng lại

        function createDoughnutChart(labels, dataValues) {
            const ctx = document.getElementById('canvasDoughnut').getContext('2d');
            doughnutChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: dataValues,
                        backgroundColor: ['#3498db', '#26b99a', '#9b59b6', '#e74c3c', '#f39c12'],
                        hoverBackgroundColor: ['#2980b9', '#1abc9c', '#8e44ad', '#c0392b', '#e67e22']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false // Giữ false để phù hợp với container
                }
            });
        }
        
    // Hàm lấy dữ liệu top 5 chipid từ server
    function getTopDevices() {
        $.ajax({
            url: '/top_devices', // Gửi yêu cầu GET đến endpoint /top_devices
            method: 'GET',
            success: function (data) {
                updateTopDevices(data); // Cập nhật giao diện với dữ liệu nhận được
            },
            error: function (err) {
                console.error("Error fetching top devices: ", err);
            }
        });
    }

    // Hàm cập nhật giao diện với thông tin top 5 chipid
    function updateTopDevices(data) {
        const topDevices = data.top_devices;
        const topDevicesContainer = document.getElementById('topDevicesContainer');
        topDevicesContainer.innerHTML = ''; // Xóa dữ liệu cũ

        // Tìm giá trị request cao nhất để tính tỷ lệ phần trăm chính xác
        const maxRequestCount = Math.max(...topDevices.map(device => device[1]));

        topDevices.forEach((device) => {
            const chipId = device[0];
            const requestCount = device[1];
            const percentage = ((requestCount / maxRequestCount) * 100).toFixed(2); // Tính phần trăm dựa trên maxRequestCount

            // Tạo HTML cho mỗi chipid và thanh tiến trình
            const deviceHtml = `
                <div class="progress-container">
                    <div class="chip-id">
                        <span>${chipId}</span>
                    </div>
                    <div class="progress-wrapper">
                        <div class="progress progress_sm">
                            <div class="progress-bar bg-green" role="progressbar" style="width: ${percentage}%;"></div>
                        </div>
                    </div>
                    <div class="request-count">
                        <span>${requestCount}</span>
                    </div>
                </div>
            `;

            // Thêm HTML vào container
            topDevicesContainer.innerHTML += deviceHtml;
        });
    }

    // Gọi hàm này mỗi 5 giây để cập nhật top 5 chipid
    setInterval(getTopDevices, 5000);
        
        
        
        
        
        