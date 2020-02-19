# !/usr/bin/python3

import os
import tqdm
from sox import Transformer

SAMPLE_RATE = 16000
remove_flac = False
path = '/home/dsmolen/agh/LibriSpeech/'

i = 0
tq = tqdm.tqdm(os.walk(path, topdown=False))
for root, dirs, files in tq:
    for name in files:
        if name.endswith('.flac'):
            tq.set_postfix(converted=i)
            i += 1
            name = name[:-5]
            flac_file = os.path.join(root, name + ".flac")
            wav_file = os.path.join(root, name + ".wav")
            if not os.path.exists(wav_file):
                tfm = Transformer()
                tfm.set_output_format(rate=SAMPLE_RATE)
                tfm.build(flac_file, wav_file)
            if remove_flac:
                os.remove(flac_file)
