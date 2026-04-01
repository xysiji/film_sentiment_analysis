# -*- coding: utf-8 -*-
import scrapy
import re
from douban.items import MovieMeta, Comment

class Top250Spider(scrapy.Spider):
    name = 'top250'
    allowed_domains = ['movie.douban.com']
    
    # 增加自定义配置，降低并发防止被豆瓣拉黑IP
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'DOWNLOAD_DELAY': 1.5,
        'CONCURRENT_REQUESTS': 2,
    }

    def start_requests(self):
        # 遍历豆瓣 Top250 的 10 页 (每页25个，共250个)
        for i in range(0, 250, 25):
            url = f'https://movie.douban.com/top250?start={i}&filter='
            yield scrapy.Request(url, callback=self.parse_list)

    def parse_list(self, response):
        self.logger.info(f"正在解析 Top250 列表页: {response.url}")
        movies = response.xpath('//div[@class="item"]')
        
        for movie in movies:
            meta = MovieMeta()
            
            # 1. 提取基础信息并保证全为字符串（适配你的 pipelines.py strip() 逻辑）
            detail_link = movie.xpath('.//div[@class="hd"]/a/@href').get() or ""
            douban_id = detail_link.split('/')[-2] if detail_link else ""
            
            meta['douban_id'] = str(douban_id)
            meta['name'] = movie.xpath('.//span[@class="title"][1]/text()').get() or ""
            meta['douban_score'] = movie.xpath('.//span[@class="rating_num"]/text()').get() or "0"
            
            votes_str = movie.xpath('.//div[@class="star"]/span[4]/text()').get() or "0"
            meta['douban_votes'] = votes_str.replace('人评价', '').strip()
            meta['cover'] = movie.xpath('.//div[@class="pic"]/a/img/@src').get() or ""
            meta['type'] = 'movie'
            
            # 兼容旧表结构，没抓到的字段给空字符串
            meta['slug'] = ""
            meta['year'] = ""
            meta['directors'] = ""
            meta['actors'] = ""
            meta['genres'] = ""
            meta['regions'] = ""
            meta['languages'] = ""
            meta['release_date'] = ""
            meta['mins'] = ""
            meta['alias'] = ""
            meta['imdb_id'] = ""
            meta['tags'] = ""
            meta['storyline'] = ""
            meta['actor_ids'] = ""
            meta['director_ids'] = ""

            yield meta

            # 2. 为当前电影生成抓取评论的 Request (抓取前 5 页，每页 20 条，共 100 条评论/部)
            if douban_id:
                for page in range(5):
                    comment_url = f'https://movie.douban.com/subject/{douban_id}/comments?start={page*20}&limit=20&status=P&sort=new_score'
                    yield scrapy.Request(
                        comment_url, 
                        callback=self.parse_comments, 
                        meta={'douban_id': douban_id}
                    )

    def parse_comments(self, response):
        douban_id = response.meta['douban_id']
        comments = response.xpath('//div[@class="comment-item "]')
        
        for c in comments:
            item = Comment()
            item['douban_id'] = str(douban_id)
            item['douban_comment_id'] = c.xpath('./@data-cid').get() or ""
            item['douban_user_nickname'] = c.xpath('.//span[@class="comment-info"]/a/text()').get() or "匿名"
            item['douban_user_avatar'] = c.xpath('.//a[@class="avatar"]/img/@src').get() or ""
            item['douban_user_url'] = c.xpath('.//span[@class="comment-info"]/a/@href').get() or ""
            
            content = c.xpath('.//span[@class="short"]/text()').get() or ""
            item['content'] = content.replace('\n', ' ').strip()
            
            votes = c.xpath('.//span[@class="votes vote-count"]/text()').get()
            item['votes'] = str(votes) if votes else '0'
            item['comment_time'] = c.xpath('.//span[@class="comment-time "]/@title').get() or ""

            # 提取星级评分 (豆瓣的 class 格式为 allstar50 代表 5星)
            rating_class = c.xpath('.//span[contains(@class, "rating")]/@class').get()
            if rating_class:
                match = re.search(r'allstar(\d)0', rating_class)
                item['rating'] = match.group(1) if match else '0'
            else:
                item['rating'] = '0'

            yield item