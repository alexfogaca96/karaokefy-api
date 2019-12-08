from spleeter.separator import Separator


class VoiceRemover:
    
    def __init__(self):
        self.separator = Separator('spleeter:2stems')

    def remove(self, audio_path):
        self.separator.separate_to_file(audio_path, 'output', synchronous=False)
