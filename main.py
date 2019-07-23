#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 YA-androidapp(https://github.com/YA-androidapp) All rights reserved.
# Required:
# $  pip install icrawler

from icrawler.builtin import GoogleImageCrawler
import cv2
import datetime
import glob
import imghdr
import os
import re


DATAFILEPATH = 'q.txt'
IMAGEDIRPATH = 'images'
FACEIMAGEDIRPATH = 'images_face'


HAARCASCADE_PATH = 'sources/data/haarcascades/haarcascade_frontalface_default.xml'


IMAGEDIRPATH = IMAGEDIRPATH if IMAGEDIRPATH.endswith(os.path.sep) else (IMAGEDIRPATH + os.path.sep)
FACEIMAGEDIRPATH = FACEIMAGEDIRPATH if FACEIMAGEDIRPATH.endswith(os.path.sep) else (FACEIMAGEDIRPATH + os.path.sep)


def checkDir():
    # IMAGEDIRPATH
    if os.path.exists(IMAGEDIRPATH):
        nowstr = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        os.rename(os.path.dirname(IMAGEDIRPATH), os.path.dirname(IMAGEDIRPATH) + '_' + nowstr + '.bak')
    os.makedirs(IMAGEDIRPATH, exist_ok=True)

    # FACEIMAGEDIRPATH
    if os.path.exists(FACEIMAGEDIRPATH):
        nowstr = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        os.rename(os.path.dirname(FACEIMAGEDIRPATH), os.path.dirname(FACEIMAGEDIRPATH) + '_' + nowstr + '.bak')
    os.makedirs(FACEIMAGEDIRPATH, exist_ok=True)


def collect():
    with open(DATAFILEPATH) as f:
        for line in f:
            keyword = line.strip().replace(' ', '').replace('　', '')
            print(keyword)

            dname = re.sub(r'[\\|/|:|?|.|\'|<|>|\|]', '-', keyword)
            dpath = os.path.join(IMAGEDIRPATH, dname)
            os.makedirs(dpath, exist_ok=True)

            crawler = GoogleImageCrawler(storage={'root_dir': dpath})
            crawler.crawl(keyword=keyword, max_num=200)


def filter():
    dirs = glob.glob(os.path.join(IMAGEDIRPATH, '**' + os.sep), recursive=True)
    # print(dirs) # ['images/', 'images/AAA/', 'images/BBB/', 'images/CCC/', 'images/DDD/', 'images/EEE/']
    for dir in dirs:
        if os.path.basename(os.path.dirname(dir)) == os.path.basename(os.path.dirname(IMAGEDIRPATH)):
            continue
        actress = os.path.basename(os.path.dirname(dir))
        print('actress: ' + actress)

        # 出力先
        mvdir = os.path.join(FACEIMAGEDIRPATH, actress)
        os.makedirs(mvdir, exist_ok=True)

        # 移動し得るファイルを検索
        files = glob.glob(os.path.join(dir, '?*.???*'), recursive=True) # 拡張子3文字以上のファイル
        # print(files) # ['images/EEE/000001.jpg', 'images/EEE/000002.jpg', 'images/EEE/000003.jpg', 'images/EEE/000173.jpg']]
        for file in files:
            if imghdr.what(file) is not None: # 画像ファイルか判定
                detectFace(file)


def detectFace(file):
    src = cv2.imread(file)
    src_gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    faces = faceCascadeClassifier.detectMultiScale(src_gray)
    for x, y, w, h in faces:
        face = src[y: y + h, x: x + w]

        actress = os.path.basename(os.path.dirname(file))
        mvdir = os.path.join(FACEIMAGEDIRPATH, actress)
        filesplt = os.path.splitext(os.path.basename(file))
        facefile = os.path.join(mvdir, filesplt[0] + '_{:04}-{:04}-{:04}-{:04}'.format(y, y + h, x, x + w) + filesplt[1])
        print('facefile: ' + facefile)
        cv2.imwrite(facefile, face)


if __name__ == '__main__':
    checkDir()
    collect()

    faceCascadeClassifier = cv2.CascadeClassifier(HAARCASCADE_PATH)
    filter()
