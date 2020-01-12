import requests
import json
from time import sleep
from .music_search_result import MusicSearchResult
from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from pytube import YouTube


chrome_driver_path = '/home/alex/Downloads/'

class RemoteSearcher:
    def __init__(self):
        self.remote_url = 'https://www.letras.mus.br/'
        self.cse_url = 'https://cse.google.com/cse/element/v1'
        self.cse_params = dict(rsz='1', num='1', hl='pt-PT', source='gcsc', gss='.br', cselibv='8b2252448421acb3',
                               cx='partner-pub-9911820215479768:4038644078', safe='off',
                               cse_tok='AKaTTZg-jGfIAJ3mrxhGPzaVDpUV:1578758834084', exp='csqr,cc',
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
        music_video_path = requests.get('youtube.com/watch?v=' + music_ocid)
        print(music_video_path)
        return MusicSearchResult(False)

    def get_music_url(self, music, artist):
        self.cse_params['q'] = artist + ' ' + music
        response = requests.get(url=self.cse_url, params=self.cse_params).text
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
        all_requests = browser.requests
        for request in all_requests:
            print(request.path)
            if 'youtube.com/api/stats/atr' in request.path:
                ocid_index = request.path.find('ocid=')
                ocid_end_index = request.path[ocid_index:].find('&') - 1
                return request.path[ocid_index + 5:ocid_end_index]
        return None
