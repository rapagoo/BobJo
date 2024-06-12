#!/usr/bin/python
# coding=utf-8

import sys
import sqlite3
import telepot
import requests
import xml.etree.ElementTree as ET
from datetime import date, datetime
import traceback

key = 'soQgOYvc8y5bv5jP8tIfni3Lrv4ZcDAk63zxA6k88sGR2vzdP0PhJy7%2FFRk%2FRiDA2OmsrOGcypnfZAglrz2wPQ%3D%3D'
TOKEN = '7120980199:AAHPYHAPiYCkKzyDnrChPquVpsyquT75GoA'
MAX_MSG_LENGTH = 300
baseurl = 'http://apis.data.go.kr/B552584/EvCharger/getChargerInfo?servicekey='+key
bot = telepot.Bot(TOKEN)

def fetch_data(zscode):
    params = {
        'serviceKey': 'soQgOYvc8y5bv5jP8tIfni3Lrv4ZcDAk63zxA6k88sGR2vzdP0PhJy7/FRk/RiDA2OmsrOGcypnfZAglrz2wPQ==',
        'pageNo': '1',
        'numOfRows': '30000',
        'zscode': zscode
    }

    response = requests.get(baseurl, params=params)
    root = ET.fromstring(response.content)

    data = {}
    for item in root.findall('.//item'):
        statId = item.find('statId').text if item.find('statId') is not None else ''
        if statId not in data:
            statNm = item.find('statNm').text if item.find('statNm') is not None else ''
            addr = item.find('addr').text if item.find('addr') is not None else ''
            location = item.find('location').text if item.find('location') is not None else ''
            useTime = item.find('useTime').text if item.find('useTime') is not None else ''
            busiNm = item.find('busiNm').text if item.find('busiNm') is not None else ''
            parkingFree = item.find('parkingFree').text if item.find('parkingFree') is not None else ''
            limitYn = item.find('limitYn').text if item.find('limitYn') is not None else ''
            limitDetail = item.find('limitDetail').text if item.find('limitDetail') is not None else ''

            parkingFree = "무료" if parkingFree == "Y" else "유료"
            limitYn = "이용자 제한 있음" if limitYn == "Y" else "이용자 제한 없음"

            data[
                statId] = f"충전소명: {statNm}, 주소: {addr}, 위치: {location}, 이용가능시간: {useTime}, 운영기관: {busiNm}, 주차료: {parkingFree}, 이용자 제한: {limitYn}, 제한 사유: {limitDetail}"

    return list(data.values())


def sendMessage(user, msg):
    try:
        bot.sendMessage(user, msg)
    except:
        traceback.print_exc(file=sys.stdout)