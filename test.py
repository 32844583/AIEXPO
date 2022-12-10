import os
import numpy as np
import re
from urllib.parse import parse_qsl
from flask import Flask, request, abort
import imutils
import easyocr
import time
import shutil
import cv2
import torch
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    LocationSendMessage, ImageSendMessage, StickerSendMessage,
    VideoSendMessage, TemplateSendMessage, ButtonsTemplate, PostbackAction, MessageAction, URIAction,
    PostbackEvent, ConfirmTemplate, CarouselTemplate, CarouselColumn,
    ImageCarouselTemplate, ImageCarouselColumn, FlexSendMessage
)
import json

# create flask server
app = Flask(__name__)
line_bot_api = LineBotApi('HztiZOU9ZzSNRo3nZkSJBG4ogUbRVNi3M7C5ZFl2MwIMUdOwISgXfxO4PEyoZ+Tbwhz1W9373cDeD88w/S9k5NWI057BRN4MOlVd/pCQW2iVRp9uKnGw7xqZJ7oT01FEJNZLY1VS4FjFlM7hTsaX7AdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('cf7f7ae047a99d9b97604b6c3fa391d2')
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        print('receive msg')
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'

# handle msg
@handler.add(MessageEvent)
def handle_message(event):
    if (event.message.type == "image"):
        SendImage = line_bot_api.get_message_content(event.message.id)
        curpath = os.path.abspath(os.curdir)
        curpath = '/'.join(curpath.split("\\"))

        path = curpath + '/static/' + event.message.id + '.jpg'
        with open(path, 'wb') as fd:
            for chenk in SendImage.iter_content():
                fd.write(chenk)
        reader = easyocr.Reader(['ch_sim','en']) # this needs to run only once to load the model into memory
        license_num = reader.readtext(path, detail = 0)
        license_num = ''.join(license_num)

        model = torch.hub.load('ultralytics/yolov5', 'custom', 'best.pt')
        results = model(path, size=640)  # includes NMS
        results = results.pandas().xyxy[0]['confidence'].to_numpy()
        try:
            prob = results[0]
        except:
            prob = 0
        print(results[0])
        time.sleep(10)
        reply_text = '車牌號碼: ' + license_num + '\n' + '是烏賊車的機率: ' + str(prob)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text = reply_text))


# run app
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5566)