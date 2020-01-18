from .music_search_result import MusicSearchResult

from bs4 import BeautifulSoup
import json
import os
import requests

from moviepy.editor import VideoFileClip
from pathlib import Path
from pytube import YouTube
from seleniumwire.webdriver import Chrome
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager


chrome_driver_path = '/home/alex/Downloads/'


class RemoteSearcher:
    def __init__(self):
        self.music_path = 'src/music/'
        self.remote_url = 'https://www.letras.mus.br/'
        self.cse_url = 'https://cse.google.com/cse/element/v1'
        self.cse_params = dict(rsz='1', num='1', hl='pt-PT', source='gcsc', gss='.br', cselibv='8b2252448421acb3',
                               cx='partner-pub-9911820215479768:4038644078', safe='off',
                               cse_tok='find_token', exp='csqr,cc',
                               callback='google.search.cse.api18195')

    def find_music(self, music, artist):
        if self.check_internet_connection() is False:
            return MusicSearchResult(False)
        music_url = self.get_music_url(music, artist)
        if music_url is None:
            print('%s by %s not found remotely.' % (music, artist))
            return MusicSearchResult(False)
        music_id = self.get_music_id_from_url(music_url)
        subtitles = self.get_subtitles(music_id)
        if subtitles is None:
            return MusicSearchResult(False)
        music_ocid = self.get_music_ocid(music_url)
        if music_ocid is None:
            return MusicSearchResult(False)
        video = YouTube('https://youtube.com/watch?v=' + music_ocid)
        stream = video.streams.filter(file_extension='mp4').first()
        normalized_artist = artist.strip().lower()
        artist_file_path = self.music_path + normalized_artist
        Path(artist_file_path).mkdir(parents=True, exist_ok=True)
        stream.download(artist_file_path)
        video_file = VideoFileClip(os.path.join('src', 'music', normalized_artist, video.title + '.mp4'))
        video_file.audio.write_audiofile(os.path.join('src', 'music', normalized_artist, video.title + '.mp3'))
        with open(artist_file_path + '/' + video.title + '.txt', 'w') as subtitle_file:
            subtitle_file.write(subtitles)
        return MusicSearchResult(True, file_path=artist_file_path, file_name=video.title, file_codac='mp3')

    @staticmethod
    def check_internet_connection():
        try:
            request = requests.get('http://www.google.com/', timeout=2)
            request.raise_for_status()
            return True
        except requests.HTTPError as error:
            print('Checking internet connection failed, status code {0}.'.format(error.response.status_code))
        except requests.ConnectionError:
            print('No internet connection available.')
        return False

    def get_music_url(self, music, artist):
        cse_params = self.cse_params.copy()
        cse_params['q'] = artist + ' ' + music
        response = self.do_get_music_url(cse_params)
        response = response.text
        first_bracket = response.find('{')
        last_bracket = response.rfind('}')
        json_response = json.loads(response[first_bracket:last_bracket - len(response) + 1])
        music_url = json_response['results'][0]['richSnippet']['metatags']['ogUrl']
        return self.trim_translated_music_url(music_url)

    def do_get_music_url(self, cse_params):
        try:
            response = requests.get(url=self.cse_url, params=cse_params)
            response.raise_for_status()
            status_code = self.extract_status_from_response(response.text)
            if status_code == 403:
                cse_params['cse_tok'] = self.update_cse_token()
                response = requests.get(url=self.cse_url, params=cse_params)
        except requests.HTTPError:
            cse_params['cse_tok'] = self.update_cse_token()
            response = requests.get(url=self.cse_url, params=cse_params)
        return response

    @staticmethod
    def extract_status_from_response(response):
        first_index = response.find('{')
        last_index = len(response) - response.rfind('}') - 1
        json_response = json.loads(response[first_index:-last_index])
        if 'error' not in json_response:
            return 200
        return json_response['error']['code']

    def update_cse_token(self):
        cse_token = self.get_valid_cse_token()
        if cse_token is None:
            print('Could not update cse_tok from %s' % self.cse_url)
            return None
        self.cse_params['cse_tok'] = cse_token
        return cse_token

    def get_valid_cse_token(self):
        chrome = Chrome(ChromeDriverManager().install())
        chrome.get(self.remote_url + '?q=42')
        for request in chrome.requests:
            path = request.path
            if request.response and 'https://cse.google.com/cse/element' in path:
                first_index = path.find('&cse_tok=') + 9
                end_index = len(path) - path.find('&exp=')
                cse_token = path[first_index:-end_index]
                print('Updated cse_token to %s' % cse_token)
                chrome.__exit__()
                return cse_token
        chrome.__exit__()
        return None

    @staticmethod
    def trim_translated_music_url(music_url):
        wrong_word_index = music_url.find('traducao.html')
        if wrong_word_index != -1:
            music_url = music_url[:wrong_word_index - len(music_url)]
        https_end = music_url.find('https://m.')
        if https_end != -1:
            https_end = https_end + 10
            music_url = 'https://' + music_url[https_end:]
        return music_url

    @staticmethod
    def get_music_id_from_url(music_url):
        music_url = music_url[:-1]
        last_separation = music_url.rfind('/')
        music_id = music_url[last_separation + 1:]
        if music_id.isnumeric():
            return music_id
        soup = BeautifulSoup(requests.get(music_url).text, 'html.parser')
        footer_rows = soup.find_all('li', {'class': 'cnt-list-row'})
        for row in footer_rows:
            if row['data-url'] == music_id:
                return row['data-id']

    def get_subtitles(self, music_id):
        subtitles_url = self.remote_url + 'api/v2/subtitle/' + music_id + '/'
        response = requests.get(subtitles_url).json()
        subtitle_json = requests.get(subtitles_url + response[0] + '/').json()
        return subtitle_json['Original']['Subtitle']

    @staticmethod
    def get_music_ocid(music_url):
        browser = webdriver.Chrome(executable_path=ChromeDriverManager().install())
        browser.get(music_url)
        delay = 5
        try:
            thumbnail_prop = (By.CLASS_NAME, 'plm_thumb')
            thumb = WebDriverWait(browser, delay).until(expected_conditions.presence_of_element_located(thumbnail_prop))
            src = thumb.get_attribute('src')
            first_part = len('https://i.ytimg.com/vi/')
            browser.__exit__()
            return src[first_part:- len(src) + src.rfind('/')]
        except TimeoutException:
            print('Page didn''t load in %d seconds' % delay)
            browser.__exit__()
            return None
