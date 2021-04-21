import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import SsuncorpgroupItem
from itemloaders.processors import TakeFirst
import datetime

pattern = r'(\xa0)?'
base = 'https://www.suncorpgroup.com.au/news/news?year={}'

class SsuncorpgroupSpider(scrapy.Spider):
	name = 'suncorpgroup'
	now = datetime.datetime.now()
	year = now.year
	start_urls = ['https://www.suncorpgroup.com.au/news']

	def parse(self, response):
		post_links = response.xpath('//h3/a/@href').getall()
		for link in post_links:
			if not 'pdf' in link:
				yield response.follow(link, self.parse_post)

		next_page = response.xpath('//a[@rel="next"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)

		else:
			if self.year > 2018:
				self.year -= 1
				yield response.follow(base.format(self.year), self.parse)

	def parse_post(self, response):
		date = response.xpath('//time/text()').get()
		title = response.xpath('//h1/text()').get()
		content = response.xpath('//p[@class="lead color-grey"]//text()').getall() + response.xpath('(//section[@class="relative flex"])[position()<last()]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=SsuncorpgroupItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
