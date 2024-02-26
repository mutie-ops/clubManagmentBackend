from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from database import session, ScheduleEvent, func
from datetime import datetime

app = Flask(__name__)
CORS(app)


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

        schedule_event = ScheduleEvent(eventName=data['eventName'], venueName=data['venueName'],
                                       eventLatitude=data['eventLatitude'], eventLongitude=data['eventLongitude'],
                                       eventTime=data['eventTime'], eventDate=event_date,
                                       eventDescription=data['eventDescription'], eventImage=data['eventImage'])
        session.add(schedule_event)
        session.commit()
        session.close()
        return jsonify({'message': 'Event Scheduled Successfully'})
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
            extract_data = {
                'eventName': event.eventName,
                'venueName': event.venueName,
                'eventLatitude': event.eventLatitude,
                'eventLongitude': event.eventLongitude,
                'eventTime': event.eventTime,
                'eventDate': event.eventDate,
                'eventDescription': event.eventDescription,
                'eventImage': event.eventImage}
            current_month_data.append(extract_data)

        print('dictionary of current month', current_month_data)
        return jsonify({'message': 'successful retrival',
                        'data': current_month,
                        'status': True})
    except Exception as e:
        return jsonify({'message': 'error',
                        'data': str(e),
                        'status': False})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
