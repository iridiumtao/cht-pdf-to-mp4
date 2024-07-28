import os
from pathlib import Path
import json
from tqdm import tqdm
from loguru import logger
from cht_pdf_to_mp4.file_reader import search_dir_and_copy_to_temp, get_audio_length, get_files_with_suffix
from cht_pdf_to_mp4.pdf_tool import pdf_to_images
from cht_pdf_to_mp4.azure_tool import ocr_image, audio_to_text
from cht_pdf_to_mp4.text_matcher import merge_recognition_results
from cht_pdf_to_mp4.media_tool import create_video
from cht_pdf_to_mp4.exception import *
import shutil


def process_ebook(ebook_path: Path, temp_dir: Path, output_dir: Path):
    try:
        # 定義資料夾路徑
        pdf_paths, audio_paths = search_dir_and_copy_to_temp(ebook_path, temp_dir)

        if not (temp_dir / "images").exists():
            # 轉換PDF為圖片
            all_images = pdf_to_images(pdf_paths=pdf_paths, temp_dir=temp_dir)
        else:
            all_images = get_files_with_suffix((temp_dir / "images"), "jpg")

        logger.debug(all_images)

        # OCR圖片
        image_data = {"image": []}
        for image_path in all_images:
            ocr_result = ocr_image(image_path)
            image_data["image"].append({
                "page_number": str(image_path)[-6:-4],
                "image_text": ocr_result,
                "image_file": str(image_path),
            })

        # 確保目錄存在
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / 'image.json'
        with open(output_file, 'w+') as f:
            json.dump(image_data, f, indent=4)
        logger.info(json.dumps(image_data, indent=4))


        # 語音辨識
        speech_data = {"speech": []}
        for audio in audio_paths:
            audio_text = audio_to_text(audio)
            # audio to text 步驟會生成 wav 檔，先暫時直接用
            audio_length = get_audio_length(audio.with_suffix('.wav'))
            speech_data["speech"].append({
                "audio_number": audio.stem,
                "speech_text": audio_text,
                "audio_file": str(audio),
                "audio_length": audio_length,
            })
        # 確保目錄存在
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / 'speech.json'
        with open(output_file, 'w+') as f:
            json.dump(speech_data, f, indent=4)
        logger.info(json.dumps(speech_data, indent=4))

        merged_result = merge_recognition_results(image_data, speech_data)
        merged_dict = json.loads(merged_result)

        # 儲存結果到JSON
        with open(temp_dir / 'data.json', 'w', encoding='utf-8') as f:
            json.dump(merged_dict, f, ensure_ascii=False, indent=4)

        if not isinstance(merged_dict, dict) or not merged_result:
            raise VideoCreationError("merged_result JSON invalid or not generated.")
        # 創建影片
        create_video(merged_dict, output_dir / f"{ebook_path.name}.mp4")

    except (FileNotFoundError, InvalidFileError, OCRProcessingError,
            SpeechRecognitionError, TextMatchingError, VideoCreationError,
            AudioVideoSyncError, ConfigurationError) as e:
        logger.error(f"Error processing {ebook_path.name}: {e}")


def main():
    logger.add("log/log_{time}.log")

    input_dir = Path('data/input')
    temp_dir = Path('temp')
    output_dir = Path('data/output')

    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    temp_dir.mkdir(parents=True, exist_ok=True)

    ebooks = [d for d in input_dir.iterdir() if d.is_dir()]

    for ebook in tqdm(ebooks, desc="Processing eBooks"):
        ebook_name = ebook.name
        if temp_dir.exists():
            # 刪除資料夾內的所有檔案
            shutil.rmtree('temp')

        process_ebook(ebook, temp_dir, output_dir / ebook_name)


if __name__ == "__main__":
    main()
