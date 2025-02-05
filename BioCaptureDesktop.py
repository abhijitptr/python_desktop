import sys
import cv2
import numpy as np
import pymysql
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QGridLayout, QFileDialog, QLineEdit, QMessageBox
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
from mantra.MFS100 import MFS100  # type: ignore # Importing Mantra MFS100 SDK

class BioCaptureApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.mfs100 = MFS100()  # Initialize the Mantra MFS100 SDK
        self.photoPath = "FingerPrints"
        self.fingerprintPath = "Photos"

    def initUI(self):
        self.setWindowTitle('Bio-Metric Data Capture')
        self.setGeometry(100, 100, 800, 600)
        
        self.nameLabel = QLabel('Name:', self)
        self.nameInput = QLineEdit(self)
        
        self.idLabel = QLabel('User ID:', self)
        self.idInput = QLineEdit(self)
        
        self.photoLabel = QLabel(self)
        self.photoLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.photoLabel.setText("Photo Preview")
        
        self.fingerprintLabel = QLabel(self)
        self.fingerprintLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.fingerprintLabel.setText("Fingerprint Preview")
        
        self.capturePhotoButton = QPushButton('Capture Photo', self)
        self.capturePhotoButton.clicked.connect(self.capturePhoto)
        
        self.scanFingerprintButton = QPushButton('Scan Fingerprint', self)
        self.scanFingerprintButton.clicked.connect(self.scanFingerprint)
        
        self.saveButton = QPushButton('Save Data', self)
        self.saveButton.clicked.connect(self.saveData)
        
        self.statusLabel = QLabel('Status: Ready')
        
        layout = QGridLayout()
        layout.addWidget(self.nameLabel, 0, 0)
        layout.addWidget(self.nameInput, 0, 1, 1, 3)
        layout.addWidget(self.idLabel, 1, 0)
        layout.addWidget(self.idInput, 1, 1, 1, 3)
        layout.addWidget(self.photoLabel, 2, 0, 1, 2)
        layout.addWidget(self.capturePhotoButton, 3, 0)
        layout.addWidget(self.fingerprintLabel, 2, 2, 1, 2)
        layout.addWidget(self.scanFingerprintButton, 3, 2)
        layout.addWidget(self.saveButton, 4, 1, 1, 2)
        layout.addWidget(self.statusLabel, 5, 0, 1, 4)
        
        self.setLayout(layout)
        
    def capturePhoto(self):
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        if ret:
            filename, _ = QFileDialog.getSaveFileName(self, 'Save Image', '', 'Images (*.png *.jpg)')
            if filename:
                cv2.imwrite(filename, frame)
                self.displayImage(filename, self.photoLabel)
                self.photoPath = filename
                self.statusLabel.setText("Status: Photo Captured Successfully")

    def displayImage(self, filename, label):
        pixmap = QPixmap(filename)
        label.setPixmap(pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio))

    def scanFingerprint(self):
        try:
            self.mfs100.Init()
            fingerprint_data = self.mfs100.AutoCapture()
            if fingerprint_data:
                self.fingerprintPath = 'fingerprint.bmp'
                with open(self.fingerprintPath, 'wb') as file:
                    file.write(fingerprint_data)
                self.displayImage(self.fingerprintPath, self.fingerprintLabel)
                self.statusLabel.setText("Status: Fingerprint Captured Successfully")
            else:
                self.statusLabel.setText("Status: Fingerprint Capture Failed")
        except Exception as e:
            self.statusLabel.setText(f"Status: Error - {str(e)}")

    def saveData(self):
        user_name = self.nameInput.text()
        user_id = self.idInput.text()
        if not user_name or not user_id or not self.photoPath or not self.fingerprintPath:
            self.statusLabel.setText("Status: Please fill all fields and capture data.")
            return
        
        confirm = QMessageBox.question(self, 'Confirm Save', 'Are you sure you want to save this data?', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.No:
            return

        connection = pymysql.connect(host='localhost', user='root', password='', database='biometric_db')
        cursor = connection.cursor()
        cursor.execute("INSERT INTO users (user_id, name, photo, fingerprint) VALUES (%s, %s, %s, %s)",
                       (user_id, user_name, self.photoPath, self.fingerprintPath))
        connection.commit()
        connection.close()
        self.statusLabel.setText("Status: Data Saved Successfully")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BioCaptureApp()
    window.show()
    sys.exit(app.exec())
