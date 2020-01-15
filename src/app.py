from flask import Flask, request, send_from_directory
from src.core.voice_remover import VoiceRemover
from src.search.music_searcher import MusicSearcher
from os.path import join

app = Flask(__name__)
remover = VoiceRemover()
searcher = MusicSearcher(app.root_path)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return 'Sorry, but the path "%s" is not available' % path


@app.route('/split')
def split_exact_music():
    music_data = get_artist_and_music()
    if not music_data[0]:
        return music_data[1]
    mode = request.args.get('mode', default='exact')
    result = searcher.find_music(mode, music_data[1], music_data[2])
    if not result.success:
        return 'Music not found.'
    print('Splitting song into voice and accompaniment!')
    remover.remove(result.file_path, result.file_name, result.file_codac)
    return 'Success!'


def get_artist_and_music():
    artist = request.args.get('artist')
    music = request.args.get('music')
    if artist is None or music is None:
        return False, 'You forgot to send the name of the artist or the music!'
    return True, artist, music


@app.route('/favicon.ico')
def favicon():
    static_path = join(app.root_path, 'static')
    return send_from_directory(static_path, 'favicon.ico', mimetype='image/vnd.microsoft.icon')
