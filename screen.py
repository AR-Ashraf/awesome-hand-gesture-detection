from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QWidget
from PyQt5 import uic
import cv2
import mediapipe as mp
import numpy as np
import os
from PIL import Image
import random


class Thread(QThread):
    changePixmap = pyqtSignal(QImage)
    mp_drawing = mp.solutions.drawing_utils
    mp_hands = mp.solutions.hands
    results = None
    count = 0
    tipIds = [4, 8, 12, 16, 20]
    xp, yp = 0, 0
    imgCanvas = np.zeros((480, 640, 3), np.uint8)
    bookSerial = 0


    def run(self):
        cap = cv2.VideoCapture(0)
        mp_drawing = self.mp_drawing
        mp_hands = self.mp_hands
        xp, yp = self.xp, self.yp
        imgCanvas = self.imgCanvas


        self.overlayList = []
        path = "adventure"
        myList = os.listdir(path)
        for book in myList:
            bookImgs = Image.open(f'{path}/{book}').convert('RGB')
            self.overlayList.append(bookImgs)



        with mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.5) as hands:
            while True:
                ret, frame = cap.read()

                if ret:
                    rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    rgbImage = cv2.flip(rgbImage, 1)
                    rgbImage.flags.writeable = False
                    self.results = hands.process(rgbImage)
                    rgbImage.flags.writeable = True
                    h, w, ch = rgbImage.shape
                    lmList = self.findPosition(rgbImage)

                    if self.count == 0:

                        if self.results.multi_hand_landmarks:

                            for num, hand in enumerate(self.results.multi_hand_landmarks):
                                mp_drawing.draw_landmarks(rgbImage, hand, mp_hands.HAND_CONNECTIONS,
                                                          mp_drawing.DrawingSpec(color=(56, 58, 89), thickness=2,
                                                                                 circle_radius=4),
                                                          mp_drawing.DrawingSpec(color=(250, 44, 250), thickness=2,
                                                                                 circle_radius=2),
                                                          )

                        if len(lmList) != 0:
                            x1, y1 = lmList[8][1:]
                            x2, y2 = lmList[12][1:]
                            finger = self.fingerUp()

                            if finger[0] == True and finger[1] == True and finger[2] == True and finger[3] == True and finger[4] == True:
                                if xp == 0 and yp == 0:
                                    xp, yp = x1, y1

                                cv2.line(imgCanvas, (xp, yp), (x1, y1), (0, 0, 0), 50)
                                cv2.circle(rgbImage, (x2, y2), 35, (0, 0, 0), cv2.FILLED)

                            elif finger[1] == True and finger[2] == True and finger[0] == False and finger[3] == False and finger[4] == False:
                                xp, yp = 0, 0

                            elif finger[1] == True and finger[2] == False:
                                if xp == 0 and yp == 0:
                                    xp, yp = x1, y1
                                cv2.line(rgbImage, (xp, yp), (x1, y1), (30, 144, 255), 15)
                                cv2.line(imgCanvas, (xp, yp), (x1, y1), (30, 144, 255), 15)

                            xp, yp = x1, y1

                        imgGrey = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
                        _, imgInv = cv2.threshold(imgGrey, 127, 255, cv2.THRESH_BINARY_INV)
                        imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
                        rgbImage = cv2.bitwise_and(rgbImage, imgInv)
                        rgbImage = cv2.bitwise_or(rgbImage, imgCanvas)

                    if self.count == 1:
                        if len(lmList) != 0:
                            x1, y1 = lmList[8][1:]
                            finger = self.fingerUp()

                            if finger[1] == True and finger[2] == False:
                                if xp == 0 and yp == 0:
                                    xp, yp = x1, y1

                                # bookImg = cv2.resize(bookImg, (100, 160), interpolation=cv2.INTER_AREA)
                                bookImg = self.overlayList[self.bookSerial]
                                bookImg = bookImg.resize((100, 160), Image.ANTIALIAS)
                                bookImg = np.array(bookImg)
                                rgbImage[y1 - 170: y1 - 10, x1 - 50: x1 + 50] = bookImg

                            if finger[0] == False and finger[1] == False and finger[2] == False and finger[3] == False and finger[4] == False:
                                if xp == 0 and yp == 0:
                                    xp, yp = x1, y1
                                self.bookSerial = random.randint(0, len(self.overlayList))

                            xp, yp = x1, y1


                    bytesPerLine = ch * w
                    convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                    p = convertToQtFormat.scaled(991, 641)
                    self.changePixmap.emit(p)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        cap.release()
        cv2.destroyAllWindows()

    def findPosition(self, img, handNo=0):
        self.lmList = []

        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]

            for id, lm in enumerate(myHand.landmark):
                height, width, cho = img.shape

                cx, cy = int(lm.x * width), int(lm.y * height)
                self.lmList.append([id, cx, cy])

        return self.lmList

    def fingerUp(self):
        fingers = []

        # Thumb
        if self.lmList[self.tipIds[0]][1] < self.lmList[self.tipIds[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # 4 fingers
        for id in range(1, 5):
            if self.lmList[self.tipIds[id]][2] < self.lmList[self.tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers




class Screen(QWidget):



    def __init__(self):
        super().__init__()
        uic.loadUi("screen.ui", self)
        self.webcamShow()
        self.academicRadio.setChecked(True)
        self.acdClicked()
        self.academicRadio.clicked.connect(lambda: self.acdClicked())
        self.bookRadio.clicked.connect(lambda: self.bookClicked())




    def webcamShow(self):
        th = Thread(self)
        th.changePixmap.connect(self.setImage)
        th.start()

    @pyqtSlot(QImage)
    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))

    def acdClicked(self):
        Thread.count = 0
        print("Academic Radio Clicked")

    def bookClicked(self):
        Thread.count = 1
        print("Book Radio Clicked")






