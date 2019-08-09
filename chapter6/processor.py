import cv2
import time

class MotionDetector(object):

#初期化
	def __init__(self, camera):
		self.camera = camera.start()
		self.background = None

#フレーム取り出し
	def get_frame(self):
		frame = self.detect()
		_, jpeg = cv2.imencode('.jpg', frame)
		return jpeg.tobytes()

#動体検知
	def detect(self):
		frame = self.camera.read()
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

		if self.background is None:
			self.background = gray
			return frame

		frameDelta = cv2.absdiff(self.background, gray)
		thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
		thresh = cv2.dilate(thresh, None, iterations=2)
		thresh = cv2.erode(thresh, None, iterations=2)

		cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
			cv2.CHAIN_APPROX_SIMPLE)[1]

		for c in cnts:
			if cv2.contourArea(c) < 2000:
				continue

			(x, y, w, h) = cv2.boundingRect(c)
			cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 2)
		
		return frame



class SingleCounter(object):
	def __init__(self, camera):
		self.camera = camera.start()
		self.background = None
		self.height = None
		self.width = None
		self.track_time = time.time()
		self.track_list = []
		self.timeout = 0.5
		self.total_right = 0
		self.total_left = 0

#フレーム取り出し
	def get_frame(self):
		frame = self.detect()
		_, jpeg = cv2.imencode('.jpg', frame)
		return jpeg.tobytes()


#物体選択
	def detect(self):
		frame = self.camera.read()

		if self.height is None or self.width is None:
			self.height, self.width = frame.shape[:2]

		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

		if self.background is None:
			self.background = gray
			return frame

		frameDelta = cv2.absdiff(self.background, gray)
		thresh = cv2.threshold(frameDelta, 50, 255, cv2.THRESH_BINARY)[1]
		thresh = cv2.dilate(thresh, None, iterations=2)
		thresh = cv2.erode(thresh, None, iterations=2)
		cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
			cv2.CHAIN_APPROX_SIMPLE)[1]

		biggest_area = 400
		motion_found = False
		for c in cnts:
			found_area = cv2.contourArea(c)
			if found_area > biggest_area:
				motion_found = True
				biggest_area = found_area
				(x, y, w, h) = cv2.boundingRect(c)
				cx = int(x + w / 2)
				cy = int(y + h / 2)


		if motion_found:
			cv2.rectangle(frame, (x, y), (x + w, y + h), (0.255, 0), 2)
			cv2.circle(frame, (cx, cy), 5, (0, 0, 255), 2)

			
		return frame


		



