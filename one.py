from flask import Flask
from flask import request
from flask import make_response
from flask import redirect
from flask import abort
from flask import jsonify



app = Flask(__name__)


@app.route('/')
def index():
    user_agent = request.headers.get('User-Agent')
    return '<p>Your browser is %s</p>' % user_agent

def load_user(id):
    return None

@app.route('/user/<id>')
def get_user(id):
    user = load_user(id)
    if not user:
        abort(404)
    return "<h1>Hello, %s</h1>" % user.name

@app.route('/cookie')
def cookie():
    response = make_response("<h1>This document carries a cookie!</h1>")
    response.set_cookie("answer","42")
    return response

@app.route('/redirect')
def redirecttopage():
    return redirect("http://www.google.com")

@app.route('/responsecode/400')
def response_400():
    return "<h1>Bad Request</h1>", 400

@app.route('/user/<name>')
def user(name):
    return '<h1>Hello, %s!</h1>' % name



@app.route("/get_my_ip", methods=["GET"])
def get_my_ip():
    return '<h1>I am my address</h1>'
    #return jsonify({'ip': request.remote_addr}), 200


if __name__ == '__main__':
    app.run(debug=True)