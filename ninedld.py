from __future__ import print_function
import re
from lxml.html import fromstring
from sdld import SimpleDownloader
try:
    from urllib.parse import urljoin 
except ImportError:
     from urlparse import urljoin


class NineDownloader(SimpleDownloader):
    DL_URL_REGEX = re.compile('file: \'(.*?)\'.*?label: \'(\d*?) P\'')

    def __init__(self, ep_url, quality, file_path):
        super(NineDownloader, self).__init__(None, file_path)
        self.url = self._get_url(ep_url, quality)

    def start(self):
        super(NineDownloader, self).start()

    def _get_url(self, ep_url, quality):
        ep_str = self.scraper.get(ep_url).content.decode('utf-8')
        ep_page = fromstring(ep_str)
        iframe_url = ep_page.xpath('//iframe')[0].xpath('./@src')[0].strip()
        iframe_url = urljoin(ep_url, iframe_url)
        iframe_str = self.scraper.get(iframe_url).content.decode('utf-8')
        for dl_url, dl_quality in self.DL_URL_REGEX.findall(iframe_str):
            if dl_quality == quality:
                return dl_url
        print('Quality not found for %s. URL: %s.' % (self.file_name, ep_url))
        raise ValueError
