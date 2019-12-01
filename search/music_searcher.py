from fuzzywuzzy import fuzz
from operator import itemgetter
from os import path, walk
from .music_search_result import MusicSearchResult


class MusicSearcher:

    def __init__(self, root_path):
        self.music_path = path.join(root_path, 'music')

    def exact_search(self, file_name):
        """
        Retrieves the exact path of the file if it exists.

        :param file_name: name of the file with format (e.g 'music.mp3')
        :return: relative file path to app root path
        """
        if file_name is None:
            return MusicSearchResult(False)
        file_path = path.join(self.music_path, file_name)
        if not path.exists(file_path):
            return MusicSearchResult(False)
        return MusicSearchResult(True, file_path=file_path)

    def best_search(self, file_name):
        """
        Retrieves the file's name best match path.

        :param file_name: name of the file with format (e.g 'music.mp3')
        :return: relative
        """
        if file_name is None:
            return MusicSearchResult(False)
        best_dirs = []
        for file in next(walk(self.music_path))[2]:
            dir_point = fuzz.token_sort_ratio(file_name, file)
            best_dirs.append((file, dir_point))
        if not best_dirs:
            return MusicSearchResult(False)
        best_dirs.sort(key=itemgetter(1), reverse=True)
        best_match = path.join(self.music_path, best_dirs[0][0])
        return MusicSearchResult(True, file_path=best_match)
