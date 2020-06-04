from spiders.process_spider import ProcessSpider
from scrapy.crawler import CrawlerProcess


def scrap_law_scrapy(process_id):
    """ Scrapy Scrapper"""
    outputResponse = {}
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'LOG_ENABLED': False,
        'FEED-EXPORT_ENCODING': 'utf-8'
    })
    process.crawl(ProcessSpider, outputResponse=outputResponse, process_id=process_id)
    process.start()
    print(outputResponse)

ids = ["11001310503920170014900", "11001400300620170035900", "11001400300820170073900", "11001400301120170065300", "11001400301220170070600"]
process_id = ids[4]
scrap_law_scrapy(process_id)
