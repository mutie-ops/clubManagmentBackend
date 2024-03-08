import base64
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from database import session, ScheduleEvent, func, Users
from datetime import datetime

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'MonkeyDluffy282'

jwt = JWTManager(app)
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

        phone_query = session.query(Users).filter(Users.phoneNumber == data['phoneNumber']).all()
        email_query = session.query(Users).filter(Users.email == data['email']).all()

        if phone_query:
            return jsonify({'message': 'Phone Number already exists'}), 401
        elif email_query:
            return jsonify({'message': 'Email already exists'}), 401

        else:
            session.add(users)
            session.commit()
            session.close()
            return jsonify({'message': 'User Created Successfully'}), 200

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500


@app.route('/login', methods=['POST'])
@cross_origin()
def login():
    try:
        data = request.form.to_dict()
        request_fields = ['userAccount', 'password']
        if not all(field in data for field in request_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        phone_query = session.query(Users).filter(Users.phoneNumber == data['userAccount']).first()
        email_query = session.query(Users).filter(Users.email == data['userAccount']).first()

        if not phone_query and not email_query:
            return jsonify({'message': 'Account does not exist'}), 401

        user = phone_query if phone_query else email_query

        if user.password != data['password']:
            return jsonify({'message': 'Invalid Password'}), 401

        # At this point, the user exists and the password is correct
        access_token = create_access_token(identity=data['userAccount'])
        return jsonify({'message': 'Successful login', 'data': access_token})




    except Exception as e:
        print(e)
        return jsonify({'message': str(e)}), 500


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
