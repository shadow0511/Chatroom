from flask import (
    Flask, render_template, url_for,
    request, redirect, session
)
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import timedelta, datetime

app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY='admin0513'
)
app.permanent_session_lifetime = timedelta(minutes=60)

socketio = SocketIO(app)

# INDEX
@app.route('/', methods = ['GET'])
def index():
    if 'user' not in session:
        return redirect(url_for('user'))
    
    return render_template('index.html', time=(int(session['time'])*60*1000))

@app.route('/user', methods = ['GET', 'POST'])
def user():
    if 'user' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # set session data
        session.permanent = True
        set_session_time(int(request.form['time']))
        session['user'] = request.form['user']
        session['room'] = request.form['room']
        session['time'] = request.form['time']

        return redirect(url_for('index'))
    
    return """
        <!DOCTYPE html>
        <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, height=device-height, initial-scale=1.0, user-scalable=no">
                <style>
                    html { width: 100%; height:100%; }
                    body { width: 100%; height:100%; display: flex; justify-content: center; align-items: center; }
                    form { display:block; }
                    form > * { display:block; margin-bottom:8px; font-size:16px; font-family: system-ui; }
                    form > input { padding: 5px 10px; }
                    form > button { font-weight: 600; padding: 5px 10px; }
                </style>
            </head>
            <body>
                <form method="post">
                    <label for="user">enter your name:</label>
                    <input type="text" id="user" name="user" required />
                    <label for="room">which room?</label>
                    <input type="text" id="room" name="room" required />
                    <label for="time">enter the time</label>
                    <input type="number" min="1" max="20" id="time" name="time" required />
                    <button type="submit">Submit</button>
                </form>
            </body>
        </html>
    """

@socketio.on('message')
def handle_message(data):
    msg = str(datetime.now().strftime('%m-%d / %H:%M')) + ' - ' + str(data['who'] + " : " + data['data']) + '\n'
    emit('update', msg, broadcast=True, to=data['roomid'])

@socketio.on('join')
def join_group(data):
    username = data['who']
    room = data['roomid']
    join_room(room)

@socketio.on('leave')
def leave_group(data):
    username = data['who']
    room = data['roomid']
    leave_room(room)

def set_session_time(time):
    app.permanent_session_lifetime = timedelta(minutes=time)

if __name__ == '__main__':
    socketio.run(app, port=4440)
