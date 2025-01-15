from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def helloworld():
    return render_template("index.html")

@app.route("/upload", methods=['GET', 'POST'])
def upload() :
    title =  request.form.get("title")
    description = request.form.get("description")
    video = request.files.get("video")
    # print(title, description)
    return render_template("upload.html")

@app.route("/coffee")
def coffee():
    return render_template("coffee.html")

if __name__ == "__main__":
    app.run(port=8080, host='0.0.0.0', debug=True)