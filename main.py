import base64

from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from database import session, ScheduleEvent, func, Users
from datetime import datetime

app = Flask(__name__)
CORS(app)


@app.route('/createUser', methods=['POST'])
@cross_origin()
def create_user():
    try:
        data = request.form.to_dict()
        request_fields = ['fullNames', 'phoneNumber', 'email', 'password']
        if not all(field in data for field in request_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        users = Users(fullNames=data['fullNames'], phoneNumber=data['phoneNumber'],
                      email=data['email'], password=data['password'])

        session.add(users)
        session.commit()
        session.close()
        return jsonify({'message': 'Event Scheduled Successfully'}), 200

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500


@app.route('/postEvent', methods=['POST'])
@cross_origin()
def create_event():
    try:
        data = request.form.to_dict()  # Convert form data to dictionary
        # Validate input data
        required_fields = ['eventName', 'venueName', 'eventLatitude', 'eventLongitude', 'eventTime', 'eventDate',
                           'eventDescription', 'eventImage']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        try:
            event_date = datetime.strptime(str(data['eventDate']), '%d/%m/%Y').date()
        except ValueError:
            print(ValueError)
            return jsonify({'message': 'Invalid date format for eventDate'}), 400

        # data_image = data['eventImage']

        # print(data_image)
        # decoded_bytes = base64.b64decode(data_image)
        # decoded_string = decoded_bytes.decode('utf-8')
        # print('decode to string', decoded_string)
        # with open('output.jpg', 'wb') as f:
        #     f.write(decoded_bytes)

        schedule_event = ScheduleEvent(eventName=data['eventName'], venueName=data['venueName'],
                                       eventLatitude=data['eventLatitude'], eventLongitude=data['eventLongitude'],
                                       eventTime=data['eventTime'], eventDate=event_date,
                                       eventDescription=data['eventDescription'], eventImage=data['eventImage'])
        session.add(schedule_event)
        session.commit()
        session.close()
        return jsonify({'message': 'Event Scheduled Successfully'}), 200
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500


@app.route('/getEventMonth', methods=['GET'])
def get_event_current_month():
    # get current month: convert to String append 0 if the length of days is less than 2
    try:
        current_month = datetime.now().month
        if len(str(current_month)) < 2:
            new_month = '0' + str(current_month)
            events = session.query(ScheduleEvent).filter(
                func.substr(ScheduleEvent.eventDate, 6, 2) == str(new_month)).all()
        else:
            events = session.query(ScheduleEvent).filter(
                func.substr(ScheduleEvent.eventDate, 6, 2) == str(current_month)).all()

        current_month_data = []
        for event in events:
            event_date = event.eventDate
            formatted_date = event_date.strftime("%d %B %Y")
            extract_data = {
                'eventName': event.eventName,
                'venueName': event.venueName,
                'eventLatitude': event.eventLatitude,
                'eventLongitude': event.eventLongitude,
                'eventTime': event.eventTime,
                'eventDate': formatted_date,
                'eventDescription': event.eventDescription,
                'eventImage': event.eventImage
            }
            current_month_data.append(extract_data)

        print('dictionary of current month', current_month_data)

        # DONT REMOVE THE CURRENT_MONTH_DATA HERE FUTURE MUTIE
        if len(current_month_data) == 0:
            return jsonify({"message": 'No events listed for current Month',
                            'data': current_month_data}), 200

        else:
            return jsonify({'message': 'successful retrival',
                            'data': current_month_data,
                            'status': True})
    except Exception as e:
        return jsonify({'message': 'error',
                        'data': str(e),
                        'status': False})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
