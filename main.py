import os
from pathlib import Path
import json
from tqdm import tqdm
from loguru import logger
from cht_pdf_to_mp4.file_reader import search_dir_and_copy_to_temp, get_audio_length
from cht_pdf_to_mp4.pdf_tool import pdf_to_images
from cht_pdf_to_mp4.azure_tool import ocr_image, audio_to_text
from cht_pdf_to_mp4.text_matcher import text_similarity_checker
from cht_pdf_to_mp4.media_tool import create_video, merge_audio_video
from cht_pdf_to_mp4.exception import *
import shutil


def process_ebook(ebook_path: Path, temp_dir: Path, output_dir: Path):
    try:
        # 定義資料夾路徑
        temp_file = search_dir_and_copy_to_temp(ebook_path, temp_dir)

        # 轉換PDF為圖片
        all_images = pdf_to_images(pdf_dir=temp_dir / "pdf", temp_dir=temp_dir)

        logger.debug(all_images)
        ocr_image(all_images[0])

        # OCR圖片
        pages_data = {"pages": []}
        for image_path in all_images:
            ocr_result = ocr_image(image_path)
            pages_data["pages"].append({
                "page_number": image_path[-6:-4],
                "image_text": ocr_result,
                "image_file": str(image_path),
            })

        with open(f'{output_dir}/data.json', 'w') as f:
            json.dump(pages_data, f, indent=4)
        logger.info(json.dumps(pages_data, indent=4))


        # 語音辨識
        for audio in temp_file.get("audio"):
            audio_text = audio_to_text(audio)
            # audio to text 步驟會生成 wav 檔，先暫時直接用
            audio_length = get_audio_length(audio.with_suffix('.wav'))
            pages_data["pages"].append({
                "audio_text": audio_text,
                "audio_file": str(audio),
                "audio_length": audio_length,
            })
        with open(f'{output_dir}/data.json', 'w') as f:
            json.dump(pages_data, f, indent=4)
        logger.info(json.dumps(pages_data, indent=4))
        #
        # # 比對圖片文字與音檔文字
        # for page in pages_data["pages"]:
        #     if "audio_text" in page and "image_text" in page:
        #         matched_text = text_similarity_checker(page["audio_text"], page["image_text"])
        #         page["matched_text"] = matched_text
        #
        # # 儲存結果到JSON
        # with open(temp_dir / 'pages_data.json', 'w', encoding='utf-8') as f:
        #     json.dump(pages_data, f, ensure_ascii=False, indent=4)
        #
        # # 創建影片
        # create_video(pages_data, output_dir / f"{ebook_path.name}.mp4")
        #
        # # 合併影片和音檔
        # merge_audio_video(output_dir / f"{ebook_path.name}.mp4")
        #
        # logger.info(f"{ebook_path.name} 轉換成功")

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
