// static/chart_script.js
// ... (Nội dung giống như bên trên)
// static/chart_script.js
const config = {
    type: 'line',
    data: data,
    options: {
        scales: {
            x: {
                type: 'linear',
                position: 'bottom'
            },
            y: {
                min: 0
            }
        },
        elements: {
            point: {
                radius: 0, // Kích thước của điểm trên đường biểu đồ
            },
        },
        plugins: {
            legend: {
                display: false, // Ẩn chú thích
            },
        },
        responsive: true,
        maintainAspectRatio: false,
        layout: {
            padding: {
                top: 10,
            },
        },
        scales: {
            x: {
                grid: {
                    color: 'rgba(255, 255, 255, 0.1)', // Màu đường lưới theo chiều ngang
                },
                ticks: {
                    color: 'rgba(255, 255, 255, 0.7)', // Màu các dấu chia trục x
                },
            },
            y: {
                grid: {
                    color: 'rgba(255, 255, 255, 0.1)', // Màu đường lưới theo chiều dọc
                },
                ticks: {
                    color: 'rgba(255, 255, 255, 0.7)', // Màu các dấu chia trục y
                },
            },
        },
        elements: {
            line: {
                borderColor: 'rgb(75, 192, 192)', // Màu đường biểu đồ
                borderWidth: 2,
            },
        },
    },
};

// Hàm để lọc dữ liệu theo thời gian
function filterData(timeUnit) {
    // Ở đây, bạn có thể thực hiện logic để lọc dữ liệu theo giờ, ngày, tháng, năm
    // và cập nhật lại biểu đồ myChart
    // Dữ liệu mới sau khi lọc cần được cập nhật vào data.datasets[0].data
    // Sau đó, gọi lại myChart.update() để cập nhật biểu đồ
    // Ví dụ: Nếu bạn muốn lọc theo giờ, thì chỉ hiển thị dữ liệu của giờ hiện tại

    // Dưới đây là ví dụ giả sử đã lọc dữ liệu theo giờ
    const newData = [15, 23, 30, 40, 35, 28, 20, 18, 25, 32, 38, 45, 12];
    myChart.data.datasets[0].data = newData;
    myChart.update();
}
