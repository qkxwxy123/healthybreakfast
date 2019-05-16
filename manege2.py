from flask import Flask

app = Flask(__name__)

@app.route('/' , methods=["GET"])
def hello():
    return '<h1>hello</h1>'

if __name__ == '__main__':
    app.run(port = 8001)