import scrapy
import json

class TimelineSpider(scrapy.Spider):
    name = "timeline"

    def start_requests(self):
        urls = [
            'https://github.com/artemmikhalitsin'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        filename = 'timeline.txt'
        counts = response.css('rect.day::attr(data-count)').extract()
        dates = response.css('rect.day::attr(data-date)').extract()
        history = dict()
        for i in range(0, len(dates)):
            history[i] = {
                'Date': dates[i],
                'Counts': counts[i]
            }
        with open(filename, 'w') as f:
            json.dump(history, f)
