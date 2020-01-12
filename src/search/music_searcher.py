from .music_search_result import MusicSearchResult
from .local_searcher import LocalSearcher
from .remote_searcher import RemoteSearcher


class MusicSearcher:
    def __init__(self, root_path):
        self.root_path = root_path
        self.local_searcher = LocalSearcher(root_path)
        self.remote_searcher = RemoteSearcher()

    def find_music(self, mode, music, artist):
        """
        Try to find the 'music' file locally, following one of two different strategies
        that are selected by the 'mode' parameter.
        """
        if mode == 'exact':
            result = self.local_searcher.exact_search(music)
        else:
            result = self.local_searcher.best_search(music)
        if not result.success:
            result = self.remote_searcher.find_music(music, artist)
        if not result.success:
            return MusicSearchResult(False)
        return MusicSearchResult(True, file_path=result.file_path)
