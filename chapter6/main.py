from flask import Flask, Response
from threading import Condition
from camera import Camera
from processor import SingleCounter
import cv2
import io
import picamera

import os
import time
import datetime

from logging import getLogger, DEBUG, INFO, StreamHandler, Formatter
logger = getLogger(__name__)
handler = StreamHandler()
handler.setFormatter(Formatter('[%(levelname)s] %(asctime)s %(message)s'))
logger.addHandler(handler)

if os.environ.get('DEBUG', False):
    logger.setLevel(DEBUG)
else:
    logger.setLevel(INFO)


#HTTP_PORT = int(os.environ.get('HTTP_PORT', '5000'))
app = Flask(__name__)
camera = Camera()
#camera.start()
#processor = MotionDetector(camera)
processor = SingleCounter(camera)

def gen(processor):
	while  True:
		frame = processor.get_frame()
		#frame = camera.read()
		#_,jpeg = cv2.imencode('.jpg', frame)
		yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/stream')
def stream():
	return Response(gen(processor),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

	
if __name__ == '__main__':
	
	logger.info('start script.')

	try:
		app.run(host='0.0.0.0', debug=False, use_reloader=False)

    # Ctrol + Cや、終了コールがあった際はこのような例外が発生する。
	except KeyboardInterrupt:
		logger.info('goodbye.')

    # 終了時に画面をクリアする
	finally:
		camera.stop()

