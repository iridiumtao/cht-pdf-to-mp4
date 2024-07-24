# 中華電信電子書 Project PDF to MP4

## 目標

用mp4影片檔來播放電子書

- 作者頁顯示三秒
- 撤除空白與無效頁面（如果可以）
- 畫面內容與音檔對上
- 內容頁面的時間長度為音檔長度+留白2秒

## 步驟

1. 把資料夾內的有效PDF和音檔全部抓出來
    1. 直接用資料夾內搜尋副檔名並判斷檔案大小是否大於2KB（暫定），不論效率
2. 把PDF轉成圖片檔
    1. 創一個新資料夾 images
    2. 把PDF轉成圖片檔存入 images
    3. 刪除檔案大小小於20KB（暫定）的空白頁（可能需要引入其他方法來判斷是否為空白頁）
    4. 將檔名存為陣列，以檔名 alphabetical, 數字 小到大排序（00視為0）
3. 將圖片檔OCR成文字並結構化資料
    1. 利用 Azure AI Vision 的 OCR 服務取得文字
    2. 存入JSON（或dict）
4. 將音檔語音辨識為文字並結構化資料
    1. 利用 Azure AI speech 的 Speech to Text 服務取得文字
    2. 存入JSON
5. 固定圖片檔順序的情況下，比對並配對圖片文字語音檔文字，結構化為JSON檔，並取得音檔長度
    1. 可能用TF-IDF做相似度匹配或是其他模糊搜尋演算法
    2. 比對順序演算法：音1比對圖1、音1比對圖2、音1比對圖3；音2比對圖4；音3比對圖5；音4比對圖6、音4比對圖7
    3. 將匹配的結果存入JSON
    4. 用一function取得音檔長度並存入JSON
    5. 如果判定有問題的話就不做並記錄
6. 做出影片
    1. 存取JSON檔
    2. 依頁碼順序放置圖片，並依照音檔長度設定畫面長度
7. 做出聲音
    1. 如果遇到只有畫面沒有聲音的，就讓音檔延遲n秒
8. 將影片與音檔結合
    1. 比對兩檔案播放長度，如果誤差過大就不做並記錄

## JSON結構

- 頁碼
  - 圖片文字
  - 音檔文字
  - 音檔檔名
  - 音檔長度

## Build


`conda create --name cht-pdf-to-mp4 python=3.12`

`conda activate cht-pdf-to-mp4`

poppler is required.
see https://github.com/Belval/pdf2image

ffmpeg is required for pydub to read mp3
