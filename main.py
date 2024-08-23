import os
import argparse
import pandas as pd
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QMessageBox, QMainWindow, QWidget, QPushButton, QAction, QHBoxLayout, QVBoxLayout, QSlider, QLabel, QSizePolicy, QStyle
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl, Qt
import sys
import downloader


class VideoLabelingTool(QMainWindow):
    def __init__(self, df, vids_folder, result_file):
        super(VideoLabelingTool, self).__init__()

        self.df = df
        self.vids_folder = vids_folder
        self.result_file = result_file
        self.current_index = 0
        self.temp_id = ""
        self.temp_index = 0

        self.initUI()
        
        try:
            while (not pd.isna(self.df.iloc[self.current_index]['Status'])):
                self.current_index += 1
        except:
            None

        self.temp_index = self.current_index

        while(pd.isna(self.df.iloc[self.temp_index]['Video ID'])):
            self.temp_index -= 1
        self.temp_id = self.df.iloc[self.temp_index]['Video ID']

        self.load_clip(self.current_index)
        
    def initUI(self):
        self.setWindowTitle('Video Labeling Tool')

        # MediaPlayer to handle video playback
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVolume(50)
        self.video_widget = QVideoWidget(self)
        
        # Play Button
        self.play_button = QPushButton()
        self.play_button.setEnabled(False)
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.clicked.connect(self.play)

        # Slider to control video position
        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 0)
        self.position_slider.sliderMoved.connect(self.setPosition)

        # Error label
        self.error_label = QLabel()
        self.error_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        self.video_info_label = QLabel(self)
        self.video_info_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.update_video_info_label()  # 라벨 내용 업데이트

        # Text fields
        self.entry1 = QtWidgets.QLineEdit(self)
        self.entry2 = QtWidgets.QLineEdit(self)
        self.entry3 = QtWidgets.QLineEdit(self)
        self.entry4 = QtWidgets.QLineEdit(self)
        self.entry5 = QtWidgets.QLineEdit(self)

        # Confirm button
        self.confirm_button = QtWidgets.QPushButton("확인", self)
        self.confirm_button.clicked.connect(self.press_confirm)

        # Backward Button
        self.backward_button = QPushButton("이전", self)
        self.backward_button.setEnabled(True)
        self.backward_button.clicked.connect(self.press_backward)

        # Layouts
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.position_slider)
        control_layout.addWidget(self.backward_button)

        layout = QVBoxLayout()
        layout.addWidget(self.video_widget)
        layout.addLayout(control_layout)
        layout.addWidget(self.video_info_label)
        layout.addWidget(self.entry1)
        layout.addWidget(self.entry2)
        layout.addWidget(self.entry3)
        layout.addWidget(self.entry4)
        layout.addWidget(self.entry5)
        layout.addWidget(self.confirm_button)
        layout.addWidget(self.error_label)

        wid = QWidget(self)
        wid.setLayout(layout)
        self.setCentralWidget(wid)

        # Connect media player signals to slots
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.stateChanged.connect(self.mediaStateChanged)
        self.media_player.positionChanged.connect(self.positionChanged)
        self.media_player.durationChanged.connect(self.durationChanged)
        self.media_player.error.connect(self.handleError)
        self.media_player.mediaStatusChanged.connect(self.mediaStatusChanged)

    def update_video_info_label(self):
        total_clips = len(self.df)
        video_id = self.df.iloc[self.current_index]['Video ID'] if not pd.isna(self.df.iloc[self.current_index]['Video ID']) else self.temp_id
        start = self.df.iloc[self.current_index]['Start']
        end = self.df.iloc[self.current_index]['End']
        
        self.video_info_label.setText(f"Clip {self.current_index + 1}/{total_clips}, Video ID: {video_id}, Start: {start}s, End: {end}s")

    def load_clip(self, index):
        row = self.df.iloc[index]
        video_id = row['Video ID'] if not pd.isna(row['Video ID']) else self.temp_id
        self.temp_id = video_id
        start = row['Start']
        end = row['End']

        self.entry1.setText(str(row['Sentence_1'])) if pd.isna(row['Reviewed_Sentence_1']) or str(row['Reviewed_Sentence_1']) == '' else self.entry1.setText(str(row['Reviewed_Sentence_1']))
        self.entry2.setText(str(row['Sentence_2'])) if pd.isna(row['Reviewed_Sentence_2']) or str(row['Reviewed_Sentence_2']) == '' else self.entry2.setText(str(row['Reviewed_Sentence_2']))
        self.entry3.setText(str(row['Sentence_3'])) if pd.isna(row['Reviewed_Sentence_3']) or str(row['Reviewed_Sentence_3']) == '' else self.entry3.setText(str(row['Reviewed_Sentence_3']))
        self.entry4.setText(str(row['Category'])) if pd.isna(row['Reviewed_Category']) or str(row['Reviewed_Category']) == '' else self.entry4.setText(str(row['Reviewed_Category']))
        self.entry5.setText(str(row['Audio'])) if pd.isna(row['Reviewed_Audio']) or str(row['Reviewed_Audio']) == '' else self.entry5.setText(str(row['Reviewed_Audio']))

        self.update_video_info_label()

        if os.getcwd() in self.vids_folder:
            video_path = os.path.join(self.vids_folder, f"<clip>_{video_id}_[{start}]s_[{end}]s_{row['Category']}.mp4")
        else:
            video_path = os.path.join(os.getcwd(), self.vids_folder, f"<clip>_{video_id}_[{start}]s_[{end}]s_{row['Category']}.mp4")
        print(video_path)
        
        if os.path.exists(video_path):
            mediacontent = QMediaContent(QUrl.fromLocalFile(video_path))
            self.media_player.setMedia(mediacontent)
            self.play_button.setEnabled(True)
            self.media_player.play()

            video_meta_data = mediacontent.canonicalResource().resolution()
            if video_meta_data.isValid():
                video_width = video_meta_data.width()
                video_height = video_meta_data.height()
                self.resize(video_width, video_height + 150)
            else:
                self.resize(800, 750)
        else:
            self.confirm_label("Error")

    def press_confirm(self):
        self.confirm_label(status='Confirm')

    def press_backward(self):
        row = self.df.iloc[self.current_index]
        before_labels = [row['Sentence_1'], row['Sentence_2'], row['Sentence_3'], row['Category'], row['Audio']]
        after_labels = [self.entry1.text(), self.entry2.text(), self.entry3.text(), self.entry4.text(), self.entry5.text()]

        self.df.at[self.current_index, 'Reviewed_Category'] = after_labels[3] if before_labels[3] != after_labels[3] else ''
        self.df.at[self.current_index, 'Reviewed_Audio'] = after_labels[4] if before_labels[4] != after_labels[4] else ''
        self.df.at[self.current_index, 'Reviewed_Sentence_1'] = after_labels[0] if before_labels[0] != after_labels[0] else ''
        self.df.at[self.current_index, 'Reviewed_Sentence_2'] = after_labels[1] if before_labels[1] != after_labels[1] else ''
        self.df.at[self.current_index, 'Reviewed_Sentence_3'] = after_labels[2] if before_labels[2] != after_labels[2] else ''
        self.df.to_excel(self.result_file, index=False)

        self.current_index -= 1
        if self.current_index >= 0:
            self.temp_index = self.current_index
            while(pd.isna(self.df.iloc[self.temp_index]['Video ID'])):
                self.temp_index -= 1

            self.temp_id = self.df.iloc[self.temp_index]['Video ID']
            self.load_clip(self.current_index)
        else:
            QMessageBox.information(self, "알림", "처음 비디오 클립입니다.")
            self.current_index += 1    

    def confirm_label(self, status):
        row = self.df.iloc[self.current_index]
        before_labels = [row['Sentence_1'], row['Sentence_2'], row['Sentence_3'], row['Category'], row['Audio']]
        after_labels = [self.entry1.text(), self.entry2.text(), self.entry3.text(), self.entry4.text(), self.entry5.text()]

        self.df.at[self.current_index, 'Reviewed_Category'] = after_labels[3] if before_labels[3] != after_labels[3] else ''
        self.df.at[self.current_index, 'Reviewed_Audio'] = after_labels[4] if before_labels[4] != after_labels[4] else ''
        self.df.at[self.current_index, 'Reviewed_Sentence_1'] = after_labels[0] if before_labels[0] != after_labels[0] else ''
        self.df.at[self.current_index, 'Reviewed_Sentence_2'] = after_labels[1] if before_labels[1] != after_labels[1] else ''
        self.df.at[self.current_index, 'Reviewed_Sentence_3'] = after_labels[2] if before_labels[2] != after_labels[2] else ''
        self.df.at[self.current_index, 'Status'] = status
        self.df.to_excel(self.result_file, index=False)

        self.current_index += 1
        if self.current_index < len(self.df):
            self.load_clip(self.current_index)
        else:
            QMessageBox.information(self, "알림", "모든 비디오 클립을 리뷰하였습니다.")
            self.close()

    def play(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

    def mediaStateChanged(self, state):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.position_slider.setValue(position)

    def durationChanged(self, duration):
        self.position_slider.setRange(0, duration)

    def setPosition(self, position):
        self.media_player.setPosition(position)

    def handleError(self):
        self.play_button.setEnabled(False)
        self.error_label.setText("Error: " + self.media_player.errorString())

    def mediaStatusChanged(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.media_player.setPosition(0)
            self.media_player.play()

def main():
    parser = argparse.ArgumentParser(description="Youtube Video Labeling Tool")
    parser.add_argument("--xlsx_from", type=str, default="Annotations.xlsx", help="엑셀 파일 경로")
    parser.add_argument("--save_videos", type=str, default="vids", help="처리된 비디오를 저장할 디렉토리 경로")
    args = parser.parse_args()

    if not os.path.exists(args.save_videos):
        os.makedirs(args.save_videos)

    
    df = pd.read_excel(args.xlsx_from)

    if (input("비디오를 다운로드하시겠습니까? (y/n): ") == 'y'):
        downloader.process_videos(df, args.save_videos)

    app = QtWidgets.QApplication(sys.argv)
    window = VideoLabelingTool(df, args.save_videos, args.xlsx_from)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()