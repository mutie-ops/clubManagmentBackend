import base64
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from database import session, ScheduleEvent, func, Users, EventStatus
from datetime import datetime, timedelta
import bcrypt
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import joinedload

application = app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'MonkeyDluffy282'

jwt = JWTManager(app)
CORS(app)


def create_admin():
    try:
        # Check if admin user already exists
        admin_user = session.query(Users).filter(Users.email == 'admin@gmail.com').first()

        if admin_user:
            print("Admin already exists")
        else:
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw('123'.encode('utf-8'), salt)
            admin = Users(fullNames='Admin', phoneNumber='000',
                          email='admin@gmail.com', password=hashed_password, is_admin=True)

            session.add(admin)
            session.commit()
            print("Admin created successfully")
    except Exception as e:
        session.rollback()
        print(f"Error creating admin: {e}")
    finally:
        session.close()


create_admin()


@app.route('/createUser', methods=['POST'])
@cross_origin()
def create_user():
    try:
        data = request.form.to_dict()
        request_fields = ['fullNames', 'phoneNumber', 'email', 'password']
        if not all(field in data for field in request_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), salt)
        users = Users(fullNames=data['fullNames'], phoneNumber=data['phoneNumber'],
                      email=data['email'], password=hashed_password)

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
            return jsonify({'message': 'User Created Successfully', 'status': True}), 200

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
        if not bcrypt.checkpw(data['password'].encode('utf-8'), user.password):
            return jsonify({'message': 'Invalid Password'}), 401

        #  this will change and I WILL QUERY THE ENTIRE USER AND RELATIONSHIPS
        # user_data = {'userName': user.fullNames, 'phoneNumber': user.phoneNumber, 'uuid': user.id}
        user_data = {'userName': user.fullNames, 'phoneNumber': user.phoneNumber, 'isAdmin': user.is_admin}

        # At this point, the user exists and the password is correct
        access_token = create_access_token(identity=user.id, expires_delta=timedelta(days=7))
        return jsonify({'message': 'Successful login', 'accessToken': access_token, 'data': user_data, 'status': True})


    except Exception as e:
        print(e)
        return jsonify({'message': str(e)}), 500


@app.route('/postEvent', methods=['POST'])
@jwt_required()
@cross_origin()
def create_event():
    try:
        user_id = get_jwt_identity()

        print('user id from header', user_id)
        data = request.form.to_dict()  # Convert form data to dictionary
        # Validate input data
        required_fields = ['eventName', 'venueName', 'eventLatitude', 'eventLongitude', 'eventTime', 'eventDate',
                           'eventDescription', 'eventImage']

        # print(data)
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
                                       eventDescription=data['eventDescription'], eventImage=data['eventImage'],
                                       user_id=int(user_id))
        session.add(schedule_event)
        session.commit()
        session.close()
        return jsonify({'message': 'Event Scheduled Successfully'}), 200
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500


@app.route('/getEventMonth', methods=['GET'])
def get_event_current_month():
    try:
        current_month = datetime.now().month
        str_month = f"{current_month:02d}"

        events = session.query(ScheduleEvent).outerjoin(EventStatus).options(
            joinedload(ScheduleEvent.event_statuses)).filter(
            func.strftime('%m', ScheduleEvent.eventDate) == str_month
        ).all()

        current_month_data = []
        for event in events:
            event_date = event.eventDate
            formatted_date = event_date.strftime("%d-%B-%Y")
            # Adjusted to a more standard format, change as needed
            # Collecting EventStatus data for each event

            event_status_data = None
            if event.event_statuses:
                status = event.event_statuses[0]  # Assuming there's only one event status per event
                event_status_data = {
                    'booked': status.booked,
                    'checkedIn': status.checkedIn,
                    'event_id': status.event_id
                }

            extract_data = {
                'eventName': event.eventName,
                'venueName': event.venueName,
                'eventLatitude': event.eventLatitude,
                'eventLongitude': event.eventLongitude,
                'eventTime': event.eventTime,
                'eventDate': formatted_date,
                'eventDescription': event.eventDescription,
                'eventImage': event.eventImage,
                'eventStatus': event_status_data  # Include EventStatus data here
            }
            current_month_data.append(extract_data)

        print('dictionary of current month', current_month_data)

        if len(current_month_data) == 0:
            return jsonify({"message": 'No events listed for the current month', 'data': current_month_data}), 200
        else:
            return jsonify({'message': 'Successful retrieval', 'data': current_month_data, 'status': True})
    except Exception as e:
        print(str(e))
        return jsonify({'message': 'An error occurred, no events are listed', 'data': str(e), 'status': False}), 401


@app.route('/updateProfile', methods=['POST'])
def profile():
    return 'rewr'


@app.route('/booking', methods=['POST'])
@jwt_required()
@cross_origin()
def booking():
    user_id = get_jwt_identity()
    data = request.form.to_dict()
    print(data)

    event_id = data['event_id']
    booked = data['booking'].lower() == 'true'
    checkedIn = False

    try:
        book_event = session.query(EventStatus).filter_by(event_id=event_id, user_id=user_id).one()
        book_event.checkedIn = checkedIn
        book_event.booked = booked
    except NoResultFound:
        book_event = EventStatus(booked=booked, checkedIn=checkedIn, user_id=user_id, event_id=event_id)
        session.add(book_event)

    session.commit()
    specific_booking = session.query(EventStatus).filter_by(event_id=event_id, user_id=user_id).all()

    session.close()
    for booking in specific_booking:
        if booking.checkedIn:
            print('checked in', booking.checkedIn)
            return jsonify({'message': 'checking in successful', 'data': booking.checkedIn, 'status': True}), 200
        elif booking.booked:
            print('booked', booking.booked)
            return jsonify({'message': 'booking successful', 'data': booking.booked, 'status': True}), 200


@app.route('/', methods=['GET'])
def callBackUrl():
    return jsonify({'message': 'successful  deployment'})

# if __name__ == '__main__':
#     app.run('0.0.0.0', port=5000, debug=True)
