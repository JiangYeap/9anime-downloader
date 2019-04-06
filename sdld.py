from __future__ import print_function
from builtins import input
import sys, os, time
from datetime import timedelta
try:
    import cfscrape
except ImportError:
    import requests
    _has_cfscrape = False
else:
    _has_cfscrape = True


class SimpleDownloader(object):
    def __init__(self, url, file_path):
        self.url = url
        self.file_path = file_path
        self.file_name = file_path.split('\\')[-1]
        if _has_cfscrape:
            self.scraper = cfscrape.create_scraper()
        else:
            self.scraper = requests

    def start(self):
        if not self._check_duplicate():
            print('Skipping download %s.' % self.file_name)
            return
        resp = self.scraper.get(self.url, allow_redirects=True, stream=True)
        length = int(resp.headers.get('content-length', default=0))
        resp_it = resp.iter_content(chunk_size=1024)
        label = 'Downloading %s - ' % self.file_name
        size = (length//1024) + 1
        self._show_progress(resp_it, label, size)

    def _check_duplicate(self):
        if os.path.exists(self.file_path):
            message = 'File %s already exists. Overwite file? (Y/N): '
            overwrite = input(message % self.file_path)
            if overwrite.lower() == 'y':
                return True
            elif overwrite.lower() == 'n':
                return False
            else:
                print('Invalid input. Please try again.')
                return self._check_duplicate()
        else:
            return True
        
    def _show_progress(self, resp_it, label, size):
        with open(self.file_path, 'wb') as f:
            current_size = 0
            start_time = time.time()
            for data in resp_it:
                f.write(data)
                current_size += 1
                elapsed_time = int(time.time() - start_time)
                elapsed_time = timedelta(seconds=elapsed_time)
                progress = int(50*current_size/size)
                done = '#'*progress
                left = ' '*(50 - progress)
                sys.stdout.write('\r%s[%s%s] %d/%d KB - %s' % (label, done,
                    left, current_size, size, elapsed_time))
                sys.stdout.flush()
        print('')
