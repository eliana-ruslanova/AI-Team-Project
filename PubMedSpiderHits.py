import scrapy
import time
import pdb

class PubMedSpiderHits(scrapy.Spider):
    name = "dois"
    currentDoc = 'dummy'
    url_blank_search = 'https://pubmed.ncbi.nlm.nih.gov/?term=Artificial%20Intelligence&filter=years.2005-2020&page='
    url_blank_article = 'https://pubmed.ncbi.nlm.nih.gov/'
    page = 0
    
    def start_requests(self):
        yield scrapy.Request(url = self.url_blank_search)
            
    def parse(self, response):
        numberHits = response.css('div.results-amount span::text').get()
        numberHits = numberHits.replace(",", "")
        numberPages = int((int(numberHits)/10)+1)
        for x in range(1,numberPages):
            self.page = x
            url = self.url_blank_search + f'{x}'
            yield scrapy.Request(url = url, callback = self.parsePage)
        
    
    def parsePage(self, response):
        for article in response.css('article.labs-full-docsum'):
            self.currentDoc = article.css('.docsum-pmid::text').get()
            url_article = self.url_blank_article + self.currentDoc
            yield scrapy.Request(url = url_article, callback = self.parseDoi)
    
    def parseDoi(self, response):
        count = 0
        for span in response.css('span.identifier'):
            countStr = str(count)
            idLabel = span.css('.id-label::text').get()
            if 'DOI' in idLabel:
                print(span.css('a.id-link::text').get())
        print(response.css('div.abstract p::text').get())
            
