# -*- coding: utf-8 -*-
import scrapy
import re
from douban.items import MovieMeta, Comment

class Top250Spider(scrapy.Spider):
    name = 'top250'
    allowed_domains = ['movie.douban.com']
    # 抓取前10页，共250部电影
    start_urls = [f'https://movie.douban.com/top250?start={i*25}&filter=' for i in range(10)]

    # 🚀 绕过豆瓣反爬的核心配置
    custom_settings = {
        'DOWNLOAD_DELAY': 5.0,        # 延迟5秒，安全第一
        'CONCURRENT_REQUESTS': 1,     # 强制串行
        'COOKIES_ENABLED': True,
        'DEFAULT_REQUEST_HEADERS': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0',
            'Cookie': '_pk_id.100001.8cb4=d6e3648bd6e60097.1758709967.; __utmv=30149280.29143; __yadk_uid=xhrdjQwENXExgPgAGJmnrB3ywoIAnOv0; bid=gwioWkdGA_k; ll="118251"; _vwo_uuid_v2=D73A64A846E65FE79015DA8CEB99FBE6B|29b63d541342a31eda9e2c2111c7193a; dbcl2="291432106:InaZjv/ewh8"; push_noty_num=0; push_doumail_num=0; ck=KSFC; frodotk_db="57e95218728dcd2d07bbf64957a96787"; ap_v=0,6.0; _pk_ref.100001.8cb4=%5B%22%22%2C%22%22%2C1773988424%2C%22https%3A%2F%2Fcn.bing.com%2F%22%5D; _pk_ses.100001.8cb4=1; __utma=30149280.1107377671.1758709968.1758715123.1773988425.3; __utmc=30149280; __utmz=30149280.1773988425.3.2.utmcsr=cn.bing.com|utmccn=(referral)|utmcmd=referral|utmcct=/; __utmt=1; __utmb=30149280.4.10.1773988425'
        }
    }

    def parse(self, response):
        for movie in response.xpath('//div[@class="item"]'):
            meta = MovieMeta()
            detail_link = movie.xpath('.//div[@class="hd"]/a/@href').get() or ""
            db_id = detail_link.split('/')[-2] if detail_link else ""
            
            meta['douban_id'] = str(db_id)
            meta['type'] = 'movie'
            meta['cover'] = movie.xpath('.//div[@class="pic"]/a/img/@src').get() or ""
            meta['name'] = movie.xpath('.//span[@class="title"][1]/text()').get() or ""
            meta['douban_score'] = movie.xpath('.//span[@class="rating_num"]/text()').get() or "0.0"
            
            # 使用 contains 防止 DOM 空格影响
            votes_text = movie.xpath('.//div[@class="star"]/span[contains(text(), "人评价")]/text()').get() or "0"
            meta['douban_votes'] = "".join(re.findall(r'\d+', votes_text)) or "0"
            
            # 🚨 解决 MySQL 的 1366 / 1292 类型严格报错
            meta['year'] = "0"
            meta['mins'] = "0"
            meta['release_date'] = "2000-01-01"
            
            # 其余字符串字段置空防报错
            for f in ['slug', 'directors', 'actors', 'genres', 'official_site', 'regions', 'languages', 'alias', 'imdb_id', 'tags', 'storyline', 'actor_ids', 'director_ids']:
                meta[f] = ""
            yield meta

            # 每部电影抓取前 2 页的短评
            if db_id:
                for p in range(2):
                    yield scrapy.Request(
                        f'https://movie.douban.com/subject/{db_id}/comments?start={p*20}&status=P&sort=new_score',
                        callback=self.parse_comments,
                        meta={'db_id': db_id}
                    )

    def parse_comments(self, response):
        # 拦截校验
        if "sec.douban.com" in response.url: return
        
        db_id = response.meta['db_id']
        comments = response.xpath('//div[contains(@class, "comment-item")]')
        
        for c in comments:
            item = Comment()
            item['douban_id'] = str(db_id)
            item['douban_comment_id'] = c.xpath('./@data-cid').get() or ""
            item['douban_user_nickname'] = c.xpath('.//span[@class="comment-info"]/a/text()').get() or "匿名用户"
            
            # 兼容两种评论标签结构
            content = c.xpath('.//span[@class="short"]/text()').get()
            if not content:
                content = c.xpath('.//p[contains(@class, "comment-content")]/span/text()').get()
            item['content'] = (content or "").replace('\n', ' ').strip()
            
            rating_class = c.xpath('.//span[contains(@class, "rating")]/@class').get()
            item['rating'] = re.search(r'allstar(\d)0', rating_class).group(1) if rating_class else '3'
            
            for f in ['douban_user_avatar', 'douban_user_url']:
                item[f] = ""
            
            # 🚨 解决评论表的 1366 报错 (INT) 和 1292 报错 (DATETIME)
            item['votes'] = "0"
            item['comment_time'] = "2000-01-01 00:00:00"
            
            self.logger.info(f"✅ 成功抓取并入库评论: {item['content'][:15]}...")
            yield item