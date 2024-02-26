from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from database import session, ScheduleEvent,func
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


@app.route('/getEvent', methods=['GET'])
def get_event():
    # logic to retrieve events goes here
    pass


#  extract by sustring

events = session.query(ScheduleEvent).filter(func.substr(ScheduleEvent.eventDate, 6,2 )=='02').all()


print(events)
for event in events:
    # print('events', event.eventName)
    print(event.eventDate)
if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
