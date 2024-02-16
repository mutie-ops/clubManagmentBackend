from flask import Flask, jsonify, json, request
from flask_cors import CORS, cross_origin
from database import session, ScheduleEvent
from datetime import datetime

import base64

app = Flask(__name__)

CORS(app)


@app.route('/home', methods=['POST', 'GET'])
@cross_origin()
def home():
    event_longitude = request.form['eventLongitude']
    event_latitude = request.form['eventLatitude']
    event_name = request.form['eventName']
    event_time = request.form['eventTime']
    event_date = request.form['eventDate']
    event_image = request.form['eventImage']
    event_description = request.form['eventDescription']

    event_location = f'longitude:{event_longitude} latitude:{event_latitude}'
    decode = base64.b64decode(event_image)
    # print('decoded image', decode)
    # this is for testing purposes
    filename = 'C:\\Users\\HP\\OneDrive\\Desktop\\cubManangegmentBackend\\output.jpg'
    with open(filename, 'wb') as f:
        f.write(decode)

    schedule_event = ScheduleEvent(event_name=event_name, event_location=event_location, event_time=event_time
                                   , event_date=event_date, event_image=event_image,
                                   event_description=event_description)

    try:
        session.add(schedule_event)
        session.commit()
        # Step 7: Close the session
        session.close()
        return jsonify({'message': 'Event Scheduled Successfully'})
    except Exception as e:
        print(e)
        return jsonify({'message': 'error Scheduling event'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
