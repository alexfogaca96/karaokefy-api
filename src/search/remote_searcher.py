from .music_search_result import MusicSearchResult
import json
import requests
from time import sleep
from pytube import YouTube
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager


chrome_driver_path = '/home/alex/Downloads/'

class RemoteSearcher:
    def __init__(self):
        self.remote_url = 'https://www.letras.mus.br/'
        self.cse_url = 'https://cse.google.com/cse/element/v1'
        self.cse_params = dict(rsz='1', num='1', hl='pt-PT', source='gcsc', gss='.br', cselibv='8b2252448421acb3',
                               cx='partner-pub-9911820215479768:4038644078', safe='off',
                               cse_tok='AKaTTZiTfoWWy9poT4ZAUEGOfAA4:1579015681629', exp='csqr,cc',
                               callback='google.search.cse.api18195')

    def find_music(self, music, artist):
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
        music_video_path = requests.get('https://youtube.com/watch?v=' + music_ocid)
        print('music_video_path %s' % music_video_path)
        print('subtitles %s' % subtitles)
        return MusicSearchResult(False)

    def get_music_url(self, music, artist):
        self.cse_params['q'] = artist + ' ' + music
        response = requests.get(url=self.cse_url, params=self.cse_params)
        if not response:
            print('cse_token is outdated.')
            return None
        response = response.text
        first_bracket = response.find('{')
        last_bracket = response.rfind('}')
        json_response = json.loads(response[first_bracket:last_bracket - len(response) + 1])
        music_url = json_response['results'][0]['richSnippet']['metatags']['ogUrl']
        return self.trim_translated_music_url(music_url)

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
        return music_url[last_separation + 1:]

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
            thumb_properties = (By.CLASS_NAME, 'plm_thumb')
            thumb = WebDriverWait(browser, delay).until(EC.presence_of_element_located(thumb_properties))
            src = thumb.get_attribute('src')
            first_part = len('https://i.ytimg.com/vi/')
            return src[first_part:- len(src) + src.rfind('/')]
        except TimeoutException:
            print("Page didn't load in %d seconds" % delay)
            return None
