# coding=utf-8

import requests
from bs4 import BeautifulSoup
import json
import configparser
import os
import time
import datetime
import ctypes
import _tkinter
import tkinter
import gc
import threading


def getnotifyidlist():
    # Read config from file
    config = configparser.ConfigParser()
    configfile = 'config.ini'
    config.read(configfile, encoding='utf-8')
    notifyidlist_text = config.get('sseinfo', 'notifyidlist')
    notifyidlist = notifyidlist_text.split(',')
    return notifyidlist


def setlastnotifyid(notifyidlist):
    # Read config from file
    notifyidlisttext = ''
    config = configparser.ConfigParser()
    configfile = 'config.ini'
    config.read(configfile, encoding='utf-8')
    for notifyid in notifyidlist:
        notifyidlisttext = notifyidlisttext + notifyid + ','
    config.set('sseinfo', 'notifyidlist', notifyidlisttext)
    config.write(open(configfile, 'w'))


def getkeywordlist():
    # Read config from file
    config = configparser.ConfigParser()
    configfile = 'config.ini'
    config.read(configfile, encoding='utf-8')
    keywordlist_text = config.get('keyword', 'keyword')
    keywordlist = keywordlist_text.split(',')
    return keywordlist


# def postnotification(title, message):
#     toaster = ToastNotifier()
#     toaster.show_toast(title, message)


def message_box(title, msg):
    # 桌面弹出消息框
    # Python弹出MessageBox http://www.bubuko.com/infodetail-255690.html
    ctypes.windll.user32.MessageBoxW(0, msg, title, 1)


def processnewpost():
    main_url = "http://sns.sseinfo.com/"
    api_prefix = "ajax/feeds.do?"
    type_dict = [
        {
            'type': '10',
            'type_meaning': '问答'
        },
        {
            'type': '11',
            'type_meaning': '最新答复'
        },
        {
            'type': '20',
            'type_meaning': '观点'
        },
        {
            'type': '30',
            'type_meaning': '上市公司发布'
        },
        {
            'type': '40',
            'type_meaning': '上市公司公告'
        }
    ]
    # url = "http://sns.sseinfo.com/ajax/feeds.do?type=10&pageSize=10&lastid=-1&show=1&page=1"
    type_req = type_dict[1]['type']
    pageSize = '10'
    lastid = '-1'
    show = '1'
    page = '1'
    url = main_url + api_prefix + 'type=' + type_req + '&pageSize=' + pageSize + '&lastid=' + lastid \
        + '&show=' + show + '&page=' + page
    payload = {}
    headers = {
        # 'Cookie': 'SSESNSXMLSID=3dbbf719-ebc1-4a2c-9050-b1091be3edfd; JSESSIONID=2af40h5aylzt1qq2mqgaqlmwt'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    soup = BeautifulSoup(response.text.encode('utf8'), features="html5lib")
    response.close()
    # lastnotifyid = '619706'
    notifyidlist = getnotifyidlist()

    # if (type_req == '10'):
    #     questions = soup.find_all('div', class_='m_feed_txt')
    #     for question in questions:
    #         # print(question.attrs['id'])
    #         comment_id = question.attrs['id'].split('-')[1]
    #         gupiao = question.find('a')
    #         if gupiao != None:
    #             gupiao = gupiao.text.replace(':','').replace(')','')
    #         gupiao_name = gupiao.split("(")[0]
    #         gupiao_code = gupiao.split("(")[1]
    #         comment = str(question.contents).split('/a>, ')[1].replace(r'\n','').replace(r'\t','').replace(r'\'','').replace(']','')
    #         if (comment_id > lastnotifyid):
    #             print('ID: ' + comment_id)
    #             print(gupiao_code + " - " + gupiao_name + " - " + comment)
    #             # toaster = ToastNotifier()
    #             # toaster.show_toast(gupiao_name, gupiao_code + " - " + gupiao_name + " - " + comment)

    if (type_req == '11'):
        items = soup.find_all('div', class_='m_feed_item')
        id_list = []
        for item in items:
            m_feed_cnt = item.find('div', class_='m_feed_cnt')
            question_div = m_feed_cnt.find('div', class_='m_feed_txt')
            comment_id = question_div.attrs['id'].split('-')[1]
            id_list.append(comment_id)
            gupiao = question_div.find('a')
            if gupiao != None:
                gupiao = gupiao.text.replace(':', '').replace(')', '')
            gupiao_name = gupiao.split("(")[0]
            gupiao_code = gupiao.split("(")[1]
            question = str(question_div.contents).split(
                '/a>, ')[1].replace(r'\n', '').replace(r'\t', '').replace('\'', '').replace(']', '')

            # print(gupiao_code + " - " + gupiao_name + " - " + question)
            # toaster = ToastNotifier()
            # toaster.show_toast(gupiao_name, gupiao_code + " - " + gupiao_name + " - " + comment)

            m_qa = item.find('div', class_='m_qa')
            answer_div = m_qa.find('div', class_='m_feed_txt')
            answer = str(answer_div.contents).replace(r'\n', '').replace(
                r'\t', '').replace('\'', '').replace(']', '').replace('[', '')

            if (not comment_id in notifyidlist):
                print('ID: ' + comment_id +
                      datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                print(gupiao_code + " - " + gupiao_name)
                print('Question:' + question)
                print('Answer:' + answer)
                # postnotification(gupiao_code + " - " + gupiao_name,answer)
                if answer.find("is") == -1:
                    message_box(gupiao_code + " - " + gupiao_name,
                                "Ask: \n" + question + "\nAnswer: \n" + answer)
                notifyidlist.append(comment_id)

        setlastnotifyid(notifyidlist)
        gc.collect()


def keep_process():
    count = 1
    while (count <= 1000):
        print(count)
        processnewpost()
        time.sleep(3)
        count = count + 1


def process_threding(top, start_button):
    if (start_button['text'] == "Start"):
        x = threading.Thread(target=keep_process, name='scraper')
        x.daemon = True
        x.start()
        start_button['text'] = "Stop"
    else:
        top.destroy()


def main():
    top = tkinter.Tk()
    top.title("行情获取")
    top.iconbitmap('favicon.ico')
    top.geometry('200x100+100+100')
    start_button = tkinter.Button(
        top, text="Start", bg="lightblue", width=100, command=lambda: process_threding(top, start_button))
    # stop_button = tkinter.Button(
    #     top, text="Stop", bg="lightblue", width=100, command=top.destroy)
    start_button.pack()
    # stop_button.pack()
    top.mainloop()


if __name__ == '__main__':
    main()
