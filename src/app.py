from os import path
from flask import Flask, request, send_from_directory
from src.core.voice_remover import VoiceRemover
from src.search.music_searcher import MusicSearcher

app = Flask(__name__)
remover = VoiceRemover()
searcher = MusicSearcher(app.root_path)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return 'Sorry, but this path "%s" is not available' % path


@app.route('/split')
def split_exact_music():
    music = request.args.get('music')
    if music is None:
        return 'You forgot to send the name of the music!.\n Ex: .../?music=Track.mp3'
    mode = request.args.get('mode')
    if mode is None or mode == 'exact':
        result = searcher.exact_search(music)
    else:
        result = searcher.best_search(music)
    if not result.success:
        return 'Music not found... (っ °Д °;)っ'
    print('Splitting song into voice and accompaniment!')
    remover.remove(result.file_path)
    return 'Success!'


@app.route('/favicon.ico')
def favicon():
    static_path = path.join(app.root_path, 'static')
    return send_from_directory(static_path, 'favicon.ico', mimetype='image/vnd.microsoft.icon')
