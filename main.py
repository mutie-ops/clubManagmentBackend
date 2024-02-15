from flask import Flask, jsonify, json, request
from flask_cors import CORS, cross_origin
from sqlalchemy import insert
from database import schedule_table, engine
from datetime import datetime

import base64

app = Flask(__name__)

CORS(app)


@app.route('/home', methods=['POST', 'GET'])
@cross_origin()
def home():
    event_location = None

    # Handling JSON data
    # data = request.get_json()
    # if data:
    #     event_location = data.get('eventLocation')

    event_name = request.form['eventName']
    event_time = request.form['eventTime']
    event_date = request.form['eventDate']
    event_image = request.form['eventImage']
    event_description = request.form['eventDescription']
    decode = base64.b64decode(event_image)
    # print('decoded image', decode)
    filename = 'C:\\Users\\HP\\OneDrive\\Desktop\\cubManangegmentBackend\\output.jpg'
    with open(filename, 'wb') as f:
        f.write(decode)

    # create date time objects
    # event_date_obj = datetime.strptime(event_date, '%d/%m/%Y')
    # event_time_obj = datetime.strptime(event_time, '%I:%M %p')
    #
    # formatted_date = event_date_obj.strftime('%d/%B/%Y')
    # formatted_time = event_time_obj.strftime('%I:%M %p')

    print(event_date)
    print(event_time)

    # Format the datetime objects as 'dd/mmmm/yyyy' and 'hh:mm AM/PM' respectively

    insert_schedule = schedule_table.insert().values(
        EventName=event_name,
        # EventLocation=event_location,
        # EventDate=formatted_date,
        # EventTime=formatted_time,
        EventDate=event_date,
        EventTime=event_time,
        EventImage=event_image,
        EventDescription=event_description

    )
    try:
        with engine.connect() as conn:
            conn.execute(insert_schedule)
            return jsonify({'message': 'Event Scheduled Successfully'})
    except Exception as e:
        print(e)
        return jsonify({'message': 'Event error Scheduling'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
