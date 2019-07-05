# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy import signals
import json,os
import codecs
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
from scrapy import Request,log
from douban.settings import IMAGES_STORE as IMGS

class MyspiderPipeline(object):
    def __init__(self):
        self.file = codecs.open('data_except.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) +"\n"
        self.file.write(line)
        return item

    def spider_closed(self, spider):
        self.file.close()


class DoubanImgDownloadPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        for url in item['image_url']:
            yield Request(url)
    def item_completed(self, results, item, info):
        os.rename(IMGS + '/' + results[0][1]['path'], IMGS + '/full/' + item['image_name'])
