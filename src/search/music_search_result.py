
class MusicSearchResult:
    def __init__(self, success, **kwargs):
        self.success = success
        self.file_path = kwargs.get('file_path', None)
        self.file_name = kwargs.get('file_name', None)
        self.file_codac = kwargs.get('file_codac', None)
