import csv
import time
from queue import Empty
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QLabel, QFileDialog, QTableWidget,
    QTableWidgetItem, QHBoxLayout
)
from PyQt6.QtCore import QTimer

class RadarTestDialog(QDialog):
    def __init__(self, data_queue, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Radar Test")
        self.setMinimumSize(600, 400)

        self.data_queue = data_queue
        self.is_streaming = False
        self.csv_file = None
        self.csv_writer = None

        layout = QVBoxLayout()

        self.status_label = QLabel("Status: Idle")
        layout.addWidget(self.status_label)

        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Stream")
        self.start_button.clicked.connect(self.toggle_stream)
        button_layout.addWidget(self.start_button)

        self.choose_file_button = QPushButton("Choose CSV Output")
        self.choose_file_button.clicked.connect(self.choose_csv_file)
        button_layout.addWidget(self.choose_file_button)

        layout.addLayout(button_layout)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["ID", "Lat", "Long", "vLat", "vLong", "RCS"])
        layout.addWidget(self.table)

        self.timer = QTimer()
        self.timer.timeout.connect(self.poll_data)

        self.setLayout(layout)

    def choose_csv_file(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV files (*.csv)")
        if filename:
            self.csv_file = open(filename, 'w', newline='')
            self.csv_writer = csv.writer(self.csv_file)
            self.csv_writer.writerow(["timestamp", "id", "dist_lat", "dist_long", "vel_rel_lat", "vel_rel_long", "rcs"])
            self.status_label.setText(f"CSV Output: {filename}")

    def toggle_stream(self):
        if not self.is_streaming:
            if not self.csv_writer:
                self.status_label.setText("Error: Please choose a CSV file first.")
                return
            self.is_streaming = True
            self.start_button.setText("Stop Stream")
            self.status_label.setText("Streaming...")
            self.timer.start(100)
        else:
            self.is_streaming = False
            self.start_button.setText("Start Stream")
            self.status_label.setText("Stopped")
            self.timer.stop()
            if self.csv_file:
                self.csv_file.close()
                self.csv_file = None
                self.csv_writer = None

    def poll_data(self):
        while not self.data_queue.empty():
            try:
                obj = self.data_queue.get_nowait()
                self.csv_writer.writerow([
                    time.time(),
                    obj["id"],
                    obj["dist_lat"],
                    obj["dist_long"],
                    obj["vel_rel_lat"],
                    obj["vel_rel_long"],
                    obj["rcs"]
                ])
                self.append_row(obj)
            except Empty:
                break

    def append_row(self, obj):
        row_pos = self.table.rowCount()
        self.table.insertRow(row_pos)
        self.table.setItem(row_pos, 0, QTableWidgetItem(str(obj["id"])))
        self.table.setItem(row_pos, 1, QTableWidgetItem(f"{obj['dist_lat']:.2f}"))
        self.table.setItem(row_pos, 2, QTableWidgetItem(f"{obj['dist_long']:.2f}"))
        self.table.setItem(row_pos, 3, QTableWidgetItem(f"{obj['vel_rel_lat']:.2f}"))
        self.table.setItem(row_pos, 4, QTableWidgetItem(f"{obj['vel_rel_long']:.2f}"))
        self.table.setItem(row_pos, 5, QTableWidgetItem(f"{obj['rcs']:.2f}"))

    def closeEvent(self, event):
        self.timer.stop()
        if self.csv_file:
            self.csv_file.close()
        event.accept()
