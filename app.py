from flask import Flask, render_template, redirect, url_for, request
import requests as rq
import calendar
from datetime import datetime
import uuid
import json

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
LAMBDA_FUNCTION_URL ='https://kgwtully4gddfje4y7kxtlx5xy0mmbsf.lambda-url.ap-southeast-1.on.aws/'

# functions
def upload_video(filename, timestamp, title, description, video):
    print("filename: ", filename)
    payload = {'action': 'upload',
                'params': {
                    'object_name':filename,
                    }
                }

    try:
        # Getting the presigned URL from AWS S3
        lambda_request = rq.post(LAMBDA_FUNCTION_URL, json=payload, headers={'Content-Type': 'application/json'})
        
        response_url = lambda_request.json()

        url = response_url.get("url")
        # Send a PUT request with the raw binary data (important)
        http_response = rq.put(url,data=video.read(), headers={'Content-Type': 'video/mp4'})
        
        print("HTTP response status:", http_response.status_code)

        if http_response.status_code == 200:
            # If the upload succeeds, update the DynamoDB with an entry
            # Craft a different payload
            submission_id = uuid.uuid4().int & (1<<32)-1
            timestamp = datetime.now().replace(microsecond=0).isoformat()
            
            payload = {'action': 'write_to_db',
                'params': {
                    'user_id':1,
                    'submission_id': submission_id,
                    'object_name':filename,
                    'timestamp': timestamp,
                    'title':title,
                    'description': description
                    }
                }
            
            db_request = rq.post(LAMBDA_FUNCTION_URL, json=payload, headers={'Content-Type': 'application/json'})
            print("DynamoDB response status:", db_request.status_code)
            print("DynamoDB", db_request.text)


    except Exception as e:
        print(e)

def get_calendar_view():
    pass


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

@app.route("/upload", methods=['GET'])
def upload():
    return render_template("upload.html")

@app.route("/upload", methods=['POST'])
def upload_post():
    date = datetime.now
    title =  request.form.get("title")
    description = request.form.get("description")
    video = request.files.get("video")
    filename = video.filename if video else ""
    # print("filename: ", filename)
    # print(title, description)
    upload_video(filename, date, title, description, video)
    return render_template("calendar.html")

@app.route("/edit/<int:id>", methods=['GET', 'POST'])
def edit(id):
    # Find the record by the provided ID, but Im not sure if this generator thing will work
    video_record = next((record for record in attendance_data if record['id'] == id), None)
    
    if not video_record:
        return "Record not found", 404

    if request.method == 'POST':
        title = request.form.get("title")
        description = request.form.get("description")
        video = request.files.get("video")

        if video:
            filename = video.filename
            video_record['video_link'] = f"https://your-s3-bucket-url/{filename}" # Im not sure if this is how the linsk should be
            upload_video(filename, datetime.now(), title, description, video)

        video_record['name'] = title
        video_record['remarks'] = description

        return redirect(url_for('view', date=datetime.now().strftime('%Y-%m-%d')))

    return render_template("edit.html", video=video_record)

@app.route('/view/<date>', methods=['GET', 'POST'])
def view(date):
    try:
        # Send a payload to AWS Lambda to process DynamoDB queries
        payload = {
            'action': 'get_calendar',
            'params': {
                'date': date
            }
        }

        response = rq.post(
            LAMBDA_FUNCTION_URL, 
            json=payload, 
            headers={'Content-Type': 'application/json'}
        )

        # print(f"Lambda response status: {response.status_code}")
        # print(f"Lambda response text: {response.text}")

        if response.status_code == 200:
            calendar_data = response.json()
            return render_template("view.html", 
                                date=date, attendance_data=calendar_data)
        else:
            return render_template("view.html", 
                                date=date, 
                                attendance_data=[])
    except Exception as e:
        print(f"Error: {e}")
        return render_template("view.html", 
                            date=date, 
                            attendance_data=[])

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