from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    seo = {'title': 'Farm Bình Thuận || Quản lý công việc'}
    data = {}  # Pass any data needed for rendering
    template = 'index.html'
    return render_template(template, seo=seo, data=data)

if __name__ == '__main__':
    app.run(debug=True)
