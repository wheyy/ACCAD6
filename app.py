from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def helloworld():
    return render_template("index.html")

@app.route("/buymerugs")
def buymerugs() :
    return render_template("templates/rugs.html")

if __name__ == "__main__":
    app.run(port=8000, host='0.0.0.0', debug=True)