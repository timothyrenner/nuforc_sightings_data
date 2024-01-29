# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime

class NuforcReportSpider(scrapy.Spider):
    name = 'nuforc_report_spider'
    allowed_domains = ['www.nuforc.org', 'nuforc.org']
    start_urls = ['https://www.nuforc.org/ndx/?id=post']

    def __init__(self, start_date=None, stop_date=None, *args, **kwargs):
        self.start_date = \
            datetime.strptime(start_date, '%m/%d/%Y') \
            if start_date else None
        self.stop_date = \
            datetime.strptime(stop_date, '%m/%d/%Y') \
            if stop_date else None
        super(NuforcReportSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        
        table_links = response.xpath('//tr/td/u/a')
        for tl in table_links:
            # Guard against empty rows.
            if not tl: continue

            # Get a selector on the date text.
            link_date_selector = tl.xpath('./text()')
            
            # Skip out if it's unsuccessful.
            if not link_date_selector: continue

            # If that's extracted, parse and check the date.
            link_date = \
                datetime.strptime(link_date_selector.extract()[0], '%Y-%m-%d')
            # If link date is less than the start date, skip.
            if self.start_date and (link_date < self.start_date): continue

            # If link date is greater than or equal to the stop date, skip.
            if self.stop_date and (link_date >= self.stop_date): continue
            url = tl.xpath("@href").get()

            yield response.follow('https://nuforc.org' + url, self.parse_date_index)

    def parse_date_index(self, response):

        table_rows = response.xpath('//table/tbody/tr')
        
        # Each table row comes with structured summary information.
        # Extract this and pass it to the next request as metadata.
        for tr in table_rows:
            table_elements = tr.xpath('.//td')
            date_time_path = table_elements[1] \
                if len(table_elements) > 0 else None

            
            # If the date time path can't be extracted, skip this row.
            if not date_time_path: continue
            
            date_time = date_time_path.xpath('./text()').get() \
                if date_time_path else None

            report_link =  table_elements[0].xpath('./a/@href').get() \
                if table_elements[0] else None
            city = table_elements[2].xpath('./text()').extract() \
                if len(table_elements) > 1 else None
            state = table_elements[3].xpath('./text()').extract() \
                if len(table_elements) > 2 else None
            country = table_elements[4].xpath('./text()').extract() \
                if len(table_elements) > 3 else None
            shape = table_elements[5].xpath('./text()').extract() \
                if len(table_elements) > 4 else None
#            duration = table_elements[5].xpath('./text()').extract() \
#                if len(table_elements) > 5 else None
#            duration = 0
            summary = table_elements[6].xpath('./text()').extract() \
                if len(table_elements) > 5 else None
            posted = table_elements[8].xpath('./text()').extract() \
                if len(table_elements) > 7 else None

            # Passing the summary table contents as metadata so the report 
            # request has access.
            yield response.follow(
                report_link,
                self.parse_report_table,
                meta={
                    "report_summary": {
                        "date_time": date_time if date_time else None,
                        "report_link": f"http://www.nuforc.org{report_link}" if report_link else None, 
                        "city": city[0] if city else None,
                        "state": state[0] if state else None,
                        "country": country[0] if country else None,
                        "shape": shape[0] if shape else None,
 #                       "duration": duration[0] if duration else None,
                        "summary": summary[0] if summary else None,
                        "posted": posted[0] if posted else None
                    }
                }
            )

    def parse_report_table(self, response):

        #report is not a table anymore
        report_area = response.xpath('//div[contains(@class, "content-area clr")]')

        # The first row is a rehash (sort of) of the table summary.
        # Included for completeness.
        report_data = { k : v for k,v in zip([x.split(":")[0] for x in report_area.xpath('//div[contains(@class, "content-area clr")]//b/text()').getall()], \
                                     [x for x in [x.strip() for x in report_area.xpath('//div[contains(@class, "content-area clr")]/text()').getall()] if x != '']) }
        report_zip = zip([x.split(":")[0] for x in report_area.xpath('//div[contains(@class, "content-area clr")]//b/text()').getall()], \
                                     [x for x in [x.strip() for x in report_area.xpath('//div[contains(@class, "content-area clr")]/text()').getall()] if x != ''])
        report_text = " ".join([x.strip() for x in report_area.xpath('//div[contains(@class, "content-area clr")]/text()').getall()][9:])
        
        report_summary = response.meta["report_summary"]
    
        report = {
            "text"    : report_text,
            "duration": report_data["Duration"] if 'Duration' in report_data else None,
            "stats"   : "|".join([str(k)+":"+str(v) for k,v in report_zip]),
            **report_summary
        }

        yield report
