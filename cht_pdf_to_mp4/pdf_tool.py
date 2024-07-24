from pathlib import Path
import shutil
from pdf2image import convert_from_path
from loguru import logger
import cv2
import numpy as np
from typing import List
import re


def is_blank_image(image_path: Path) -> bool:
    # 可以使用更多的方法來判斷是否為空白頁，這裡提供一個簡單的篩選條件
    if image_path.stat().st_size < 20480:  # 20KB
        return True

    img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)

    if np.all([img == 255]):
        logger.info(f"Image is white: {image_path}")
        return True
    else:
        return False


def pdf_to_images(pdf_paths: List[Path], temp_dir: Path) -> List[Path]:
    """
    1. 創一個新資料夾 images
    2. 把PDF轉成圖片檔存入 images
    3. 刪除檔案大小小於20KB（暫定）的空白頁（可能需要引入其他方法來判斷是否為空白頁）
    4. 將檔名存為陣列，以檔名 alphabetical, 數字 小到大排序（00視為0）
    :return: [image_names]
    """
    logger.debug(f"Converting PDF to images...")

    images_dir = temp_dir / 'images'
    images_dir.mkdir(parents=True, exist_ok=True)

    for pdf_path in pdf_paths:
        # 把PDF轉成圖片檔存入 images
        convert_from_path(pdf_path,
                          output_folder=images_dir,
                          # fmt='png',
                          fmt='jpeg',
                          output_file=f"image")

    # image_files = images_dir.glob(f"*.png")
    image_files = images_dir.glob(f"*.jpg")

    logger.debug(f"Searching for invalid images")

    # 刪除檔案大小小於20KB的空白頁
    valid_image_names = []
    for image in image_files:
        if not is_blank_image(image):
            valid_image_names.append(image)
        else:
            image.unlink()  # 刪除空白頁

    # 將檔名存為陣列，以檔名 alphabetical, 數字 小到大排序（00視為0）
    valid_image_names.sort(key=lambda x: (x.stem.split('-')[0], int(x.stem.split('-')[1])))

    return [Path(image) for image in valid_image_names]
