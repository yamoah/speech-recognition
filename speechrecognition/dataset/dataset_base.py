import numpy as np
import tensorflow as tf
import pickle
from tqdm import tqdm
import random

from speechrecognition.utils import audio_utils, text_utils

class DatasetBase(object):
    """
    Base class for datasets operation.
    """

    def __init__(self, num_features, num_context):
        """
        Initializer of DatasetBase object
        :param int num_features: size of feature vector
        :param num_context: NOT USED...
        """
        self._audio_filenames = []
        self._label_filenames = []
        self._num_examples = 0

        self.num_features = num_features
        self.num_context = num_context

        self._index_in_epoch = 0
        self._epochs_completed = 0


    # TODO: override this method
    def read_dataset(self):
        raise NotImplemented

    def train_dataset(self):
        """
        Returns the train targets for the model in wanted format.

        :return: tuple of (x, sparse_label, x_length)
        """
        return self.transform_to_speech_targets(self._train_audios, self._train_labels)

    def test_dataset(self):
        """
        Returns the train targets for the model in wanted format.

        :return: tuple of (x, sparse_label, x_length)
        """
        return self.transform_to_speech_targets(self._test_audios, self._test_labels)

    def transform_to_speech_targets(self, audios, labels):
        """
        Transorms the two inputs to training model acceptable forms.
        For labels it create sparse matrix and pads the audio sequence to same length.

        :param np.ndarray audios: dataset audios
        :param np.ndarray labels: labels as transcription of audios
        :return: tuple of (x, sparse_label, x_length)
        """
        if not isinstance(labels, np.ndarray):
            raise Exception('Labels needs to be of type numpy arrays...')
        if not isinstance(audios, np.ndarray):
            raise Exception('Audios needs to be of type numpy arrays...')

        y_sparse = text_utils.sparse_tuple_from(labels)

        # pad audio batch
        x, x_length = audio_utils.pad_sequences(audios)

        return x, y_sparse, x_length

    def shuffle(self, x, y, seed):
        """
        Shuffles the x and y in same order.

        :param x: audio features
        :param y: sparse labels
        :param seed: random seed value
        :return: tuple of shuffled x, y
        """

        files = list(zip(x, y))
        random.seed(seed)
        random.shuffle(files)
        x, y = zip(*files)

        return x, y

    def next_batch(self, batch_size):
        """"
        Deprecated: use tf.data.dataset batching
        Returns from Datset batch of audios for training/testing of batch_size
        """

        if batch_size > self._num_examples:
            raise ValueError('Batch size cannot be greather then number of examples in dataset')

        start = self._index_in_epoch
        self._index_in_epoch += batch_size

        audio_filenames_batch = []
        label_filenames_batch = []

        if self._index_in_epoch > self._num_examples:
            # count finished epoches
            self._epochs_completed += 1

            # perfrom shuffle
            files = list(zip(self._audios, self._labels))
            random.shuffle(files)
            self._audios, self._labels= zip(*files)

            # start next epoch
            start = 0

            self._index_in_epoch = batch_size

        end = self._index_in_epoch

        audios_batch = self._audios[start:end]
        labels_batch = self._labels[start:end]

        output_target = np.asarray(labels_batch)
        sparse_targets = text_utils.sparse_tuple_from(output_target)

        # pad audio batch
        train_input, train_length = audio_utils.pad_sequences(audios_batch)

        return train_input, sparse_targets, train_length


    def next_batch_and_preprocess(self, batch_size):
        """"
        Deprecated: use tf.data.dataset batching
        Returns from Datset batch of audios for training/testing of batch_size
        """

        if batch_size > self._num_examples:
            raise ValueError('Batch size cannot be greather then number of examples in dataset')

        start = self._index_in_epoch
        self._index_in_epoch += batch_size


        if self._index_in_epoch > self._num_examples:
            # count finished epoches
            self._epochs_completed += 1

            # perfrom shuffle
            files = list(zip(self._audio_filenames, self._label_filenames))
            random.shuffle(files)
            self._audio_filenames, self._label_filenames= zip(*files)

            # start next epoch
            start = 0

            self._index_in_epoch = batch_size

        end = self._index_in_epoch

        audios = []
        labels = []

        print("Preprocessing audio files for batch of size", batch_size)

        for audio_filename, label_filename in tqdm(zip(self._audio_filenames[start:end], self._label_filenames[start:end]), total=(end - start)):
            audio_features = audio_utils.audiofile_to_input_vector(audio_filename, self.num_features, self.num_context)

            text_target = text_utils.get_refactored_transcript(label_filename, is_filename=True, is_digit=False)

            audios.append(audio_features)
            labels.append(text_target)

        output_target = np.asarray(labels)
        sparse_targets = text_utils.sparse_tuple_from(output_target)

        # pad audio batch
        train_input, train_length = audio_utils.pad_sequences(audios)

        return train_input, sparse_targets, train_length

    def load_pickle_dataset(self, name_dataset):
        """
        Loads from pickle file variables for audio and it's label transcription.
        :param str name_dataset: Path datset
        """

        with open(name_dataset + '_audios', 'rb') as f:
            self._audios = pickle.load(f)

        with open(name_dataset + '_labeles', 'rb') as f:
            self._labels = pickle.load(f)

    def save_pickle_dataset(self, name_dataset):
        """
        Save to pickle file variables for audio and it's label transcription.
        :param str name_dataset: Path datset
        """
        # sfile = bz2.BZ2File('smallerfile', 'w')

        with open(name_dataset + '_audios', 'wb') as f:
            pickle.dump(self.audios, f)

        with open(name_dataset + '_labeles', 'wb') as f:
            pickle.dump(self.labels, f)



