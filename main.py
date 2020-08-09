#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 YA-androidapp(https://github.com/YA-androidapp) All rights reserved.
# Required:
# $  pip install icrawler

from icrawler.builtin import BingImageCrawler
from PIL import Image
import cv2
import datetime
import glob
import imghdr
import numpy as np
import os
import re
import sys


nowstr = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
LOGFILEPATH = 'log_{}.txt'.format(nowstr)
LOGEXFILEPATH = 'logex_{}.txt'.format(nowstr)
DATAFILEPATH = 'q.txt'
IMAGEDIRPATH = 'images'
FACEIMAGEDIRPATH = 'images_face'

MAX_IMAGES_PER_PERSON = 100


HAARCASCADE_PATH = 'sources/data/haarcascades/haarcascade_frontalface_default.xml'


IMAGEDIRPATH = IMAGEDIRPATH if IMAGEDIRPATH.endswith(
    os.path.sep) else (IMAGEDIRPATH + os.path.sep)
FACEIMAGEDIRPATH = FACEIMAGEDIRPATH if FACEIMAGEDIRPATH.endswith(
    os.path.sep) else (FACEIMAGEDIRPATH + os.path.sep)


def imread2(filename, flags=cv2.IMREAD_COLOR, dtype=np.uint8):
    try:
        n = np.fromfile(filename, dtype)
        img = cv2.imdecode(n, flags)
        return img
    except Exception as e:
        print(e)
        return None


def imwrite2(filename, img, params=None):
    try:
        ext = os.path.splitext(filename)[1]
        result, n = cv2.imencode(ext, img, params)

        if result:
            with open(filename, mode='w+b') as f:
                n.tofile(f)
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False


def checkDir():
    # IMAGEDIRPATH
    if os.path.exists(IMAGEDIRPATH):
        nowstr = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        os.rename(os.path.dirname(IMAGEDIRPATH), os.path.dirname(
            IMAGEDIRPATH) + '_' + nowstr + '.bak')
    os.makedirs(IMAGEDIRPATH, exist_ok=True)

    # FACEIMAGEDIRPATH
    if os.path.exists(FACEIMAGEDIRPATH):
        nowstr = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        os.rename(os.path.dirname(FACEIMAGEDIRPATH), os.path.dirname(
            FACEIMAGEDIRPATH) + '_' + nowstr + '.bak')
    os.makedirs(FACEIMAGEDIRPATH, exist_ok=True)


def collect():
    with open(DATAFILEPATH, 'r', encoding='utf-8') as f:
        i = 0
        for line in f:
            keyword = re.sub(r'[\\|/|:|?|.|\'|<|>|\|]', '-',
                             line.strip().replace(' ', '').replace('　', ''))
            dname = '{:03}_{}'.format(i, keyword)
            print(dname)
            dpath = os.path.join(IMAGEDIRPATH, dname)
            os.makedirs(dpath, exist_ok=True)

            crawler = BingImageCrawler(storage={'root_dir': dpath})
            crawler.crawl(keyword=keyword, max_num=MAX_IMAGES_PER_PERSON)

            i += 1


def filter():
    dirs = glob.glob(os.path.join(IMAGEDIRPATH, '**' + os.sep), recursive=True)
    # print(dirs) # ['images/', 'images/AAA/', 'images/BBB/', 'images/CCC/', 'images/DDD/', 'images/EEE/']
    for dir in dirs:
        if os.path.basename(os.path.dirname(dir)) == os.path.basename(os.path.dirname(IMAGEDIRPATH)):
            continue
        actress = os.path.basename(os.path.dirname(dir))
        print('actress: {}'.format(actress, datetime.datetime.now().strftime(
            '%Y/%m/%d %H:%M:%S')))

        # 出力先
        mvdir = os.path.join(FACEIMAGEDIRPATH, actress)
        os.makedirs(mvdir, exist_ok=True)

        # 移動し得るファイルを検索
        files = glob.glob(os.path.join(dir, '?*.???*'),
                          recursive=True)  # 拡張子3文字以上のファイル
        # print(files) # ['images/EEE/000001.jpg', 'images/EEE/000002.jpg', 'images/EEE/000003.jpg', 'images/EEE/000173.jpg']]
        for file in files:
            imgType = imghdr.what(file)
            print('\t{} {} {}'.format(file, imgType, datetime.datetime.now().strftime(
                '%Y/%m/%d %H:%M:%S')))
            if imgType is None:
                pass
            elif any(map(imgType.__contains__, ('bmp', 'jpeg', 'png'))):  # 対応する形式の画像ファイルか判定
                detectFace(file)
            elif imgType == 'gif':
                newfile = os.path.splitext(file)[0]+'.png'
                newimg = Image.open(file).convert('RGB').save(newfile)
                if newimg is not None:
                    detectFace(newfile)


def detectFace(file):
    src = imread2(file)
    if file is not None:
        src_gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        print('\t{} src_gray {}'.format(file, datetime.datetime.now().strftime(
            '%Y/%m/%d %H:%M:%S')))
        faces = faceCascadeClassifier.detectMultiScale(src_gray)
        print('\t{} faces {}'.format(file, datetime.datetime.now().strftime(
            '%Y/%m/%d %H:%M:%S')))
        for x, y, w, h in faces:
            try:
                face = src[y: y + h, x: x + w]

                actress = os.path.basename(os.path.dirname(file))
                mvdir = os.path.join(FACEIMAGEDIRPATH, actress)
                filesplt = os.path.splitext(os.path.basename(file))
                facefile = os.path.join(
                    mvdir, filesplt[0] + '_{:04}-{:04}-{:04}-{:04}'.format(y, y + h, x, x + w) + filesplt[1])
                print('\tfacefile: {} {}'.format(facefile, datetime.datetime.now().strftime(
                    '%Y/%m/%d %H:%M:%S')))
                imwrite2(facefile, face)
            except Exception as e:
                with open(LOGEXFILEPATH, 'a', encoding='utf-8') as logfile:
                    print('Exception: {} {}'.format(e, datetime.datetime.now().strftime(
                        '%Y/%m/%d %H:%M:%S')), file=logfile, flush=True)


if __name__ == '__main__':
    try:
        sys.stdout = open(LOGFILEPATH, 'a', encoding='utf-8')

        # checkDir()
        # collect()

        faceCascadeClassifier = cv2.CascadeClassifier(HAARCASCADE_PATH)
        filter()
    except Exception as e:
        with open(LOGEXFILEPATH, 'a', encoding='utf-8') as logfile:
            print('Exception: {} {}'.format(e, datetime.datetime.now().strftime(
                '%Y/%m/%d %H:%M:%S')), file=logfile, flush=True)
    finally:
        sys.stdout.close()
        sys.stdout = sys.__stdout__
        pass
