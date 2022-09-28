# -*- coding: utf-8 -*-
"""
Created on Sun Sep 25 19:05:21 2022

@author: YC
"""

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
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from parsel import Selector
import datetime
import re
import numpy as np
import pandas as pd
import os
import random
from flex import multi_flex
import time



#### scrap code #####
#### scrap code #####
# search results from google map
def scrapping(key_food, key_place1, key_place2) :
    # options setting
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
    url = 'https://www.google.com/maps/search/{0}/@{1},{2},14z'.format(key_food, key_place1, key_place2)
    driver.get(url)
    
    key_num = driver.find_elements(By.XPATH, '//div[contains(@aria-label, "Results for")]/div')[2].get_attribute('jstcache')
    script = '//div[@jstcache="{0}"]'.format(key_num)
    try:
        for i in range(5,20,3):
            last_review = driver.find_elements(By.XPATH, script)
            driver.execute_script('arguments[0].scrollIntoView(true);', last_review[i])
            time.sleep(2)
    except:
        pass    

    results = []

    for el in driver.find_elements(By.XPATH, '//div[contains(@aria-label, "Results for")]/div/div[./a]'):
        tep = el.find_element(By.XPATH, 'div//div[contains(@class, "UaQhfb fontBodyMedium")]//div[contains(@class, "W4Efsd")]/following::div//span[@jsan="0.aria-hidden"]/following::div').text.replace(" ","")
        title = el.find_element(By.XPATH, './a').get_attribute('aria-label')
        link = el.find_element(By.XPATH, './a').get_attribute('href')
        try:
            type_ = el.find_element(By.XPATH, 'div[contains(@class, "UaQhfb fontBodyMedium")]//div[contains(@class, "W4Efsd")]/following::div//span[text()="·"]/following::span').text
        except:
            type_ = None
        
        try: 
            rating = el.find_elements(By.XPATH, 'div//span[contains(@aria-hidden, "true")]')[0].text
        except:
            rating = None
        
        try:
            review = el.find_elements(By.XPATH, 'div//span[contains(@aria-hidden, "true")]')[1].text.replace("(", "").replace(")","")
        except:
            review = None
        
        try:
            service = [a.text for a in el.find_elements(By.XPATH, './/div[contains(@class, "ah5Ghc")]')]
            service = ' '.join(service)
        except:
            service = None
            
        try:
            address = el.find_element(By.XPATH, 'div//div[contains(@class, "UaQhfb fontBodyMedium")]//div[contains(@class, "W4Efsd")]/following::div//span[@jsan="0.aria-hidden"]/following::span').text
        except:
            address = None
        
        try: 
            status = tep.split("⋅")[0]
        except: 
            status = None
        
        try:
            nextOpenTime = tep.split("⋅")[1].split("·")[0]
        except:
            nextOpenTime = None
        
        try:
            phone = tep.split("⋅")[1].split("·")[1]
        except:
            phone = None
        
        try: 
            website = el.find_element(By.XPATH, '//a[@data-value="Website"]').get_attribute('href')
        except:
            website = None
        # driver2.get(url2)
        results.append({
            'title': title,
            'link': link,
            'type': type_ , 
            'rating': rating,
            'reviewsCount': review, 
            'service': service,
           'address': address,
            'status': status,
            'nextOpenTime': nextOpenTime,
            'phone': phone,
            'website': website
      
        })    
    try: 
        for a in results:
            url = 'https://www.google.com/search?q={0}+ +食記'.format(a['title'])
            driver.get(url)
            a.update({
                'blog_title': driver.find_element(By.XPATH, '//div[@class="yuRUbf"]/a/h3').text,
                'blog_link': driver.find_element(By.XPATH, '//div[@class="yuRUbf"]/a').get_attribute('href')
                })
    except:
        pass
    df = pd.DataFrame(results)
    return(df)
print(scrapping("錢都", 25.0594522, 121.5531985))

# search_result = [a['title'] for a in results]
    # picked_result = search_result[3]
    
    # url = 'https://www.google.com/search?q={0}+ +食記'.format(picked_result)
    # driver.get(url)
    # blog_results = []
    # for el in driver.find_elements(By.XPATH, '//div[@class="yuRUbf"]'):
    #     blog_results.append({
    #         'blog_title': el.find_element(By.XPATH, 'a/h3').text,
    #         'blog_link': el.find_element(By.XPATH, 'a').get_attribute('href')
    #     })


    #search_result = [a['title'] for a in results]
    #picked_result = search_result
    #target_url = [a['link'] for a in results if a['title'] == picked_result]
    #driver.get(target_url[0])
    #to refresh the browser
    #driver.refresh()

    # search results of related blogs
    #driver.quit()
    # return


# variable setting
category = ""
star = ""
takeout = ""
shownumber = ""
lat = ""
long = ""
fun = ""
rest = ""
default_cate = ["中式料理","日式料理","韓式料理","速食店","素食","飲料","飲料","咖啡廳","甜點","港式飲茶"]
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
    print(body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global category
    global star
    global takeout
    global shownumber
    global lat
    global long
    global category
    global fun
    message = event.message.text
    # First Filter : Food category
    # Click one action in the picture list at the bottom of line
    if bool(re.search("讓我選|來個驚喜", message)):
        # reset answer
        fun = event.message.text
        category, star, takeout, shownumber = "", "", "", ""
        quick_message = TextSendMessage(
        text = "請分享你現在的位置給我 :",
        quick_reply = QuickReply(items = [QuickReplyButton(action=LocationAction(label="傳送位置"))])
        )
        line_bot_api.reply_message(event.reply_token, quick_message)
    else :
        line_bot_api.reply_message(event.reply_token, TextSendMessage("不好意思，我不明白你說的話"))
# 處理位置資訊
@handler.add(MessageEvent, message=LocationMessage)
def handle_message(event):
    global address
    global lat
    global long
    address = event.message.address # 住址
    lat = event.message.latitude # latitude
    long = event.message.longitude # longitude
    quick_message = TextSendMessage(
        text = "請問你想要吃甚麼種類:",
        quick_reply = QuickReply(
            items = [
                QuickReplyButton(
                    action = PostbackAction(label = "日式料理", data = "A日式料理")),
                QuickReplyButton(
                    action = PostbackAction(label = "韓式料理", data = "A韓式料理")),
                QuickReplyButton(
                    action = PostbackAction(label = "中式料理", data = "A中式料理")),
                QuickReplyButton(
                    action = PostbackAction(label = "速食店", data = "A速食店")),
                QuickReplyButton(
                    action = PostbackAction(label = "速食店", data = "A速食店")),
                QuickReplyButton(
                    action = PostbackAction(label = "火鍋", data = "A火鍋")),
                 QuickReplyButton(
                    action = PostbackAction(label = "飲料", data = "A飲料")),
                  QuickReplyButton(
                    action = PostbackAction(label = "咖啡廳", data = "A咖啡廳")),
                QuickReplyButton(
                    action = PostbackAction(label = "隨便來個", data = "A隨便來個"))
                ])
        )
    line_bot_api.reply_message(event.reply_token, quick_message)
        
    
@handler.add(PostbackEvent)
def handle_message(event):
    # SET global varables
    global category
    global star
    global takeout
    global shownumber
    global default_cate
    global lat
    global long
    global fun
    global rest
    # set random number for random choice
    n_max = len(default_cate)
    ran_n = random.randint(0, n_max-1)
    data = event.postback.data
    # use if to differntiate response
    if data[0] == "A" :
        quick_message = TextSendMessage(
        text = "請問你想找幾星的餐廳:",
        quick_reply = QuickReply(
            items = [
                QuickReplyButton(
                    action = PostbackAction(label = "三星以上", data = "B三星以上")),
                QuickReplyButton(
                    action = PostbackAction(label = "四星以上", data = "B四星以上"))
                ])
        )
        # Store response
        if(data == "A隨便來個"):
            category = default_cate[ran_n]
        else :
            category = data[1:]
        # response another filter
        line_bot_api.reply_message(event.reply_token, quick_message)
    elif data[0] == "B" :
        # quick message
        quick_message = TextSendMessage(
        text = "請問你想外帶還是內用:",
        quick_reply = QuickReply(
            items = [
                QuickReplyButton(
                    action = PostbackAction(label = "內用", data = "C內用")),
                QuickReplyButton(
                    action = PostbackAction(label = "外帶", data = "C外帶")),
                QuickReplyButton(
                    action = PostbackAction(label = "可外送", data = "C可外送"))
                ])
        )
        # store response
        star = data[1:]
        # response antoher filter
        line_bot_api.reply_message(event.reply_token, quick_message)
    elif data[0] == "C" :
        # quick message
        quick_message = TextSendMessage(
        text = "你要顯示幾個結果:",
        quick_reply = QuickReply(
            items = [
                QuickReplyButton(
                    action = PostbackAction(label = "0~5", data = "D0~5", display_text = "請稍等", fill_in_text="請稍等...")),
                QuickReplyButton(
                    action = PostbackAction(label = "6~10", data = "D6~10", display_text = "請稍等", fill_in_text="請稍等..."))
                ])
        )
        # Sotre response
        takeout = data[1:]
        # response antoher filter
        line_bot_api.reply_message(event.reply_token, quick_message)
    elif data[0] == "D" : #顯示結果
        # Sotre response
        shownumber = data[1:]
        # Show results
        rest = scrapping(category, lat, long)
        if fun == "讓我選" :
            flex_message = FlexSendMessage(
                alt_text = "results",
                contents = multi_flex(rest))
            line_bot_api.reply_message(event.reply_token, flex_message)
            print(fun)
        elif fun == '來個驚喜' :
            poker_url_1 = "https://images.squarespace-cdn.com/content/v1/5abd8db4620b85fa99f15131/1542340370193-2M2GEBIZH1EOVZWXAL2R/Card+Back+2.0+-+Poker+Size+-+Blue_shw.png"
            poker_url_2 = "https://boardgames-bg.com/images/thumbnails/1001/1000/detailed/24/bicycle-prestige-100-plastic-poker-playing-card-deck-red-raider-back-usp1018425r-board-game-24268_yde4-zm.png"
            poker_url_2 = "https://i.pinimg.com/originals/8d/81/0e/8d810ebc5f83549e0dfc9caf65f12c60.png"
            image_message = TemplateSendMessage(
                alt_text = "results",
                template=ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url = poker_url_1,
                        action = URIAction(
                            label='選我選我',
                            uri= rest.loc[0, "link"]
                        )),
                    ImageCarouselColumn(
                        image_url = poker_url_2,
                        action = URIAction(
                            label='意想不到的驚喜',
                            uri= rest.loc[1, "link"]
                        )),
                    ImageCarouselColumn(
                        image_url = poker_url_2,
                        action = URIAction(
                            label='好膽你就來',
                            uri= rest.loc[2, "link"]
                        )),
                    ImageCarouselColumn(
                        image_url = poker_url_2,
                        action = URIAction(
                            label='何不問問神奇海螺',
                            uri= rest.loc[3, "link"]
                        )),
                    ImageCarouselColumn(
                        image_url = poker_url_2,
                        action = URIAction(
                            label='錯過會後悔',
                            uri= rest.loc[4, "link"]
                        ))
                    ]
                )
                )
            line_bot_api.reply_message(event.reply_token, image_message)
        print(category)
        print(lat)
        print(long)
        print(fun)
        
        
        
    # filt = ["種類", "星數", "內用/外帶", "顯示餐廳數"]
    # if data[0] == "A" :# 種類
    #     if(data == "A隨便來個"):
    #         category = default_cate[ran_n]
    #     else :
    #         category = data[1:]
        
    # elif data[0] == "B" : # 星
    #     star = data[1:]
    # elif data[0] == "C" : # 內用/外帶
    #     takeout = data[1:]
    # elif data[0] == "D" : # 數目
    #     shownumber = data[1:]
    
    # 回應文字
    # answer = pd.DataFrame({'answer' : [category, star, takeout, shownumber]})
    # missing = (answer['answer'].values == "").sum()
    # if all(answer['answer']) :
    #     message = "你已經全部選擇完畢 :\n種類 = {}\n星數 = {}\n內用/外帶 = {}\n顯示餐廳數 = {}".format(category, star, takeout, shownumber)
    #     confirm_template_message = TemplateSendMessage(
    #         alt_text = "Confirm filter",
    #         template = ConfirmTemplate(
    #         text = "{}\n請確認是否正確".format(message),
    #         actions = [
    #             MessageAction(
    #             label = '正確',
    #             text = '給我餐廳'),
    #             MessageAction(
    #             label = '再一次',
    #             text = '再一次')
    #         ])
    #     )
    #     line_bot_api.reply_message(event.reply_token, confirm_template_message)
    # elif not(all(answer['answer'])) :
    #     message = "你目前已選擇 :\n"
    #     pos = 0
    #     for answer in answer['answer']:
    #         if answer != "" :
    #             message = "%s%s: %s\n" % (message, filt[pos], answer)
    #             pos = pos + 1
    #         elif answer == "" :
    #             pos = pos + 1
    # message = message + "你還有%s項還沒有選擇"%(missing)
    # line_bot_api.reply_message(event.reply_token, TextSendMessage(message))    
        
    #print(event.message.type)
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
