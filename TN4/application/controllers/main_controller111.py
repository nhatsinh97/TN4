# application/controllers/main_controller.py
from flask import Blueprint,Response, render_template

main = Blueprint('main', __name__)

@main.route('/1')
def home():
    log_file_path = './database/log/log_cico_everyday.log'
    try:
        seo = {'title': 'Farm Bình || Quản lý công việc'}
        with open(log_file_path, 'r') as file:
            log_content = file.read()
    except FileNotFoundError:
        return Response("Không tìm thấy file log.", status=404)
    except Exception as e:
        return Response(f"Lỗi: {e}", status=500)
    return Response(log_content,mimetype='text/plain')
    return send_file(log_file_path,as_attachment=False)
    # seo = {'title': 'Farm Bình || Quản lý công việc'}
    # return render_template('index.html', seo=seo)
    # return render_template('index.html')
