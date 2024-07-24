import shutil
from pathlib import Path
from cht_pdf_to_mp4.exception import FileNotFoundError, InvalidFileError
from loguru import logger


def search_dir_and_copy_to_temp(ebook_path: Path, temp_path: Path) -> Path:
    """
    - 直接搜尋副檔名為pdf和mp3(不分大小寫)的檔案，抓取資料夾內的有效PDF和音檔
    - 篩選檔案大小大於2KB的PDF和音檔
    - 將找到的檔案複製到 temp/pdf 和 temp/audio 中
    :return: temp path
    """
    try:
        pdf_files = []
        audio_files = []

        logger.info(f"Reading '{str(ebook_path)}'")

        # 確保臨時目錄存在
        temp_pdf_path = temp_path / "pdf"
        temp_audio_path = temp_path / "audio"
        temp_pdf_path.mkdir(parents=True, exist_ok=True)
        temp_audio_path.mkdir(parents=True, exist_ok=True)

        # 搜索 PDF 和 MP3 文件
        for file in ebook_path.rglob('*'):
            if file.suffix.lower() == '.pdf' and file.stat().st_size > 2048:
                pdf_files.append(file)
            elif file.suffix.lower() == '.mp3' and file.stat().st_size > 2048:
                audio_files.append(file)

        # 檢查是否找到有效的文件
        if not pdf_files:
            raise FileNotFoundError(f"No valid PDF files found in '{str(ebook_path)}'")
        if not audio_files:
            raise FileNotFoundError(f"No valid MP3 files found in '{str(ebook_path)}'")

        logger.debug(f"Copying PDF and audio to '{str(temp_path)}'")

        # 複製文件到臨時目錄
        for pdf in pdf_files:
            shutil.copy(pdf, temp_pdf_path / "pdf.pdf")
        for audio in audio_files:
            shutil.copy(audio, temp_audio_path / audio.name)

        return temp_path

    except Exception as e:
        raise InvalidFileError(f"Error reading directory '{ebook_path}': {e}")
