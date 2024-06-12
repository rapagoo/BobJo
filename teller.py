#!/usr/bin/python
# coding=utf-8

import sys
import time
import telepot
from pprint import pprint
from datetime import date
import traceback

import noti

# 각 사용자별로 요청한 데이터 인덱스를 관리하기 위한 사전
user_data = {}

# 시/군 코드 매핑
zscode_map = {
    "수원시": "41110",
    "성남시": "41130",
    "의정부시": "41150",
    "안양시": "41170",
    "부천시": "41190",
    "광명시": "41210",
    "평택시": "41220",
    "동두천시": "41250",
    "안산시": "41270",
    "고양시": "41280",
    "과천시": "41290",
    "구리시": "41310",
    "남양주시": "41360",
    "오산시": "41370",
    "시흥시": "41390",
    "군포시": "41410",
    "의왕시": "41430",
    "하남시": "41450",
    "용인시": "41460",
    "파주시": "41480",
    "이천시": "41500",
    "안성시": "41550",
    "김포시": "41570",
    "화성시": "41590",
    "광주시": "41610",
    "양주시": "41630",
    "포천시": "41650",
    "여주시": "41670",
    "연천군": "41800",
    "가평군": "41820",
    "양평군": "41830"
}

def replyChargerData(user, loc_param, start_idx=0):
    if user not in user_data:
        user_data[user] = {
            "data": noti.fetch_data(loc_param),
            "index": 0,
            "loc_param": loc_param
        }

    data = user_data[user]["data"]
    index = user_data[user]["index"]

    if index >= len(data):
        noti.sendMessage(user, '더 이상 데이터가 없습니다.')
        return

    end_idx = index + 10
    res_list = data[index:end_idx]
    msg = '\n\n'.join(res_list)
    noti.sendMessage(user, msg)

    user_data[user]["index"] = end_idx

def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type != 'text':
        noti.sendMessage(chat_id, '난 텍스트 이외의 메시지는 처리하지 못해요.')
        return

    text = msg['text']
    args = text.split()

    if len(args) == 2 and args[0] == '지역':
        loc_param = zscode_map.get(args[1])
        if not loc_param:
            noti.sendMessage(chat_id, '올바른 지역명을 입력하세요. 예: "지역 수원시"')
            return
        replyChargerData(chat_id, loc_param)
    elif text == '계속':
        if chat_id not in user_data:
            noti.sendMessage(chat_id, '먼저 지역명을 입력하세요. 예: "지역 수원시"')
            return
        replyChargerData(chat_id, user_data[chat_id]["loc_param"], user_data[chat_id]["index"])
    else:
        noti.sendMessage(chat_id, '모르는 명령어입니다.\n"지역 [지역명]", "계속" 중 하나의 명령을 입력하세요.')

today = date.today()
current_month = today.strftime('%Y%m')

print(f'[ {today} ] received token : {noti.TOKEN}')

bot = telepot.Bot(noti.TOKEN)
pprint(bot.getMe())

bot.message_loop(handle)

print('Listening...')

while 1:
    time.sleep(10)
