#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from flask import Flask, request, abort

from linebot import (
        LineBotApi, WebhookHandler
)
from linebot.exceptions import (
        InvalidSignatureError
)
from linebot.models import *

# scrap package
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from parsel import Selector
import datetime
import re
#import time



#### scrap code #####
# search results from google map
def scrapping(key_word) :
    key_food = '火鍋106'
    key_place = key_word
    driver = webdriver.Chrome(ChromeDriverManager().install())
    url = 'https://www.google.com/maps/search/{0}+near+{1}'.format(key_food, key_place)
    driver.get(url)
    page_content = driver.page_source
    response = Selector(page_content)

    results = []

    for el in response.xpath('//div[contains(@aria-label, "的搜尋結果")]/div/div[./a]'):
        results.append({
            'link': el.xpath('./a/@href').extract_first(''),
            'title': el.xpath('./a/@aria-label').extract_first(''),
            'type': el.xpath('div//div[contains(@class, "UaQhfb fontBodyMedium")]//div[contains(@class, "W4Efsd")]/following::div//span[text()="·"]/following::span/text()').extract_first(),
            'rating': el.xpath('div//span[contains(@aria-hidden, "true")]/text()').extract_first(''),
            'reviewsCount': el.xpath('div//span[contains(@aria-hidden, "true")]/following::text()').extract_first(''),
            # 'service'
            # response.xpath('//div[contains(@aria-label, "的搜尋結果")]/div//div[contains(@class, "UaQhfb fontBodyMedium")]').extract_first('')
            'address': el.xpath('div//div[contains(@class, "UaQhfb fontBodyMedium")]//div[contains(@class, "W4Efsd")]/following::div//span[@jsan="0.aria-hidden"]/following::span/text()').extract_first(),
            'status': el.xpath('div//div[contains(@class, "UaQhfb fontBodyMedium")]//div[contains(@class, "W4Efsd")]/following::div[3]//span[text()="·"]/following::span/text()').extract_first(),
            'nextOpenTime': el.xpath('div//div[contains(@class, "UaQhfb fontBodyMedium")]//div[contains(@class, "W4Efsd")]/following::div[3]//span[text()="·"]/following::span[4]/text()').extract_first()
        })

    #print(results)

    search_result = [a['title'] for a in results]
    picked_result = search_result[3]
    #target_url = [a['link'] for a in results if a['title'] == picked_result]
    #driver.get(target_url[0])
    #to refresh the browser
    #driver.refresh()

    # search results of related blogs
    driver.quit()
    # return
    return(picked_result)


#### app
app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('MzvgoVaHfTUK+DnR87rdf1dGIFGZW7fgZvpdkxGmWzDkpD41ffYQKd1VTG7YQprU90boy+x+aS8bpu0WjrKcMkLm+bSq3U4BMD8yHmxUAucxKGAY0eQn4uG5sbvuc9J4xYtZUrX4jBf2b6lrZbO+YgdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('dc03f0c538f730509807c0065dac48cf')

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'
        

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = event.message.text
    # First Filter : Food category
    # Click one action in the picture list at the bottom of line
    if bool(re.match("隨機", message)) :
        carousel_message = TemplateSendMessage(
        alt_text = "food_category",
        template = CarouselTemplate(
        columns=[
            CarouselColumn(
            thumbnail_image_url = "https://www.iberdrola.com/documents/20125/39904/real_food_746x419.jpg", # thumbnail for the message
            title = "請問你想吃甚麼種類?",
            text = "請點選以下一個選項",
            actions = [
                MessageAction(
                label = "日式料理",
                text = "日式料理"),
                MessageAction(
                label = "韓式料理",
                text = "韓式料理"),
                MessageAction(
                label = "中式料理",
                text = "中式料理")
            ])
        ]))
        line_bot_api.reply_message(event.reply_token, carousel_message)
    # Second filter : stars
    # One variable from pervious filter needs to be record : food category
    elif bool(re.match("料理", message)): # if detect "料理"
        star = u'\u2B50'
        food_category = event.message.text
        carousel_message = TemplateSendMessage(
        alt_text = "star",
        template = CarouselTemplate(
        columns=[
            CarouselColumn(
            thumbnail_image_url = "https://www.iberdrola.com/documents/20125/39904/real_food_746x419.jpg", # thumbnail for the message
            title = "請問你想找幾星的餐廳?",
            text = "請點選以下一個選項",
            actions = [
                MessageAction(
                label = "0~2 " + star, # 0-2 stars
                text = "0~2 stars"),
                MessageAction(
                label = "2~3 " + star, # 2-3 stars
                text = "2~3 stars"),
                MessageAction(
                label = "3~4 " + star, # 3-4 stars
                text = "3~4 stars"),
                MessageAction(
                label = "4~5 " + star, # 4-5 stars
                text = "4~5 stars")
            ])
        ]))
        line_bot_api.reply_message(event.reply_token, carousel_message)
    # Third filter : take out / inside
    # One variable from pervious filter needs to be record : star
    elif bool(re.match("stars", message)): # if detect "star"
        stars = event.message.text
        carousel_message = TemplateSendMessage(
        alt_text = "takeout",
        template = CarouselTemplate(
        columns=[
            CarouselColumn(
            thumbnail_image_url = "https://www.iberdrola.com/documents/20125/39904/real_food_746x419.jpg", # thumbnail for the message
            title = "請問你想外帶還是內用?",
            text = "請點選以下一個選項",
            actions = [
                MessageAction(
                label = "內用", 
                text = "內用"),
                MessageAction(
                label = "外帶",
                text = "外帶")
            ])
        ]))
        line_bot_api.reply_message(event.reply_token, carousel_message)
    # forth filter : date
    # One variable from pervious filter needs to be record : takeout
    '''
    elif bool(re.match("內用|外帶", message)): # if detect "內用" or "外帶"
        takeout = event.message.text
        carousel_message = TemplateSendMessage(
        alt_text = "busy",
        template = CarouselTemplate(
        columns=[
            CarouselColumn(
            thumbnail_image_url = "https://www.iberdrola.com/documents/20125/39904/real_food_746x419.jpg", # thumbnail for the message
            title = "請問你想外帶還是內用?",
            text = "請點選以下一個選項",
            actions = [
                MessageAction(
                label = "內用", 
                text = "內用"),
                MessageAction(
                label = "外帶",
                text = "外帶")
            ])
        ]))
        line_bot_api.reply_message(event.reply_token, carousel_message) '''
    # five filter : display number
    # One variable from pervious filter needs to be record : date
    elif bool(re.match("內用|外帶", message)):
        time = str(datetime.date.today())
        carousel_message = TemplateSendMessage(
        alt_text = "display",
        template = CarouselTemplate(
        columns=[
            CarouselColumn(
            thumbnail_image_url = "https://www.iberdrola.com/documents/20125/39904/real_food_746x419.jpg",
            title = "你要顯示幾個結果?",#scrapping(event.message.text),
            text = "請點選以下一個選項",#scrapping(event.message.text),
            actions = [
                MessageAction(
                label = "0~5",
                text = "我要0~5個結果"),
                MessageAction(
                label = "6~10",
                text = "我要6~10個結果")
            ])
        ]))
        line_bot_api.reply_message(event.reply_token, carousel_message)
    # Showing results
    elif bool(re.match("結果" ,message)):
        carousel_message = TemplateSendMessage(
        alt_text = "results",
        template = CarouselTemplate(
        columns=[
            CarouselColumn(
            thumbnail_image_url = "https://www.iberdrola.com/documents/20125/39904/real_food_746x419.jpg",
            title = "台北市",#scrapping(event.message.text),
            text = "台北市",#scrapping(event.message.text),
            actions = [
                MessageAction(
                label = "台北市",
                text = "台北市"),
                MessageAction(
                label = "台北市",
                text = "台北市")
            ])
        ]))
        line_bot_api.reply_message(event.reply_token, carousel_message)
        
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
