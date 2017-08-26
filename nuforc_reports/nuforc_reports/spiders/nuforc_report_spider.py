# -*- coding: utf-8 -*-
import scrapy


class NuforcReportSpiderSpider(scrapy.Spider):
    name = 'nuforc_report_spider'
    allowed_domains = ['http://www.nuforc.org/webreports/ndxevent.html']
    start_urls = ['http://http://www.nuforc.org/webreports/ndxevent.html/']

    def parse(self, response):
        pass
