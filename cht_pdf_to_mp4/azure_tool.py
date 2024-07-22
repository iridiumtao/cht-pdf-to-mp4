from pathlib import Path
from config.setting import get_settings

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes, ComputerVisionOcrErrorException
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from array import array
import os
from loguru import logger

from PIL import Image
import sys
import time
import re

settings = get_settings()
vision_key = settings.vision_key
vision_endpoint = settings.vision_endpoint
speech_key = settings.speech_key
speech_region = settings.speech_region


def ocr_image(image_path: Path) -> str:
    """
    - 使用 Azure AI Vision OCR 服務將圖片轉成文字
    :return: text
    """
    time.sleep(1)

    '''
    Authenticate
    Authenticates your credentials and creates a client.
    '''
    subscription_key = vision_key
    endpoint = vision_endpoint

    computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))
    '''
    END - Authenticate
    '''

    '''
    OCR: Read File using the Read API, extract text - remote
    This example will extract text in an image, then print results, line by line.
    This API call can also extract handwriting style text (not shown).
    '''
    logger.debug("===== Read File =====")
    with open(image_path, 'rb') as image:

        try:
            read_response = computervision_client.read_in_stream(image, language="en", raw=True)

            # Get the operation location (URL with an ID at the end) from the response
            read_operation_location = read_response.headers["Operation-Location"]
            # Grab the ID from the URL
            operation_id = read_operation_location.split("/")[-1]

            # Call the "GET" API and wait for it to retrieve the results
            while True:
                read_result = computervision_client.get_read_result(operation_id)
                if read_result.status not in ['notStarted', 'running']:
                    break
                time.sleep(1)

            results = []

            # Print the detected text, line by line
            if read_result.status == OperationStatusCodes.succeeded:
                for text_result in read_result.analyze_result.read_results:
                    for line in text_result.lines:
                        results.append(line.text)
                        # print(line.text)
                        # print(line.bounding_box)

            result = filter_strings_with_alpha(results)

            logger.debug(f"OCR Result {image_path[-6:-4]}: {result}")
        except ComputerVisionOcrErrorException as e:
            logger.error(e)
            logger.info(e.response)
            if "Too Many Requests" in e.response:
                logger.info("Exceeded API rate limit. (Free: 20 requests per minute, Standard: 10 requests per second)")
                logger.info("We just retry after 60 second.")
            time.sleep(60)
            return ocr_image(image_path)

    '''
    END - Read File - remote
    '''

    logger.debug("End of Computer Vision.")
    return result


def filter_strings_with_alpha(strings_list):
    # 使用正則表達式檢查字串是否包含字母
    pattern = re.compile(r'[a-zA-Z]')
    # 過濾列表，只保留包含字母的字串
    filtered_list = [s for s in strings_list if pattern.search(s)]
    return " ".join(filtered_list)


def audio_to_text(audio_path: Path) -> dict:
    """
    - 使用 Azure AI Speech 的 Speech to Text 服務將音檔轉成文字
    - 將文字存入 dict
    :return: pages_data

    """
    pass


if __name__ == "__main__":
    # ocr_image(Path("temp/images/image0001-01.jpg"))
    ocr_image(Path("../temp/images/image0001-08.jpg"))
