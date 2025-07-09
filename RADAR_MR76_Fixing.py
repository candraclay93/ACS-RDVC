import sys
import math
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PySide6.QtCore import QTimer, Signal, QThread
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from ctypes import *
import time

class ZLGReaderThread(QThread):
    new_frame = Signal(list)
    def __init__(self, lib_path="./libusbcan.so", device_type=4, device_index=0, channel=0, baud=0x1c00):
        super().__init__()
        self.running = True
        self.dev_type = device_type
        self.dev_idx = device_index
        self.channel = channel
        self.baud = baud
        self.lib = cdll.LoadLibrary(lib_path)

        class ZCAN_CAN_OBJ(Structure):
            _fields_ = [("ID", c_uint32),
                        ("TimeStamp", c_uint32),
                        ("TimeFlag", c_uint8),
                        ("SendType", c_byte),
                        ("RemoteFlag", c_byte),
                        ("ExternFlag", c_byte),
                        ("DataLen", c_byte),
                        ("Data", c_ubyte * 8),
                        ("Reserved", c_ubyte * 3)]
        self.ZCAN_CAN_OBJ = ZCAN_CAN_OBJ

    def run(self):
        self.lib.VCI_OpenDevice(self.dev_type, self.dev_idx, 0)

        class ZCAN_CAN_INIT_CONFIG(Structure):
            _fields_ = [("AccCode", c_int),
                        ("AccMask", c_int),
                        ("Reserved", c_int),
                        ("Filter", c_ubyte),
                        ("Timing0", c_ubyte),
                        ("Timing1", c_ubyte),
                        ("Mode", c_ubyte)]

        init_config = ZCAN_CAN_INIT_CONFIG()
        init_config.AccCode = 0
        init_config.AccMask = 0xFFFFFFFF
        init_config.Filter = 1
        init_config.Timing0 = self.baud & 0xFF
        init_config.Timing1 = self.baud >> 8
        init_config.Mode = 0

        self.lib.VCI_InitCAN(self.dev_type, self.dev_idx, self.channel, byref(init_config))
        self.lib.VCI_StartCAN(self.dev_type, self.dev_idx, self.channel)

        while self.running:
            count = self.lib.VCI_GetReceiveNum(self.dev_type, self.dev_idx, self.channel)
            if count > 0:
                can_arr = (self.ZCAN_CAN_OBJ * count)()
                rcv = self.lib.VCI_Receive(self.dev_type, self.dev_idx, self.channel, byref(can_arr), count, 100)
                for i in range(rcv):
                    if can_arr[i].ID == 0x62B and can_arr[i].DataLen == 8:
                        data = list(can_arr[i].Data)
                        self.new_frame.emit(data)
            time.sleep(0.05)

    def stop(self):
        self.running = False
        self.quit()
        self.wait()

class MR76Parser:
    def parse_target_info(self, data):
        dist_long_raw = ((data[1] << 5) | (data[2] >> 3)) & 0x1FFF
        dist_lat_raw = ((data[2] & 0x07) << 8) | data[3]
        vel_long_raw = ((data[4] << 6) | (data[5] >> 2)) & 0x3FFF
        vel_lat_raw = ((data[5] & 0x03) << 8) | ((data[6] & 0xE0) >> 5)
        obj_class = (data[6] >> 3) & 0x03
        dyn_prop = data[6] & 0x07
        rcs_raw = data[7]

        return {
            "id": data[0],
            "dist_long": dist_long_raw * 0.2 - 500,
            "dist_lat": dist_lat_raw * 0.2 - 204.6,
            "vel_rel_long": vel_long_raw * 0.25 - 128.0,
            "vel_rel_lat": vel_lat_raw * 0.25 - 64.0,
            "object_class": obj_class,
            "dynamic_prop": dyn_prop,
            "rcs": rcs_raw * 0.5 - 64.0
        }

class RadarPlot(QWidget):
    def __init__(self):
        super().__init__()
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self.parser = MR76Parser()
        self.frames = []

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(500)

    def add_frame(self, frame):
        """Add one frame to buffer from ZLGReaderThread."""
        self.frames.append(frame)

    def update_plot(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111, polar=True)
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        ax.set_rlim(0, 5)

        count = 0
        while self.frames and count < 10:
            frame = self.frames.pop(0)
            count += 1
            parsed = self.parser.parse_target_info(frame)

            x = parsed["dist_lat"]
            y = parsed["dist_long"]
            range_m = math.hypot(x, y)
            angle_rad = math.atan2(x, y)

            ax.scatter(angle_rad, range_m, label=f'ID {parsed["id"]}')

        ax.legend(loc='lower left', fontsize='x-small')
        self.canvas.draw()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MR76 Radar Viewer (Live ZLG Data)")

        # Create radar plot without preloaded frames
        self.radar_plot = RadarPlot()
        self.setCentralWidget(self.radar_plot)

        # Start ZLG CAN reader thread
        self.reader = ZLGReaderThread()
        self.reader.new_frame.connect(self.handle_new_frame)
        self.reader.start()

    def handle_new_frame(self, data):
        """Handle each new 8-byte CAN frame emitted by ZLGReaderThread."""
        self.radar_plot.add_frame(data)

    def closeEvent(self, event):
        """Ensure ZLG thread is stopped when window is closed."""
        self.reader.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())
