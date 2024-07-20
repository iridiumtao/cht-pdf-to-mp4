from pathlib import Path


def pdf_to_images(pdf_path: Path) -> [str]:
    """
    1. 創一個新資料夾 images
    2. 把PDF轉成圖片檔存入 images
    3. 刪除檔案大小小於20KB（暫定）的空白頁（可能需要引入其他方法來判斷是否為空白頁）
    4. 將檔名存為陣列，以檔名 alphabetical, 數字 小到大排序（00視為0）
    :return: [image_names]
    """