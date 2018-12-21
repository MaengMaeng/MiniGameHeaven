# -*- coding: utf-8 -*-
import json
import os
import re
import urllib.request

from bs4 import BeautifulSoup
from slackclient import SlackClient
from flask import Flask, request, make_response, render_template

app = Flask(__name__)

slack_token = 'xoxb-506062083639-507463612610-XGpLz3HUZG47Sw1U4YQosCyB'
slack_client_id = '506062083639.507660839013'
slack_client_secret = '4573128035c6e79e6d7e6a9deea29edc'
slack_verification = '412BDhY0MC9xb9eE2MAPkRSj'
sc = SlackClient(slack_token)


# 크롤링 함수 구현하기
def _crawl_naver_keywords(texts):
    # 여기에 함수를 구현해봅시다.
    print("texts : " + texts)
    text = texts.replace('<@UEXDMJ0HY> ', '')

    keywords = []

    # text = "op.gg"
    if text.startswith("<@UEXDMJ0HY>"):
        keywords.append("◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇\n"
                        "◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇\n"
                        "◇◇◆◆◆◇◇◇◆◆◆◆◇◇◇◇◇◇◇◇◆◆◆◆◇◇◇◆◆◆◆◇\n"
                        "◇◆◇◇◇◆◇◇◆◇◇◇◆◇◇◇◇◇◇◆◇◇◇◆◇◇◆◇◇◇◆◇\n"
                        "◇◆◇◇◇◆◇◇◆◇◇◇◆◇◇◇◇◇◇◆◇◇◇◆◇◇◆◇◇◇◆◇\n"
                        "◇◆◇◇◇◆◇◇◆◇◇◇◆◇◇◇◇◇◇◆◇◇◇◆◇◇◆◇◇◇◆◇\n"
                        "◇◆◇◇◇◆◇◇◆◇◇◇◆◇◇◇◇◇◇◆◇◇◇◆◇◇◆◇◇◇◆◇\n"
                        "◇◆◇◇◇◆◇◇◆◇◇◇◆◇◇◇◇◇◇◇◆◆◆◆◇◇◇◆◆◆◆◇\n"
                        "◇◇◆◆◆◇◇◇◆◆◆◆◇◇◇◆◇◇◇◇◇◇◇◆◇◇◇◇◇◇◆◇\n"
                        "◇◇◇◇◇◇◇◇◆◇◇◇◇◇◇◆◇◇◇◆◇◇◇◆◇◇◆◇◇◇◆◇\n"
                        "◇◇◇◇◇◇◇◇◆◇◇◇◇◇◇◇◇◇◇◇◆◆◆◇◇◇◇◆◆◆◇◇\n"
                        "◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇")
    elif text.startswith("남궁명"):
        keywords.append("◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇\n◇◆◇◇◇◇◇◇◇◆◇◇◇◇◆◆◆◆◆◆◆◆◇◇◇◆◆◆◆◆◆◇◇◆◇◇\n◇◆◇◇◇◇◇◇◇◆◇◇◇◇◇◇◇◇◇◇◇◆◇◇◇◆◇◇◇◇◆◆◆◆◇◇\n◇◆◇◇◇◇◇◇◇◆◆◆◇◇◇◇◇◇◇◇◇◆◇◇◇◆◇◇◇◇◆◇◇◆◇◇\n◇◆◇◇◇◇◇◇◇◆◇◇◇◇◇◇◇◇◇◇◆◇◇◇◇◆◇◇◇◇◆◆◆◆◇◇\n◇◆◆◆◆◆◆◆◇◆◇◇◇◆◆◆◆◆◆◆◆◆◆◇◇◆◆◆◆◆◆◇◇◆◇◇\n◇◇◇◇◇◇◇◇◇◆◇◇◇◇◇◇◇◇◆◇◇◇◇◇◇◇◇◇◇◇◇◇◇◆◇◇\n◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◆◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇\n◇◇◆◆◆◆◆◆◆◆◇◇◇◇◇◆◆◆◆◆◆◇◇◇◇◇◇◆◆◆◆◆◆◇◇◇\n◇◇◆◇◇◇◇◇◇◆◇◇◇◇◆◇◇◇◇◇◇◆◇◇◇◇◆◇◇◇◇◇◇◆◇◇\n◇◇◆◇◇◇◇◇◇◆◇◇◇◇◆◇◇◇◇◇◇◆◇◇◇◇◆◇◇◇◇◇◇◆◇◇\n◇◇◆◆◆◆◆◆◆◆◇◇◇◇◇◆◆◆◆◆◆◇◇◇◇◇◇◆◆◆◆◆◆◇◇◇\n◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇")
    elif text.startswith("유현모"):
        keywords.append("◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇\n◇◇◇◆◆◆◆◆◆◇◇◇◇◇◆◆◆◇◇◇◇◆◇◇◇◇◆◆◆◆◆◆◆◆◇◇\n◇◇◆◇◇◇◇◇◇◆◇◇◇◇◇◇◇◇◇◇◇◆◇◇◇◇◆◇◇◇◇◇◇◆◇◇\n◇◇◆◇◇◇◇◇◇◆◇◇◆◆◆◆◆◆◆◇◇◆◇◇◇◇◆◇◇◇◇◇◇◆◇◇\n◇◇◆◇◇◇◇◇◇◆◇◇◇◇◆◇◆◇◇◆◆◆◇◇◇◇◆◇◇◇◇◇◇◆◇◇\n◇◇◇◆◆◆◆◆◆◇◇◇◇◆◇◇◇◆◇◇◇◆◇◇◇◇◆◇◇◇◇◇◇◆◇◇\n◇◇◇◇◇◇◇◇◇◇◇◇◇◆◇◇◇◆◇◆◆◆◇◇◇◇◆◆◆◆◆◆◆◆◇◇\n◇◇◇◇◇◇◇◇◇◇◇◇◇◇◆◆◆◇◇◇◇◆◇◇◇◇◇◇◇◇◆◇◇◇◇◇\n◇◆◆◆◆◆◆◆◆◆◆◇◇◇◇◇◇◇◇◇◇◆◇◇◇◇◇◇◇◇◆◇◇◇◇◇\n◇◇◇◆◇◇◇◇◆◇◇◇◇◇◆◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◆◇◇◇◇◇\n◇◇◇◆◇◇◇◇◆◇◇◇◇◇◆◇◇◇◇◇◇◇◇◇◇◆◆◆◆◆◆◆◆◆◆◇\n◇◇◇◆◇◇◇◇◆◇◇◇◇◇◆◆◆◆◆◆◆◆◇◇◇◇◇◇◇◇◇◇◇◇◇◇\n◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇")
    elif text.startswith("박창한"):
        keywords.append("◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇\n◇◆◇◇◇◇◆◇◇◆◇◇◇◇◇◆◆◆◇◇◇◆◇◇◇◇◆◆◆◇◇◇◇◆◇◇◇\n◇◆◇◇◇◇◆◇◇◆◇◇◇◇◇◇◇◇◇◇◇◆◇◇◇◇◇◇◇◇◇◇◇◆◇◇◇\n◇◆◆◆◆◆◆◇◇◆◇◇◇◆◆◆◆◆◆◆◇◆◆◆◆◆◆◆◆◆◆◇◇◆◇◇◇\n◇◆◇◇◇◇◆◇◇◆◆◆◇◇◇◇◆◇◇◇◇◆◇◇◇◇◆◇◆◇◇◇◇◆◆◆◇\n◇◆◇◇◇◇◆◇◇◆◇◇◇◇◇◆◇◆◇◇◇◆◇◇◇◆◇◇◇◆◇◇◇◆◇◇◇\n◇◆◆◆◆◆◆◇◇◆◇◇◇◆◆◇◇◇◆◆◇◆◇◇◇◆◇◇◇◆◇◇◇◆◇◇◇\n◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◆◇◇◇◇◆◆◆◇◇◇◇◆◇◇◇\n◇◇◆◆◆◆◆◆◆◆◇◇◇◇◇◆◆◆◆◆◆◇◇◇◇◇◇◇◇◇◇◇◇◆◇◇◇\n◇◇◇◇◇◇◇◇◇◆◇◇◇◇◆◇◇◇◇◇◇◆◇◇◇◇◆◇◇◇◇◇◇◇◇◇◇\n◇◇◇◇◇◇◇◇◇◆◇◇◇◇◆◇◇◇◇◇◇◆◇◇◇◇◆◇◇◇◇◇◇◇◇◇◇\n◇◇◇◇◇◇◇◇◇◆◇◇◇◇◇◆◆◆◆◆◆◇◇◇◇◇◆◆◆◆◆◆◆◆◇◇◇\n◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇")
    else:
        url = 'http://www.op.gg/summoner/userName=' + urllib.parse.quote_plus(text)
        req = urllib.request.Request(url)

        sourcecode = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(sourcecode, "html.parser")

        keywords.append(soup.find('span', class_="total").getText() + "전" +
                        soup.find('span', class_="win").getText() + "승" +
                        soup.find('span', class_="lose").getText() + "패")

        num = 1
        for i in soup.find_all('div', class_="ChampionBox Ranked"):
            keywords.append(str(num) + ". " + i.find('div', class_="ChampionName").getText().replace('\n', "").replace('\t', '') + ":" +
                            i.find('div', class_="Played").find_all('div')[0].getText().replace('\n', "").replace('\t',
                                                                                                                  '') +
                            "(" + i.find('div', class_="Played").find_all('div')[1].getText().replace('\n', "").replace(
                '\t', '') + ")"
                            + "\nK/D/A : " + i.find('div', class_="KDAEach").getText().replace('\n', "").replace('\t', ''))
            num += 1
    # 한글 지원을 위해 앞에 unicode u를 붙혀준다.
    return u'\n'.join(keywords)


# 이벤트 핸들하는 함수
def _event_handler(event_type, slack_event):
    print("user : " + slack_event["event"]['user'])

    if event_type == "app_mention":
        channel = slack_event["event"]["channel"]
        text = slack_event["event"]["text"]

        keywords = _crawl_naver_keywords(text)
        sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=keywords
        )

        return make_response("App mention message has been sent", 200, )

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})


@app.route("/listening", methods=["GET", "POST"])
def hears():
    slack_event = json.loads(request.data)

    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                                 "application/json"
                                                             })

    if slack_verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s" % (slack_event["token"])
        make_response(message, 403, {"X-Slack-No-Retry": 1})

    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        return _event_handler(event_type, slack_event)

    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})


@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"


# if __name__ == '__main__':
#     app.run('0.0.0.0', port=5000)
