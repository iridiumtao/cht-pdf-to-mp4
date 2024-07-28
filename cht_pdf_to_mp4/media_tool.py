from pathlib import Path
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from loguru import logger


def create_video(pages_data: dict, output_path: Path):
    """依照頁碼順序放置圖片，並依照音檔長度設定畫面長度"""
    clips = []

    for page in pages_data['data']:
        image_path = page['image_file']
        audio_path = page['audio_file']
        audio_length = page['audio_length']

        if audio_path or audio_length is not None:

            # Load image and set duration
            image_clip = ImageClip(image_path).set_duration(audio_length+2)

            # Load audio
            audio_clip = AudioFileClip(audio_path).subclip(0, audio_length)

            # Set audio to image clip
            video_clip = image_clip.set_audio(audio_clip)
        else:
            audio_length = 3
            image_clip = ImageClip(image_path).set_duration(audio_length+2)
            video_clip = image_clip

        clips.append(video_clip)

    # Concatenate all video clips
    final_clip = concatenate_videoclips(clips, method="compose")

    # Write the result to a file
    final_clip.write_videofile(str(output_path),
                               threads=8,
                               fps=5,
                               codec='libx264',
                               audio_codec='aac')

    logger.info("video created!")


if __name__ == "__main__":
    import json, os
    with open("/Users/oud/Documents/cht-pdf-to-mp4/temp/data.json") as f:
        data = json.load(f)
    os.chdir("..")
    create_video(pages_data=data, output_path=Path('data/output/test.mp4'))