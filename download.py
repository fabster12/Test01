import os
import sys
import re
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

class SiteDownloader:
    def __init__(self, base_url, max_pages=5):
        self.base_url = base_url
        self.max_pages = max_pages
        self.domain = urlparse(base_url).netloc
        self.output_dir = self.domain
        self.page_queue = [self.base_url]
        self.pages_downloaded = 0

        self.visited_pages_file = 'visited_pages.txt'
        self.visited_assets_file = 'visited_assets.txt'

        self.visited_pages = self._load_visited(self.visited_pages_file)
        self.visited_assets = self._load_visited(self.visited_assets_file)
        self.cms_detected = False

        self.session = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def _load_visited(self, filename):
        try:
            with open(filename, 'r') as f:
                return set(f.read().splitlines())
        except FileNotFoundError:
            return set()

    def _save_visited(self, visited_set, filename):
        with open(filename, 'w') as f:
            for url in sorted(list(visited_set)):
                f.write(url + '\n')

    def _get_local_path(self, url, content_type=''):
        parsed_url = urlparse(url)
        path = parsed_url.path.lstrip('/')

        if 'text/html' in content_type:
            if not path or path.endswith('/'):
                path = os.path.join(path, 'index.html')
            elif '.' not in os.path.basename(path):
                path = os.path.join(path, 'index.html')
        elif not path:
            path = os.path.basename(parsed_url.path)
            if not path: # case where url is just 'http://domain.com'
                path = 'index.html'

        return os.path.join(self.output_dir, path)

    def download_site(self):
        while self.page_queue and self.pages_downloaded < self.max_pages:
            url = self.page_queue.pop(0)
            if url in self.visited_pages:
                continue

            self.process_page(url)

        self._save_visited(self.visited_pages, self.visited_pages_file)
        self._save_visited(self.visited_assets, self.visited_assets_file)
        print("Download finished.")

    def process_page(self, url):
        print(f"Processing page: {url}")
        try:
            response = self.session.get(url, verify=False, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Failed to download page {url}: {e}")
            return

        self.visited_pages.add(url)
        self.pages_downloaded += 1
        content_type = response.headers.get('Content-Type', '')
        local_path = self._get_local_path(url, content_type)
        local_dir = os.path.dirname(local_path)
        os.makedirs(local_dir, exist_ok=True)
        if os.path.isdir(local_path): return

        if 'text/html' in content_type:
            soup = BeautifulSoup(response.content, 'html.parser')

            base_tag = soup.find('base')
            if base_tag:
                base_tag.decompose()

            if not self.cms_detected:
                generator_tag = soup.find('meta', attrs={'name': 'generator'})
                if generator_tag and 'content' in generator_tag.attrs:
                    content = generator_tag['content']
                    if 'Joomla' in content:
                        print("CMS detected: Joomla")
                        self.cms_detected = True
                    elif 'WordPress' in content:
                        print("CMS detected: WordPress")
                        self.cms_detected = True

            # Rewrite and queue page links
            for tag in soup.find_all('a', href=True):
                abs_link = urljoin(url, tag['href'])
                if urlparse(abs_link).netloc == self.domain:
                    tag['href'] = os.path.relpath(self._get_local_path(abs_link, 'text/html'), local_dir)
                    if abs_link not in self.visited_pages: self.page_queue.append(abs_link)

            # Rewrite and process asset links
            asset_tags = {'img': 'src', 'link': 'href', 'script': 'src'}
            for tag_name, attr in asset_tags.items():
                for tag in soup.find_all(tag_name, **{attr: True}):
                    if tag.name == 'link' and tag.get('type') in ['application/rss+xml', 'application/atom+xml']:
                        continue
                    asset_url = tag[attr]
                    abs_asset_url = urljoin(url, asset_url)
                    if urlparse(abs_asset_url).netloc == self.domain:
                        tag[attr] = os.path.relpath(self._get_local_path(abs_asset_url), local_dir)
                        self.process_asset(asset_url, url)

            with open(local_path, 'wb') as f:
                f.write(soup.prettify('utf-8'))
        else:
            with open(local_path, 'wb') as f:
                f.write(response.content)

    def process_asset(self, url, base_page_url):
        abs_url = urljoin(base_page_url, url)
        if urlparse(abs_url).netloc != self.domain or abs_url in self.visited_assets:
            return

        print(f"Processing asset: {abs_url}")
        try:
            response = self.session.get(abs_url, verify=False, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Failed to download asset {abs_url}: {e}")
            return

        self.visited_assets.add(abs_url)
        content_type = response.headers.get('Content-Type', '')
        local_path = self._get_local_path(abs_url, content_type)
        local_dir = os.path.dirname(local_path)
        os.makedirs(local_dir, exist_ok=True)
        if os.path.isdir(local_path): return

        if 'text/css' in content_type:
            content = response.text

            def repl(match):
                css_url = match.group(1).strip('\'"')
                abs_asset_url = urljoin(abs_url, css_url)
                if urlparse(abs_asset_url).netloc == self.domain:
                    relative_path = os.path.relpath(self._get_local_path(abs_asset_url), local_dir)
                    self.process_asset(css_url, abs_url)
                    return f"url('{relative_path}')"
                return match.group(0) # Unchanged

            content = re.sub(r'url\((.*?)\)', repl, content)
            with open(local_path, 'w', encoding='utf-8') as f:
                f.write(content)
        else:
            with open(local_path, 'wb') as f:
                f.write(response.content)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python download.py <max_pages>")
        sys.exit(1)

    try:
        max_pages_arg = int(sys.argv[1])
    except ValueError:
        print("Error: <max_pages> must be an integer.")
        sys.exit(1)

    downloader = SiteDownloader('http://samsonspin.nl', max_pages=max_pages_arg)
    downloader.download_site()
