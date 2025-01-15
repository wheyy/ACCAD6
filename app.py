from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def helloworld():
    return render_template("index.html")

@app.route("/upload")
def upload() :
    return render_template("upload.html")

if __name__ == "__main__":
    app.run(port=8080, host='0.0.0.0', debug=True)