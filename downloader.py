import os
import argparse
import pandas as pd
from pytubefix import YouTube
from pytubefix.cli import on_progress
from moviepy.video.io.VideoFileClip import VideoFileClip


def download_youtube_video(video_id, vids_folder):
    youtube_url = f'https://www.youtube.com/watch?v={video_id}'
    yt = YouTube(youtube_url, on_progress_callback=on_progress)
    stream = yt.streams.get_highest_resolution()
    video_path = stream.download(output_path=vids_folder, filename=f"{video_id}.mp4", skip_existing=True)
    print(f"[ID] {video_id}.mp4 다운로드 완료. 경로: {video_path}")
    return video_path


def make_video_clip(video_path, start, end, vids_folder, video_id, category):
    clip_name = f"<clip>_{video_id}_[{start}]s_[{end}]s_{category}.mp4"
    clip_path = os.path.join(vids_folder, clip_name)

    if os.path.exists(clip_path):
        print(f"[CLIP] 클립 이미 있음. 스킵됨: {clip_path}")
    else:
        with VideoFileClip(video_path) as video:
            clip = video.subclip(start,end)
            clip.write_videofile(clip_path, codec="libx264")
            print(f"[CLIP] 클립 저장됨: {clip_path}")


def process_videos(df, vids_folder):
    temp_video_id = None
    for _, row in df.iterrows():
        video_id = row['Video ID']
        start = row['Start']
        end = row['End']
        category = row['Category']

        if pd.isna(video_id):
            video_id = temp_video_id
        
        video_path = os.path.join(vids_folder, f"{video_id}.mp4")

        if video_id != temp_video_id:
            if temp_video_id is not None and os.path.exists(os.path.join(vids_folder, f"{temp_video_id}.mp4")):
                os.remove(os.path.join(vids_folder, f"{temp_video_id}.mp4"))
            temp_video_id = video_id
            try:
                video_path = download_youtube_video(video_id, vids_folder)
            except Exception as e:
                print(f"[ERROR] {video_id} 다운로드 실패: {e}")
                continue
        
        if os.path.exists(video_path) and not pd.isna(start) and not pd.isna(end) and not pd.isna(category):
            make_video_clip(video_path, start, end, vids_folder, video_id, category)

    if temp_video_id is not None:
        os.remove(os.path.join(vids_folder, f"{temp_video_id}.mp4"))
    print("모든 유튜브 클립을 성공적으로 다운로드하고 처리하였습니다.")


def main():
    parser = argparse.ArgumentParser(description="YouTube Download For Dense Video Captioning Dataset")
    parser.add_argument("--xlsx_from", type=str, default="video_id.xlsx", help="엑셀 파일 경로")
    parser.add_argument("--save_videos", type=str, default="vids", help="처리된 비디오를 저장할 디렉토리 경로")

    args = parser.parse_args()

    if not os.path.exists(args.save_videos):
        os.makedirs(args.save_videos)

    df = pd.read_excel(args.xlsx_from)
    process_videos(df, args.save_videos)

if __name__ == "__main__":
    main()