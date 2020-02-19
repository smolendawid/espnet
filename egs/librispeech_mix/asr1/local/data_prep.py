import argparse
import os
import shutil
import tqdm
import collections

"""
103-1240-0000 CHAPTER ONE MISSUS RACHEL LYNDE IS SURPRISED MISSUS RACHEL LYNDE LIVED JUST WHERE THE AVONLEA MAIN ROAD DIPPED DOWN INTO A LITTLE HOLLOW FRINGED WITH ALDERS AND LADIES EARDROPS AND TRAVERSED BY A BROOK
103-1240-0000 CHAPTER ONE MISSUS RACHEL LYNDE IS SURPRISED MISSUS RACHEL LYNDE LIVED JUST WHERE THE AVONLEA MAIN ROAD DIPPED DOWN INTO A LITTLE HOLLOW FRINGED WITH ALDERS AND LADIES EARDROPS AND TRAVERSED BY A BROOK

103-1240-0000 flac -c -d -s /home/dsmolen/agh//LibriSpeech/train-clean-100/103/1240/103-1240-0000.flac |
103-1240-0001 flac -c -d -s /home/dsmolen/agh//LibriSpeech/train-clean-100/103/1240/103-1240-0001.flac |

"""


def data_prep(src_dir, trg_dir='data/'):
    if not os.path.exists(os.path.join(trg_dir)):
        os.mkdir(os.path.join(trg_dir))

    sets = ['dev-clean', 'test-clean', 'dev-other', 'test-other', 'train-clean-100',
            'train-clean-360', 'train-other-500']
    for set_name in sets:
        if not os.path.exists(os.path.join(trg_dir, set_name.replace('-', '_'))):
            os.mkdir(os.path.join(trg_dir, set_name.replace('-', '_')))
        filenames = []
        roots = []
        tq = tqdm.tqdm(os.walk(os.path.join(src_dir, set_name, 'mix'), topdown=False))
        for root, dirs, files in tq:
            for filename in files:
                if filename.endswith('.wav'):
                    filenames.append(filename)
                    roots.append(root)

        wav_scp_list = []
        for root, filename in zip(roots, filenames):
            wav_scp_list.append("{} {}\n".format(filename[:-4], os.path.join(root, filename)))
        wav_scp_list = sorted(wav_scp_list)

        wav_scp = ''
        for wav in wav_scp_list:
            wav_scp += wav

        with open(os.path.join(trg_dir, set_name.replace('-', '_'), 'wav.scp'), 'w') as f:
            f.write(wav_scp)

        with open('../local/create-speaker-mixtures/transcriptions_{}.txt'.format(set_name)) as f:
            texts = f.read().splitlines()

        text_names = []
        for t in texts:
            text_names.append(t.split()[0])

        texts_sorted = [x for _, x in sorted(zip(text_names, texts))]

        with open(os.path.join(trg_dir, set_name.replace('-', '_'), 'text'), 'w') as f:
            for line in texts_sorted:
                n = line.split()[0]
                t1 = " ".join(line.split()[1:]).split('|')[0]
                f.write(n + ' ' + t1 + '\n')

        with open(os.path.join(trg_dir, set_name.replace('-', '_'), 'text_spk1'), 'w') as f1:
            with open(os.path.join(trg_dir, set_name.replace('-', '_'), 'text_spk2'), 'w') as f2:
                for line in texts_sorted:
                    n = line.split()[0]
                    t1 = " ".join(line.split()[1:]).split('|')[0]
                    t2 = line.split('|')[1]
                    f1.write(n + ' ' + t1 + '\n')
                    f2.write(n + ' ' + t2 + '\n')

        utt2spk = ''
        spk2utt = ''
        spk2utt_dict = {}
        for text_name in sorted(text_names):
            splitted = text_name.split('_')
            sentence1 = splitted[0]
            sentence2 = splitted[2]
            speaker1 = "-".join(sentence1.split('-')[:2])
            speaker2 = "-".join(sentence2.split('-')[:2])

            utt2spk += "{} {}\n".format(text_name, speaker1)
            if speaker1 not in spk2utt_dict:
                spk2utt_dict[speaker1] = []
            if speaker2 not in spk2utt_dict:
                spk2utt_dict[speaker2] = []
            spk2utt_dict[speaker1].append(text_name)
            # spk2utt_dict[speaker2].append(text_name)

        spk2utt_dict = collections.OrderedDict(sorted(spk2utt_dict.items()))

        for speaker, utterances in spk2utt_dict.items():
            spk2utt += speaker
            for utterance in utterances:
                spk2utt += ' ' + utterance
            spk2utt += '\n'

        with open(os.path.join(trg_dir, set_name.replace('-', '_'), 'spk2utt'), 'w') as f:
            f.write(spk2utt)
        with open(os.path.join(trg_dir, set_name.replace('-', '_'), 'utt2spk'), 'w') as f:
            f.write(utt2spk)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("src_dir", help="")
    parser.add_argument("trg_dir", help="")
    args = parser.parse_args()

    data_prep(src_dir=args.src_dir, trg_dir=args.trg_dir, )
