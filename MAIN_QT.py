# main.py
import multiprocessing as mp
from CANBUS_reader import can_listener
from CANBUS_viewer import run_gui
from CAM_reader import CameraFeed


if __name__ == "__main__":
    mp.set_start_method('spawn')  # safer for GUI multiprocessing on Linux

    queue = mp.Queue()
    img_queue = mp.Queue(maxsize=1)
    can_process = mp.Process(target=can_listener, args=(queue,))
    can_process.start()

    run_gui(queue, img_queue)
    can_process.join()
