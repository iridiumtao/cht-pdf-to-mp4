from cht_pdf_to_mp4.exception import TextMatchingError
from config.setting import get_settings

from openai import OpenAI
import json
from pathlib import Path
from loguru import logger

settings = get_settings()

client = OpenAI(
    api_key=settings.ebook_openai_api_key
)


def merge_recognition_results(image_data, speech_data):
    """
    1. 可能用TF-IDF做相似度匹配或是其他模糊搜尋演算法
    2. 比對順序演算法：音1比對圖1、音1比對圖2、音1比對圖3；音2比對圖4；音3比對圖5；音4比對圖6、音4比對圖7
    3. 將匹配的結果存入JSON
    4. 用一function取得音檔長度並存入JSON
    5. 如果判定有問題的話就不做並記錄
    """
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system",
             "content": (
                 "You are an assistant skilled in comparing and matching texts "
                 "from image-to-text and speech-to-text recognition results. "
                 "Given two JSON files, "
                 "one with image recognition results and the other with speech recognition results, "
                 "your task is to compare, match, and combine the texts into a single JSON file "
                 "that contains all the information "
                 "(page_number, image_text, image_file, audio_number, speech_text, audio_file, audio_length) "
                 "from each provided JSON file."
                 "The combined results should be under the key 'data'."
                 "Return a valid JSON file only. Do not use code blocks."
             )},
            {"role": "user", "content": (
                f"{json.dumps(image_data, indent=4)}\n\n"
                f"{json.dumps(speech_data, indent=4)}"
            )}
        ]
    )

    logger.debug(completion)
    logger.info(completion.usage)
    result = completion.choices[0].message.content
    logger.debug(result)

    if _validate(result):
        logger.info("JSON Valid!")
        return result
    else:
        logger.warning("JSON Invalid. Will try again.")
        # GPT 再生一次看看
        return _json_invalid_ai_handler(result)


def _validate(json_str):
    try:
        json.loads(json_str)  # put JSON-data to a variable
        print("Valid JSON")  # in case json is valid
        return True
    except json.decoder.JSONDecodeError:
        print("Invalid JSON")  # in case json is invalid
        return False


def _json_invalid_ai_handler(result):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": (
                f"The following JSON string would raise json.decoder.JSONDecodeError."
                "You need to answer the fixed JSON string. Return a valid JSON file only. Do not use code blocks.\n\n"
                f"{result}"
            )}
        ]
    )
    result = completion.choices[0].message.content

    if _validate(result):
        return result
    else:
        logger.error("JSON Invalid")
        raise TextMatchingError(json.dumps(image_data, indent=4),
                                json.dumps(speech_data, indent=4))


if __name__ == "__main__":
    image_data = Path("/Users/oud/Documents/cht-pdf-to-mp4/data/output/Pete in the Postbox/image.json")
    speech_data = Path("/Users/oud/Documents/cht-pdf-to-mp4/data/output/Pete in the Postbox/speech.json")
    with open(image_data, 'r') as file:
        image_dict = json.load(file)

    with open(speech_data, 'r') as file:
        speech_dict = json.load(file)
    merged = merge_recognition_results(image_dict, speech_dict)
    json.dumps(merged, indent=4)
