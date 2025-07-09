from PyQt6.QtWidgets import QFileDialog, QMessageBox

def selectVideoDialog(self):
    file_path, _ = QFileDialog.getOpenFileName(
        self,
        "Select Video File",
        "",
        "Video Files (*.mp4 *.avi *.mov *.mkv)"
    )
    if file_path:
        # Store or process the path if needed
        self.selected_video_path = file_path

        # Optional: Show confirmation popup
        QMessageBox.information(self, "Video Selected", f"Selected file:\n{file_path}")
