from flask import Flask, jsonify, render_template, request, Response, send_from_directory, url_for
from easygopigo3 import EasyGoPiGo3

MAX_FORCE = 5.0
MIN_SPEED = 100
MAX_SPEED = 300
gopigo3_robot = EasyGoPiGo3()

app = Flask(__name__, static_url_path='')

@app.route("/robot", methods = ["POST"])
def robot_commands():

    # get the query
    args = request.args
    state = args['state']
    angle_degrees = int(float(args['angle_degrees']))
    angle_dir = args['angle_dir']
    force = float(args['force'])
    determined_speed = MIN_SPEED + force * (MAX_SPEED - MIN_SPEED) / MAX_FORCE
    if determined_speed > MAX_SPEED:
        determined_speed = MAX_SPEED

    if state == 'move':
        # for moving backward
        if angle_degrees >= 260 and angle_degrees <= 280:
            gopigo3_robot.set_speed(determined_speed)
            gopigo3_robot.backward()

        # for moving to the left or forward
        if angle_degrees > 90 and angle_degrees < 260:
            gopigo3_robot.set_motor_dps(gopigo3_robot.MOTOR_RIGHT, determined_speed)

            left_motor_percentage = abs((angle_degrees - 170) / 90)
            sign = -1 if angle_degrees >= 180 else 1

            gopigo3_robot.set_motor_dps(gopigo3_robot.MOTOR_LEFT, determined_speed * left_motor_percentage * sign)

        # for moving to the right (or forward)- upper half
        if angle_degrees < 90 and angle_degrees >= 0:
            gopigo3_robot.set_motor_dps(gopigo3_robot.MOTOR_LEFT, determined_speed)

            right_motor_percentage = angle_degrees / 90
            gopigo3_robot.set_motor_dps(gopigo3_robot.MOTOR_RIGHT, determined_speed * right_motor_percentage)
        # for moving to the right (or forward)- bottom half
        if angle_degrees <= 360 and angle_degrees > 280:
            gopigo3_robot.set_motor_dps(gopigo3_robot.MOTOR_LEFT, determined_speed)

            right_motor_percentage = (angle_degrees - 280) / 80 - 1
            gopigo3_robot.set_motor_dps(gopigo3_robot.MOTOR_RIGHT, determined_speed * right_motor_percentage)

    elif state == 'stop':
        gopigo3_robot.stop()
    else:
        app.logger.warning('unknown state sent')

    resp = Response()
    resp.mimetype = "application/json"
    resp.status = "OK"
    resp.status_code = 200

    return resp

@app.route("/")
def index():
    return page("index.html")

@app.route("/<string:page_name>")
def page(page_name):
    return render_template("{}".format(page_name))

@app.route("/static/<path:path>")
def send_static(path):
    return send_from_directory('static', path)

if __name__ == "__main__":
    app.run(debug = True, host = "0.0.0.0")
