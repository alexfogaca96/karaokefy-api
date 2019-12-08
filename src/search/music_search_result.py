
class MusicSearchResult:

    def __init__(self, success, **kwargs):
        self.success = success
        self.file_path = kwargs.get('file_path', None)
