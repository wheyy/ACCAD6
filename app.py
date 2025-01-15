<<<<<<< HEAD
from flask import Flask, render_template, redirect, url_for
import calendar
from datetime import datetime
=======
from flask import Flask, render_template, request
>>>>>>> main

app = Flask(__name__)

@app.route('/')
def index():
    return redirect(url_for('calendar_view'))

@app.route('/calendar')
def calendar_view():
    # Get the current month and year
    today = datetime.today()
    year = today.year
    month = today.month

    # Get the calendar for the current month
    cal = calendar.monthcalendar(year, month)

    # Pass the calendar and current month/year to the template
    return render_template('calendar.html', cal=cal, year=year, month=month)

@app.route('/event/<date>')
def event_page(date):
    # Here we just pass the date to show it, you can replace this
    # with logic to fetch real event details from a database
    return render_template('event.html', date=date)

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
<<<<<<< HEAD
    app.run(port=8000, host='0.0.0.0', debug=True)
=======
    app.run(port=8080, host='0.0.0.0', debug=True)
>>>>>>> main
