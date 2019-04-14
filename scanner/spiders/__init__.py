import scrapy
from scrapy.http import FormRequest, HtmlResponse
from scrapy.selector import Selector
from scrapy.shell import inspect_response
from pprint import pprint
from scanner.items import ScannerItem
from scanner.items import Shoe
import logging
import json
class scannerSpider (scrapy.Spider):

  name = "ShoesScanner"
  stockx_base_url = "https://stockx.com/api/browse?page=%s&productCategory=sneakers"
  start_urls = [stockx_base_url % 0]
  page_number = 0
  download_delay = 0.2
  custom_settings = {
   'DEPTH_PRIORITY' : 1,
'SCHEDULER_DISK_QUEUE' : 'scrapy.squeues.PickleFifoDiskQueue',
'SCHEDULER_MEMORY_QUEUE' : 'scrapy.squeues.FifoMemoryQueue'
  }

  def parse(self, response):
   json_response = json.loads(response.text)
   lastpage = int(json_response.get("Pagination", {}).get("lastPage"))
   
   for page_number in range(1 ,lastpage + 1):
     rq = scrapy.Request(self.stockx_base_url % page_number, callback= self.parse_start_information)
     yield rq
    
    
   
  def parse_start_information(self, response):
    json_response = json.loads(response.text)
    for product in json_response.get("Products", []):
        shoes = {
        'name' :  product.get("title"),
        'style_id' : product.get("styleId"),
        'stockx_url' : "https://stockx.com/{}".format(product.get("urlKey") )} 
        rq = scrapy.Request(shoes['stockx_url'], callback= self.parse_stockx_information, meta={'shoes': shoes})
        yield rq
        
        
        

  
        
    
  def parse_stockx_information (self, response):
     
    shoes = response.meta['shoes'].copy()

    size =  response.xpath("//div[contains(@class, 'select-control ')]/div[contains(@class, 'select-options')]/ul[contains(@class, 'list-unstyled sneakers')]/li[contains(@class, 'select-option')]/div[contains(@class, 'inset')]/*[1]/text()").extract()
    size =set([float(x) for x in size if x != 'All'])

    shoes['stockx_size'] = sorted(size)
    price = response.xpath("//div[contains(@class, 'select-control ')]/div[contains(@class, 'select-options')]/ul[contains(@class, 'list-unstyled sneakers')]/li[contains(@class, 'select-option')]/div[contains(@class, 'inset')]/div[contains(@class, 'subtitle')]/text()").extract()
    price.pop(0)
    shoes['stockx_price'] = price[0:len(size)]
    yield scrapy.Request('https://www.flightclub.com/catalogsearch/result/?q={}'.format(shoes['style_id']), self.parse_flightclub_infromation,meta = {'shoes': shoes})
   
        
  def parse_flightclub_infromation(self, response): 
    shoes =  response.meta['shoes'].copy()
    shoes["flightclub_url"] = response.xpath("//div[contains(@class, \'results-view\')]/div/ul/li/a/@href").extract_first()
    shoes['flightclub_price'] = []
    selected_size = '?size=' + str(shoes['stockx_size'][0])
    yield scrapy.Request(url = shoes['flightclub_url'], callback=self.parse_flightclub_sizes , meta={'shoes': shoes,})
  def parse_flightclub_sizes(self, response):
    shoes = response.meta['shoes'].copy()
    sizes = response.xpath("//ul[contains(@class, 'list-size hidden-element')]/li/button/text()").extract() 
    sizes = map(lambda x: float(x.strip().replace(" ","")),sizes)
    shoes['flightclub_size'] = list(sizes)
    selected_size = '?size=' + str(shoes['flightclub_size'][0])
    yield scrapy.Request(url = shoes['flightclub_url'] + selected_size, callback=self.parse_flightclub_price , meta={'shoes': shoes,'next_number': 0})
  def parse_flightclub_price(self, response):
    shoes = response.meta['shoes'].copy()
    price = None
    price = response.xpath("//span[contains(@class, 'regular-price')]/span[contains(@class, 'price')]/text()").extract_first()
    logging.info(price)
    shoes['flightclub_price'].append(price)
    new_size = response.meta['next_number'] + 1
    if(new_size != len(shoes['flightclub_size'])):
      selected_size = '?size=' + str(shoes['flightclub_size'][new_size])
      yield scrapy.Request(url = shoes['flightclub_url'] + selected_size, callback=self.parse_flightclub_price , meta={'shoes': shoes,'next_number': new_size})
    else:
       shoe = Shoe()
       for pos,size in enumerate(shoes['flightclub_size']):
            position = shoes['stockx_size'].index(size)
            stockx_price = shoes['stockx_price'][position]
            shoe['stockx_price'] = "".join([c for c in stockx_price  if c in '0123456789.'])
            flightclub_price = shoes['flightclub_price'][pos]
            shoe['flightclub_price'] = "".join([c for c in flightclub_price if c in '0123456789.'])

            shoe['stockx_price'] = float(shoe['stockx_price']) + 13.0

            shoe['flightclub_price'] = float(shoe['flightclub_price']) - (float(shoe['flightclub_price'])*0.2)

            shoe['profit'] = shoe['flightclub_price'] - shoe['stockx_price']
            shoe['name'] = shoes['name']
            shoe['style_id'] = shoes['style_id']
            shoe['stockx_url'] = shoes['stockx_url']
            shoe['flightclub_url'] = shoes['flightclub_url']
            shoe['size'] = size
            yield shoe

   
     

