# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item,Field


class DoubanItem(Item):
    # define the fields for your item here like:

    # 类型
    type = Field()
    # 名称 ok
    name = Field()
    # 国家 ok
    country = Field()
    # 介绍 ok
    introduce = Field()
    # 详情 ok
    describe = Field()
    # 装备参数
    parameters = Field()
    # 推荐 ok
    recommend = Field()
    # 图片
    image_url = Field()
    image_name = Field()

    # 参数 ok
    # parameter = Field()
    # 武器装备 ok
    # weaponry = Field()
    # 技术数据 ok
    # technical_data = Field()
    # 性能数据 ok
    # performance_data = Field()

