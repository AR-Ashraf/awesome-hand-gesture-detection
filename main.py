import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic, QtCore

from screen import Screen

counter = 0


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("splash_screen.ui", self)

        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.progress)
        # TIMER IN MILLISECONDS
        self.timer.start(35)

    def progress(self):
        global counter

        # CLOSE SPLASH SCREEN
        if counter > 50:
            # STOP TIMER
            self.timer.stop()

            # SHOW MAIN WINDOW
            self.mainScreen = Screen()
            self.mainScreen.webcamShow()
            self.mainScreen.show()

            # CLOSE SPLASH SCREEN
            self.close()

        # INCREASE COUNTER
        counter += 1


if __name__ == "__main__":
    app = QApplication(sys.argv)

    main = Main()
    main.show()

    try:
        sys.exit(app.exec_())
    except SystemExit:
        print("Closing Window...")
