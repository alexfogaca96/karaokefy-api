from pathlib import Path
from spleeter.separator import Separator


class VoiceRemover:
    
    def __init__(self):
        self.separator = Separator('spleeter:2stems')

    def remove(self, file_path, file_name, file_codac):
        future_path = file_path + '/' + file_name + '_dir'
        Path(future_path).mkdir(parents=True, exist_ok=True)
        real_file_path = file_path + '/' + file_name + file_codac
        self.separator.separate_to_file(real_file_path, future_path, synchronous=False, codec='.wav')
