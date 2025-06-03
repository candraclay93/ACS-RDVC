import yaml
import numpy as np
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QSlider, QComboBox, QFileDialog,
    QPushButton, QHBoxLayout, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap


class CVCalibrationDialog(QDialog):
    def __init__(self, yaml_path):
        super().__init__()
        self.setWindowTitle("CV Calibration Settings")
        self.setFixedSize(420, 420)
        self.yaml_path = yaml_path

        self.defaults = {
            "exposure": 10000,
            "size": "HD",
            "model_path": ""
        }
        self.settings = self.defaults.copy()
        self.load_yaml()

        layout = QVBoxLayout()

        # Exposure slider
        layout.addWidget(QLabel("Exposure"))
        self.exposure_slider = QSlider(Qt.Orientation.Horizontal)
        self.exposure_slider.setMinimum(0)
        self.exposure_slider.setMaximum(30000)
        self.exposure_slider.setValue(self.settings["exposure"])
        layout.addWidget(self.exposure_slider)

        # Size dropdown
        layout.addWidget(QLabel("Image Size"))
        self.size_dropdown = QComboBox()
        self.size_dropdown.addItems(["HD", "Full HD", "4MP"])
        self.size_dropdown.setCurrentText(self.settings["size"])
        layout.addWidget(self.size_dropdown)

        # Model file picker
        layout.addWidget(QLabel("Model Path"))
        model_layout = QHBoxLayout()
        self.model_path_line = QLineEdit(self.settings["model_path"])
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_model_file)
        model_layout.addWidget(self.model_path_line)
        model_layout.addWidget(browse_button)
        layout.addLayout(model_layout)

        # Start Calibration Button
        self.calibration_button = QPushButton("Start Calibration")
        self.calibration_button.clicked.connect(self.start_calibration)
        layout.addWidget(self.calibration_button)

        # Save and Reset buttons
        action_layout = QHBoxLayout()
        save_button = QPushButton("Save to YAML")
        save_button.clicked.connect(self.save_yaml)
        reset_button = QPushButton("Reset to Default")
        reset_button.clicked.connect(self.reset_defaults)
        action_layout.addWidget(save_button)
        action_layout.addWidget(reset_button)
        layout.addLayout(action_layout)

        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.capture_image)
        self.capture_count = 0

    def load_yaml(self):
        try:
            with open(self.yaml_path, 'r') as f:
                loaded = yaml.safe_load(f)
                if loaded:
                    self.settings.update(loaded)
        except Exception as e:
            print("Could not load YAML file:", e)

    def save_yaml(self):
        self.settings["exposure"] = self.exposure_slider.value()
        self.settings["size"] = self.size_dropdown.currentText()
        self.settings["model_path"] = self.model_path_line.text()

        try:
            with open(self.yaml_path, 'w') as f:
                yaml.dump(self.settings, f)
            QMessageBox.information(self, "Saved", "Settings saved successfully.")
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not save YAML file:\n{e}")

    def browse_model_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Model File", filter="PyTorch Model (*.pt)")
        if file_path:
            if file_path.endswith(".pt"):
                self.model_path_line.setText(file_path)
            else:
                QMessageBox.warning(self, "Invalid File", "Please select a .pt model file.")

    def reset_defaults(self):
        self.exposure_slider.setValue(self.defaults["exposure"])
        self.size_dropdown.setCurrentText(self.defaults["size"])
        self.model_path_line.setText(self.defaults["model_path"])

    def start_calibration(self):
        self.capture_count = 0
        self.timer.start(5000)  # Every 5 seconds

    def capture_image(self):
        self.capture_count += 1
        # Simulate a 640x480 grayscale image (replace this with real camera capture)
        dummy_img = (np.random.rand(480, 640) * 255).astype(np.uint8)
        height, width = dummy_img.shape
        q_img = QImage(dummy_img.data, width, height, width, QImage.Format.Format_Grayscale8)
        pixmap = QPixmap.fromImage(q_img)

        img_label = QLabel()
        img_label.setPixmap(pixmap)
        img_label.setWindowTitle(f"Capture {self.capture_count}")
        img_label.resize(pixmap.width(), pixmap.height())
        img_label.show()

        if self.capture_count >= 3:  # Stop after 3 captures for demo
            self.timer.stop()
