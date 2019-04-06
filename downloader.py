from __future__ import print_function
from builtins import input
import sys, re, os
from lxml.html import fromstring
from ninedld import NineDownloader
try:
    import cfscrape
    _has_cfscrape = True
except ImportError:
    _has_cfscrape = False
    import requests
try:
    from urllib.parse import urljoin 
except ImportError:
     from urlparse import urljoin

SRC_REGEX = re.compile('https://www.rapidvideo.com/e/[^"\']*')
RANGE_REGEX = re.compile('(\d+)\s*-\s*(\d+)$')

if _has_cfscrape:
    scraper = cfscrape.create_scraper()
else:
    scraper = requests


def download(series_url, default=False):
    title, ep_urls, ep_names, num_eps = get_series_data(series_url)
    ep_start, ep_end , quality = get_range_quality(ep_names, num_eps, default)
    dir_path = create_dir(title, default)
    print('\nDownloading %d episodes at %sp.' % (ep_end - ep_start, quality))
    print('Download destination: %s\n' % dir_path)
    for i in range(ep_start, ep_end):
        try:
            n = NineDownloader(ep_urls[i], quality, dir_path + ep_names[i])
            n.start()
        except ValueError:
            continue


def get_series_data(series_url):
    series_page = fromstring(scraper.get(series_url).content.decode('utf-8'))
    title = series_page.xpath('//h2[@class="entry-title"]/text()')[0].strip()
    ep_urls = []
    ep_names = []
    for ep_entry in series_page.xpath('//li[contains(@class, "hentry")]/div[1]/a'):
        ep_url = ep_entry.xpath('./@href')[0].strip()
        ep_name = ep_entry.xpath('./@title')[0].strip()
        ep_urls.append(urljoin(series_url, ep_url))
        ep_names.append('%s.mp4' % ep_name)
    ep_urls = ep_urls[::-1]
    ep_names = ep_names[::-1]
    num_eps = len(ep_names)
    if not num_eps:
        print('No episodes found. Exiting.')
        sys.exit()
    return title, ep_urls, ep_names, num_eps


def create_dir(title, default):
    if default:
        dir_name = title
    else:
        dir_name = input('\nEnter download folder name or leave empty to use ' +
                'default title. It will be created in the current directory: ')
        if not dir_name:
            dir_name = title
    dir_root = os.getcwd()
    dir_path = dir_root + '\\' + dir_name + '\\'
    if not os.path.exists(dir_path): 
        os.makedirs(dir_path)
    else:
        merge_confirmation(default)
    return dir_path


def merge_confirmation(default):
    if default:
        return
    merge = input('Directory exists. Merge with existing directory? ' +
            'Files with the same name will be overwritten. (Y/N): ')
    if merge.lower() == 'n':
        print('Download aborted.')
        sys.exit()
    elif merge.lower() not in 'yn':
        print('Invalid input. Please try again.')
        merge_confirmation()


def get_range_quality(ep_names, num_eps, default):
    print_ep_list(ep_names)
    start_ep, end_ep = select_eps(num_eps, default)
    end_ep += 1
    quality = select_quality(default)
    return start_ep, end_ep, quality
 

def print_ep_list(ep_names):
    print('\nEpisode list:')
    for i in range(len(ep_names)):
        print('[%d] %s' % (i, ep_names[i]))
    print('')


def select_eps(num_eps, default=False):
    if default:
        return (0, num_eps - 1)
    ep_range_input = input('Select range of episodes to download or ' +
            'leave empty to download all episodes (start-end): ')
    if ep_range_input:
        res = RANGE_REGEX.search(ep_range_input)
        if res:
            start_ep = int(res.group(1))
            end_ep = int(res.group(2))
            if end_ep < start_ep or end_ep >= num_eps or start_ep < 0:
                print('Invalid input. Please try again.')
                start_ep, end_ep = select_eps(num_eps)
        else:
            print('Invalid input. Please try again.')
            start_ep, end_ep = select_eps(num_eps)
    else:
        start_ep = 0
        end_ep = num_eps - 1
    return start_ep, end_ep


def select_quality(default=False):
    if default:
        return '720'
    quality = input('Select video quality (720/480): ')
    if quality not in ['720', '480']:
        print('Invalid input. Please try again.')
        quality = select_quality()
    return quality


def query_series(title_query):
    query_url = 'https://ww.9animes.net/page/%d/?s=%s'
    page_num = 1
    series_urls = []
    series_titles = []
    while True:
        search_str = scraper.get(query_url % (page_num, title_query)).content.decode('utf-8')
        page_num += 1
        if '404' in search_str:
            break
        search_page = fromstring(search_str)
        for series in search_page.xpath('//span[@class="meta-category"]/a'):
            series_url = series.xpath('./@href')[0].strip()
            series_title = series.xpath('./text()')[0].strip()
            if series_url not in series_urls:
                series_urls.append(series_url)
                series_titles.append(series_title)
    num_series = len(series_titles)
    if not num_series:
        print('No results found. Exiting.')
        sys.exit()
    series_urls = series_urls[::-1]
    series_titles = series_titles[::-1]
    return series_urls, series_titles, num_series


def print_series_list(series_titles):
    print('\nQuery result list:')
    for i in range(len(series_titles)):
        print('[%d] %s' % (i, series_titles[i]))
    print('')


def select_series(num_series):
    series_index_input = input('Select series to download (index): ')
    if series_index_input:
        if series_index_input.isdigit():
            series_index = int(series_index_input)
            if series_index not in range(num_series):
                print('Invalid input.Please try again.')
                series_index = select_series(num_series)
    else:
        print('Invalid input. Please try again.')
        series_index = select_series(num_series)
    return series_index


if __name__ == '__main__':
    if len(sys.argv) == 2:
        series_url = sys.argv[1]
        download(series_url)
    elif len(sys.argv) == 3:
        if sys.argv[2] == '-d':
            series_url = sys.argv[1]
            download(series_url, True)
        elif sys.argv[2] == '-s':
            series_urls, series_titles, num_series = query_series(sys.argv[1])
            print_series_list(series_titles)
            series_index = select_series(num_series)
            download(series_urls[series_index])
    else:
        print('Usage: "python downloader.py <9ANIME_SERIES_URL>" or "python ' +
            'downloader.py <SERIES_NAME> -s" to search for series.')
    sys.exit()
