from flask import Flask, render_template, redirect, url_for, request
import calendar
from datetime import datetime

app = Flask(__name__)

# Populate some data
record = {
     'id' : 1,
     'name' : 'Michael',
     'mod': 'SC1003',
     'remarks': '',
     'video_link': 'https://www.youtube.com/watch?v=xvFZjo5PgG0&ab_channel=Duran'
}

attendance_data = [record]



@app.route('/')
def index():
    return redirect(url_for('upload'))
    # return render_template('base.html', navbar_links=navbar_links)

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

# @app.route('/event/<date>')
# def event_page(date):
#     # Here we just pass the date to show it, you can replace this
#     # with logic to fetch real event details from a database
#     return render_template('event.html', date=date)

@app.route("/upload", methods=['GET', 'POST'])
def upload():
    date = datetime.now
    title =  request.form.get("title")
    description = request.form.get("description")
    video = request.files.get("video")
    # print(title, description)
    return render_template("upload.html")

@app.route("/edit/<id>", methods=['GET', 'POST'])
def edit(id):
    return render_template("edit.html")

@app.route('/view/<date>', methods=['GET', 'POST'])
def view(date):
        return render_template("view.html", date=date, attendance_data = attendance_data)

@app.route("/delete/<date>/<id>", methods=['GET', 'POST'])
def delete(id, date):
    id = id
    date = date
    return redirect(url_for('view', date=date))

@app.route("/coffee")
def coffee():
    return render_template("coffee.html")

if __name__ == "__main__":
    app.run(port=8000, host='0.0.0.0', debug=True)
