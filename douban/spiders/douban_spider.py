# -*- coding: utf-8 -*-
import scrapy
from douban.items import DoubanItem
from pyquery import PyQuery

class DoubanSpiderSpider(scrapy.Spider):
    # 这里是爬虫名
    name = 'douban_spider'
    # 允许的域名
    allowed_domains = ['weapon.huanqiu.com']
    # 入口url，扔到调度器
    # start_urls = ['http://weapon.huanqiu.com/weaponlist/aircraft']
    base_site = 'http://weapon.huanqiu.com'
    # start_urls = ['http://weapon.huanqiu.com/weaponlist/aircraft']
    start_urls = ['http://weapon.huanqiu.com/weaponlist']

    def parse(self, response):
        urls = response.xpath("//div[@class='weaponWarp']//div[@class='classList clearfix']//div[@class='side']//div[@class='sideNav']/ul/li/a/@href").extract()

        # for url in urls[:-1]:
        #     url = self.base_site + url
        #     yield scrapy.Request(url, meta={'download_timeout': 3}, callback=self.parseType, dont_filter=False)

        # 测试每一个类型 总共8种 0-7
        url = self.base_site + urls[1]
        yield scrapy.Request(url, meta={'download_timeout': 1}, callback=self.parseType, dont_filter=False)

    def parseType(self, response):
        # 将每种武器第一层12个遍历
        des_urls = response.xpath("//div[@class='weaponWarp']//div[@class='classList clearfix']//div[@class='conMain']//div[@class='module']//div[@class='picList']/ul/li/span[@class='name']/a/@href").extract()

        for des_url in des_urls:
            url = self.base_site + des_url
            yield scrapy.Request(url, meta={'download_timeout': 1}, callback=self.getInfo, dont_filter=False)

        # 测试单个页面
        # start_urls = 'http://weapon.huanqiu.com/v350'
        # yield scrapy.Request(start_urls, callback=self.getInfo)

        # 爬取下一页内容 使用
        page = 1
        while(page <= 111):
            next_page_url = self.base_site + "/weaponlist/guns/list_0_0_0_0_" + str(page)
            yield scrapy.Request(next_page_url, meta={'download_timeout': 1}, callback=self.parseType, dont_filter=False)
            page = page + 1

        # 爬取下一页内容 备用
        # next_page_url = self.base_site + response.xpath("//div[@class='weaponWarp']//div[@class='classList clearfix']//div[@class='conMain']//div[@class='module']//div[@class='pages']/a[last()]/@href").extract()[0]
        #
        # if next_page_url != "javascript:;":
        #     yield scrapy.Request(next_page_url, callback=self.parseType)

    def getInfo(self, response):
        # 先爬取一页
        douban_item = DoubanItem()

        # 类型
        type = response.xpath("//div[@class='weaponWarp']//div[@class='breadcrumb']//a[last()]/text()").extract()[0]
        douban_item['type'] = type

        # 名称 & 国家 & 图片
        # 如果有大图
        pic_list1 = response.xpath("//div[@class='weaponWarp']//div[@class='detail clearfix']//div[@class='conMain']//div[@class='maxPic']")
        if pic_list1:
            douban_item['name'] = pic_list1.xpath(".//span[@class='name']/text()").extract()[0]
            print(douban_item['name'])
            douban_item['country'] = pic_list1.xpath(".//span[@class='country']/b/a/text()").extract()[0]
            douban_item['image_url'] = pic_list1.xpath("./img/@src").extract()
            douban_item['image_name'] = pic_list1.xpath("./img/@src").extract()[0].split('/')[-1]

            # 介绍
            introduce_list = response.xpath(
                "//div[@class='weaponWarp']//div[@class='detail clearfix']//div[@class='conMain']//div[@class='intron']//div[@class='module']")

            introduce_text = introduce_list.extract()[0].strip()
            introduce_text = PyQuery(introduce_text)
            introduce_temp = str(introduce_text.text())
            douban_item['introduce'] = introduce_temp

        # 如果没有大图
        pic_list2 = response.xpath("//div[@class='weaponWarp']//div[@class='detail clearfix']//div[@class='conMain']//div[@class='maxNoPic']")
        if pic_list2:
            douban_item['name'] = pic_list2.xpath(".//span[@class='name']/text()").extract()[0]
            print(douban_item['name'])
            douban_item['country'] = pic_list2.xpath(".//span[@class='country']/b/a/text()").extract()[0]
            pic_small = response.xpath("//div[@class='weaponWarp']//div[@class='detail clearfix']//div[@class='side']//div[@class='dataInfo']/img/@src")
            # 特殊武器的小图
            # pic_small = response.xpath("//div[@class='weaponWarp']//div[@class='side']//div[@class='dataInfo']/img/@src")
            # 如果有小图
            if pic_small:
                douban_item['image_url'] = pic_small.extract()
                douban_item['image_name'] = pic_small.extract()[0].split('/')[-1]

            # 介绍
            introduce_list = response.xpath(
                "//div[@class='weaponWarp']//div[@class='detail clearfix']//div[@class='conMain']//div[@class='intron']/div[@class='module']").extract()[0].strip()
            introduce_temp = PyQuery(introduce_list)
            introduce_temp = str(introduce_temp.text().split('\n')[1])
            douban_item['introduce'] = introduce_temp

        # 详情
        describe_list = response.xpath(
            "//div[@class='weaponWarp']//div[@class='detail clearfix']//div[@class='conMain']//div[@class='info']//div[@class='module']//div[@class='otherList']")
        # 如果有详情
        if describe_list:
            douban_item['describe'] = {}
            for i_describe in describe_list:
                left = str(i_describe.xpath("./h3/text()").extract()[0])

                right_list1 = i_describe.xpath("./div")
                right_text = right_list1.extract()[0].strip()
                right = PyQuery(right_text)
                right = str(right.text())

                douban_item['describe'][left] = right

        # 武器详细参数
        parameters_list = response.xpath("//div[@class='weaponWarp']//div[@class='detail clearfix']//div[@class='side']//div[@class='dataInfo']")
        # 特殊武器详细参数
        # parameters_list = response.xpath("//div[@class='weaponWarp']//div[@class='side']//div[@class='dataInfo']")
        if parameters_list:
            douban_item['parameters'] = {}
            h4 = parameters_list.xpath("./h4[not(contains(@class,'typeTitle'))]")
            h4_num = len(h4.extract())
            ul = parameters_list.xpath("./ul")
            ul_num = len(ul.extract())
            if ul_num - h4_num == 1:
                basic = {}
                parameter_list = parameters_list.xpath("./ul[1]/li")
                if parameter_list:
                    for i_parameter in parameter_list:
                        left = str(i_parameter.xpath("./span/text()").extract()[0]).replace("：", "")
                        right = str(i_parameter.xpath("./text()").extract()[0])
                        basic[left] = right
                    douban_item['parameters']['basic'] = basic
                if h4_num > 0:
                    for i in range(1, ul_num):
                        left = str(parameters_list.xpath("./h4[not(contains(@class,'typeTitle'))][%d]/text()" % i).extract()[0])

                        weapon_list = parameters_list.xpath(".//ul[contains(@class,'multiList')]")
                        # 如果没有“武器装备”这一类型
                        if not weapon_list:
                            # print("2", left)
                            right = {}
                            right_url_list = parameters_list.xpath("./ul[%d]/li" % (i + 1))

                            for i_parameter in right_url_list:
                                if i_parameter:
                                    left_second = str(i_parameter.xpath("./span/text()").extract()[0]).replace("：", "")
                                    if i_parameter.xpath("./b"):
                                        right_second = str(i_parameter.xpath("./b/text()").extract()[0])
                                    else:
                                        right_second = str(i_parameter.xpath("./text()").extract()[0])
                                    right[left_second] = right_second
                        else:
                            local_url = parameters_list.xpath("./ul[%d]" % (i+1))
                            ## 如果有武器装备这一类型，而且这个就是
                            if local_url.extract()[0] in weapon_list.extract():
                                # print("1", left)
                                right = ""
                                for i in local_url.xpath("./li/text()"):
                                    right = right + i.extract()
                            ## 如果有武器装备这一类型，而且这个不是
                            else:
                                # print("2", left)
                                right = {}
                                right_url_list = parameters_list.xpath("./ul[%d]/li" % (i+1))

                                for i_parameter in right_url_list:
                                    if i_parameter:
                                        left_second = str(i_parameter.xpath("./span/text()").extract()[0]).replace("：", "")
                                        if i_parameter.xpath("./b"):
                                            right_second = str(i_parameter.xpath("./b/text()").extract()[0])
                                        else:
                                            right_second = str(i_parameter.xpath("./text()").extract()[0])
                                        right[left_second] = right_second
                        douban_item['parameters'][left] = right

        # 相关推荐
        recommend_list = response.xpath(
            "//div[@class='weaponWarp']//div[@class='detail clearfix']//div[@class='conMain']//div[@class='tuijian']//div[@class='module']//div[@class='pic_recommend']/ul/li/span[@class='name']/a/text()")

        # 特殊武器的推荐
        # recommend_list = response.xpath(
        #     "//div[@class='weaponWarp']//div[@class='detail clearfix']//div[@class='tuijian']//div[@class='module']//div[@class='pic_recommend']/ul/li/span[@class='name']/a/text()")
        recommend_temp = []
        for i in recommend_list:
            recommend_temp.append(i.extract())
        douban_item['recommend'] = recommend_temp

        yield douban_item


        # # 参数信息
        # parameter_list = response.xpath(
        #     "//div[@class='weaponWarp']//div[@class='detail clearfix']//div[@class='side']//div[@class='dataInfo']/ul[1]/li")
        # douban_item['parameter'] = {}
        # for i_parameter in parameter_list:
        #     left = str(i_parameter.xpath("./span/text()").extract()[0]).replace("：", "")
        #     right = str(i_parameter.xpath("./text()").extract()[0])
        #
        #     # i_parameter_content = dict({left: right})
        #     # douban_item['parameter'].append(i_parameter_content)
        #     douban_item['parameter'][left] = right

        # # 武器装备
        # weaponry_url = response.xpath(
        #     "//div[@class='weaponWarp']//div[@class='detail clearfix']//div[@class='side']//div[@class='dataInfo']/ul[@class='multiList']")
        # # 如果有武器装备
        # if weaponry_url:
        #     weaponry = ""
        #     for i in weaponry_url.xpath("./li/text()"):
        #         weaponry = weaponry + i.extract()
        #         douban_item['weaponry'] = weaponry




        # # 技术数据
        # technical_data_list = response.xpath(
        #     "//div[@class='weaponWarp']//div[@class='detail clearfix']//div[@class='side']//div[@class='dataInfo']/ul[@class='dataList'][1]/li")
        # # 如果有技术数据
        # if technical_data_list:
        #     douban_item['technical_data'] = {}
        #     for i_parameter in technical_data_list:
        #         left = str(i_parameter.xpath("./span/text()").extract()[0]).replace("：", "")
        #         if i_parameter.xpath("./b"):
        #             right = str(i_parameter.xpath("./b/text()").extract()[0])
        #         else:
        #             right = str(i_parameter.xpath("./text()").extract()[0])
        #         # i_parameter_content = dict({left: right})
        #         # douban_item['technical_data'].append(i_parameter_content)
        #         douban_item['technical_data'][left] = right
        #
        # # 性能数据、弹药参数（火炮） Ammunition_parameters
        # Ammunition_parameters_list = response.xpath(
        #     "//div[@class='weaponWarp']//div[@class='detail clearfix']//div[@class='side']//div[@class='dataInfo']/ul[@class='dataList'][2]/li")
        # # 如果有性能数据
        # if Ammunition_parameters_list:
        #     douban_item['Ammunition_parameters'] = {}
        #     for i_parameter in Ammunition_parameters_list:
        #         left = str(i_parameter.xpath("./span/text()").extract()[0]).replace("：", "")
        #         if i_parameter.xpath("./b"):
        #             right = str(i_parameter.xpath("./b/text()").extract()[0])
        #         else:
        #             right = str(i_parameter.xpath("./text()").extract()[0])
        #         # i_parameter_content = dict({left: right})
        #         # douban_item['performance_data'].append(i_parameter_content)
        #         douban_item['Ammunition_parameters'][left] = right