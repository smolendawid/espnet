# !/usr/bin/python3

import os
import random
import tqdm
import soundfile as sf


def get_all_paths(path, set_name):

    all_sets_paths = []
    tq = tqdm.tqdm(os.walk(path, topdown=False))
    for root, dirs, files in tq:
        for filename in files:
            if filename.endswith('.wav'):

                if set_name not in root:
                    continue

                wav_path = os.path.join(root, filename)
                splitted = wav_path.split('LibriSpeech')
                wav_path = 'LibriSpeech' + splitted[1]

                # f = sf.SoundFile(wav_path)
                # wav_length = len(f) / f.samplerate
                # all_lengths.append(wav_length)

                all_sets_paths.append(wav_path)

    # all_paths_sorted = [x for _, x in sorted(zip(all_lengths, all_paths))]
    return all_sets_paths


def create_dataset(all_sets_paths):
    dataset = []

    results_str = ''
    for src1_ind in tqdm.tqdm(range(len(all_sets_paths))):
        snr = random.random() * 3.

        speaker1 = all_sets_paths[src1_ind].split('-')[-2]

        src2_ind = random.randrange(0, len(all_sets_paths))
        speaker2 = all_sets_paths[src2_ind].split('-')[-2]
        while speaker1 == speaker2:
            src2_ind = random.randrange(0, len(all_sets_paths))
            speaker2 = all_sets_paths[src2_ind].split('-')[-2]

        src1 = all_sets_paths[src1_ind]
        src2 = all_sets_paths[src2_ind]
        dataset.append((src1, snr, src2, snr))
    return dataset


def get_all_transcriptions(path, set_name):
    transcriptions_dict = {}

    tq = tqdm.tqdm(os.walk(path, topdown=False))
    for root, dirs, files in tq:
        for filename in files:

            if set_name not in root:
                continue

            if filename.endswith('.txt'):
                with open(os.path.join(root, filename)) as f:
                    txts = f.read().splitlines()
                for txt in txts:
                    transcriptions_dict[txt.split()[0]] = " ".join(txt.split()[1:])

    return transcriptions_dict


def _repair_snr(snr):
    """ SNR in Octave ommits zeros at the end

    :return:
    """

    snr = "{:.4f}".format(snr)
    while snr.endswith('0'):
        snr = snr[:-1]
    if snr.endswith('.'):
        snr = snr[:-1]

    return snr


def create_paths_str(dataset, set_name, prefix='create-speaker-mixtures/mix_2_spk_'):
    results_str = ''
    for instance in dataset:
        (src1, snr, src2, snr) = instance
        snr = _repair_snr(snr)

        results_str += "{} {} {} -{}\n".format(src1, snr, src2, snr)

    with open(prefix + set_name + '.txt', 'w') as f:
        f.write(results_str)


def create_reference_transcriptions(dataset, transcriptions_dict, set_name, prefix):
    results_str = ''
    for instance in dataset:
        (src1, snr, src2, snr) = instance
        snr = _repair_snr(snr)

        src1 = src1.split('/')[-1][:-4]
        src2 = src2.split('/')[-1][:-4]
        tr1 = transcriptions_dict[src1]
        tr2 = transcriptions_dict[src2]
        line = "{}_{}_{}_-{} {}|{}\n".format(src1, snr, src2, snr, tr1, tr2)
        results_str += line

    with open(prefix + set_name + '.txt', 'w') as f:
        f.write(results_str)


def remove_broken_audio_from_list(path, all_sets_paths):
    """ If audio cannot be read, remove it from list """
    new_all_sets_paths = []
    for wav_path in all_sets_paths:
        try:
            _ = sf.SoundFile(os.path.join(path, wav_path))
        except:
            print("rejected: {}".format(wav_path))
            continue
        new_all_sets_paths.append(wav_path)

    return new_all_sets_paths


if __name__ == '__main__':

    path = '/disks/sda1/dsmolen/'

    random.seed(0)

    sets = ['dev-clean', 'test-clean', 'dev-other', 'test-other',
            'train-clean-100', 'train-clean-360', 'train-other-500']

    for set_name in sets:
        all_sets_paths = get_all_paths(os.path.join(path, 'LibriSpeech'), set_name)

        all_sets_paths = remove_broken_audio_from_list(path, all_sets_paths)
        transcriptions_dict = get_all_transcriptions(os.path.join(path, 'LibriSpeech'), set_name)

        dataset = create_dataset(all_sets_paths)
        create_paths_str(dataset, set_name=set_name, prefix='create-speaker-mixtures/mix_2_spk_')
        create_reference_transcriptions(dataset,
                                        transcriptions_dict=transcriptions_dict,
                                        set_name=set_name,
                                        prefix='create-speaker-mixtures/transcriptions_')
