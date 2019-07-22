#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 YA-androidapp(https://github.com/YA-androidapp) All rights reserved.
# Required:
# $  pip install icrawler

from icrawler.builtin import GoogleImageCrawler
import datetime
import os
import re


DATAFILEPATH = 'q.txt'
IMAGEDIRPATH = 'images'


def main():
    if os.path.exists(IMAGEDIRPATH):
        nowstr = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        os.rename(IMAGEDIRPATH, IMAGEDIRPATH + '_' + nowstr + '.bak')
    os.makedirs(IMAGEDIRPATH, exist_ok=True)

    with open(DATAFILEPATH) as f:
        for line in f:
            keyword = line.strip().replace(' ', '').replace('　', '')
            print(keyword)

            dname = re.sub(r'[\\|/|:|?|.|\'|<|>|\|]', '-', keyword)
            dpath = os.path.join(IMAGEDIRPATH, dname)
            os.makedirs(dpath, exist_ok=True)

            # crawler = GoogleImageCrawler(storage={'root_dir': dpath})
            # crawler.crawl(keyword=keyword, max_num=100)


if __name__ == '__main__':
    main()