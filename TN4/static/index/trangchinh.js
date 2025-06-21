$(document).on('click', '.ajax-link', function(e) {
    e.preventDefault(); // Ngăn hành vi mặc định mở trang mới
    console.log('Click event triggered'); // Kiểm tra sự kiện click
    var url = $(this).attr('href'); // Lấy URL của liên kết
    console.log('URL:', url); // Kiểm tra URL có được lấy chính xác hay không
    
    // Gửi yêu cầu AJAX để tải nội dung mới
    $.get(url, function(data) {
        $('.main-container').html(data); // Cập nhật nội dung trong block .container .main-container
    }).fail(function() {
        alert('Không thể tải nội dung. Vui lòng thử lại sau.');
    });
});

function toggleSidebar() {
    document.body.classList.toggle('sidebar-collapsed');
}