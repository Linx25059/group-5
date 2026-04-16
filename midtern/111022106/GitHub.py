import scrapy
import re

class EasyGithubSpider(scrapy.Spider):
    name = 'easy_github'
    start_urls = ['https://github.com/Linx25059?tab=repositories']

    custom_settings = {
        'ROBOTSTXT_OBEY': False,           
        'FEED_FORMAT': 'xml',              
        'FEED_URI': 'repos.xml',      
        'FEED_EXPORT_ENCODING': 'utf-8'    
    }

    def parse(self, response):
        
        for repo in response.css('li[itemprop="owns"]'):
            
            
            about = repo.css('p[itemprop="description"]::text').get()
            language = repo.css('span[itemprop="programmingLanguage"]::text').get()
            
            
            my_data = {
                'URL': response.urljoin(repo.css('a[itemprop="name codeRepository"]::attr(href)').get()),
                'About': about.strip() if about else '無說明',
                'Languages': language if language else '未指定',
                'LastUpdated': repo.css('relative-time::attr(datetime)').get()
            }

            relative_url = repo.css('a[itemprop="name codeRepository"]::attr(href)').get()
            yield response.follow(
                relative_url, 
                callback=self.parse_commits, 
                cb_kwargs={'my_data': my_data}  
            )

    def parse_commits(self, response, my_data):

        commits_text = response.xpath('string(//a[contains(@href, "/commits/")])').get()
        
        if commits_text:
            match = re.search(r'([\d,]+)', commits_text)
            my_data['NumberOfCommits'] = match.group(1).replace(',', '') if match else '未知'
        else:
            my_data['NumberOfCommits'] = '未知'

        yield my_data
