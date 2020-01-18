import os
from pathlib import Path
from spleeter.separator import Separator


class VoiceRemover:
    
    def __init__(self):
        os.environ['KMP_WARNINGS'] = 'off'
        self.separator = Separator(
            params_descriptor='spleeter:2stems',
            descriptor_config={
                'per_process_gpu_memory_fraction': 0.05,
                'intra_op_parallelism_threads': 2,
                'inter_op_parallelism_threads': 1
            })

    def remove(self, file_path, file_name, file_codac):
        future_path = file_path + '/'
        Path(future_path).mkdir(parents=True, exist_ok=True)
        real_file_path = file_path + '/' + file_name + '.' + file_codac
        self.separator.separate_to_file(real_file_path, future_path, synchronous=False, codec=file_codac)
