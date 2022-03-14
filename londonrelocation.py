import scrapy
from scrapy import Request
from scrapy.loader import ItemLoader
from property import Property


class LondonrelocationSpider(scrapy.Spider):
    name = 'londonrelocation'
    allowed_domains = ['londonrelocation.com']
    start_urls = ['https://londonrelocation.com/properties-to-rent/']

    def parse(self, response):
        for start_url in self.start_urls:
            yield Request(url=start_url, callback=self.parse_area)

    def parse_area(self, response):
        area_urls = response.xpath('.//div[contains(@class,"area-box-pdh")]//h4/a/@href').extract()
        for area_url in area_urls:
            yield Request(url=area_url, callback=self.parse_area_pages)

    def parse_area_pages(self, response):
        # Write your code here and remove `pass` in the following line
        
        pages_urls = response.css("div.pagination-wrap div.pagination ul li a::attr(href)").extract()[:2]
        # parsing each paginated page inside the area
        for page in pages_urls:
            yield Request(url=page, callback=self.parse_one_page)

    def parse_one_page(self, page):
            
            # selecting the main div of the flats inside the page
            flats = page.css("div.right-cont")
            # iterate over all flats
            for flat in flats:
                property = ItemLoader(item=Property())

                # parsing the bedrooms and replace (br) with (bedroom)
                bd_rooms = flat.css("div.bottom-ic p::text").get().replace("br", "bedroom")
                title = bd_rooms + "flat for rental"
                property.add_value('title', title)
                
                # parsing the price of the flat                
                price_str = flat.css("div.bottom-ic h5::text").get()
                if price_str[-1] == 'w':    # case of pw (if last character = 'w')
                    price_number = str(4 * int(price_str[3 : -3]))      # multiply the price by 4 to be pcm
                else:                       # case of pcm
                    price_number = str(int(price_str[3 : -4]))          # the price is per month already
                property.add_value('price', price_number)
                

                # parsing the flat and concatenate with domain url (as the link is relative not absolute)  
                flat_url = "https://" + self.allowed_domains[0] + flat.css("div.h4-space h4 a::attr(href)").get()
                property.add_value('url', flat_url)

                
                yield property.load_item()