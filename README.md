# profile-crawler-of-SinaWeibo
I will crawl profile of user in SinaWeibo at a  higher speed than others.

Because of SinaWeibo's restrictions on the crawler, I do not intend to login SinaWeibo.
We just need to set the cookie in our code.

about the crawling speed, I think it is very fast enought. And you can manupulate multiple thread to crawl data of SinaWeib.

when you run this colde on Windows, you may encounter some chinese incorrect codes.
I guess you can add some code like blow:
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
