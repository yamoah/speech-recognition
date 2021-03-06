import numpy as np
import math
import librosa
import scipy.io.wavfile as wav
import python_speech_features as sf
from sklearn.preprocessing import scale


# TODO: refactoring to ctc format will be requierd (sparse_tuple)
def audiofile_to_input_vector(wav_filename, numcep, numcontext):
    """
    Returns audio and its transcripts. Audio is preprocessed by MFCC.
    :param wav_filename:
    :param int numcep: feature size vector
    :param int numcontext: not used
    :return: ndarray of shape (numcep, num_vectors)
    """
    # load wav file and downsamples it to 16khz
    signal, sample_rate = librosa.load(wav_filename, sr=16000)
    #sample_rate, signal = wav.read(wav_filename)

    # Applying mffc transformation to get feature vector
    mfcc_features = sf.mfcc(signal, sample_rate)

    # Swaping axes so first we get number of elements in vector(numcep) and the number of vectors
    #mfcc_features = np.swapaxes(mfcc_features, 0, 1)

    # normalization?
    mfcc_features = scale(mfcc_features, axis=1)

    return mfcc_features


def pad_sequences(sequences, maxlen=None, dtype=np.float32,
                  padding='post', truncating='post', value=0.):
    """
    From TensorLayer: http://tensorlayer.readthedocs.io/en/latest/_modules/tensorlayer/prepro.html
    Pads each sequence to the same length of the longest sequence.
    If maxlen is provided, any sequence longer than maxlen is truncated to
    maxlen. Truncation happens off either the beginning or the end
    (default) of the sequence. Supports post-padding (default) and
    pre-padding.

    :param list sequences: list of lists where each element is a sequence
    :param int maxlen: maximum length
    :param type dtype: type to cast the resulting sequence.
    :param str padding: 'pre' or 'post', pad either before or after each sequence.
    :param str truncating: 'pre' or 'post', remove values from sequences larger
    :param float value: value to pad the sequences to the desired value.
    :return: numpy.ndarray: Padded sequences shape = (number_of_sequences, maxlen)
             numpy.ndarray: original sequence lengths
    """
    lengths = np.asarray([len(s) for s in sequences], dtype=np.int64)

    nb_samples = len(sequences)
    if maxlen is None:
        maxlen = np.max(lengths)

    # take the sample shape from the first non empty sequence
    # checking for consistency in the main loop below.
    sample_shape = tuple()
    for s in sequences:
        if len(s) > 0:
            sample_shape = np.asarray(s).shape[1:]
            break

    x = (np.ones((nb_samples, maxlen) + sample_shape) * value).astype(dtype)
    for idx, s in enumerate(sequences):
        if len(s) == 0:
            continue  # empty list was found
        if truncating == 'pre':
            trunc = s[-maxlen:]
        elif truncating == 'post':
            trunc = s[:maxlen]
        else:
            raise ValueError('Truncating type "%s" not understood' % truncating)

        # check `trunc` has expected shape
        trunc = np.asarray(trunc, dtype=dtype)
        if trunc.shape[1:] != sample_shape:
            raise ValueError('Shape of sample %s of sequence at position %s is different from expected shape %s' %
                             (trunc.shape[1:], idx, sample_shape))

        if padding == 'post':
            x[idx, :len(trunc)] = trunc
        elif padding == 'pre':
            x[idx, -len(trunc):] = trunc
        else:
            raise ValueError('Padding type "%s" not understood' % padding)
    return x, lengths


# def audiofile_to_input_vector(audio_filename, numcep, numcontext):
#     '''
#     Turn an audio file into feature representation.
#     This function has been modified from Mozilla DeepSpeech:
#     https://github.com/mozilla/DeepSpeech/blob/master/util/audio.py
#     # This Source Code Form is subject to the terms of the Mozilla Public
#     # License, v. 2.0. If a copy of the MPL was not distributed with this
#     # file, You can obtain one at http://mozilla.org/MPL/2.0/.
#     '''
#     fs, audio = wav.read(audio_filename)
#
#     # Get mfcc coefficients
#     features = sf.mfcc(audio, samplerate=fs, numcep=numcep)
#
#     # We only keep every second feature (BiRNN stride = 2)
#     features = features[::2]
#
#     plt.figure(figsize=(12 / 2, 4 / 2))
#     display.specshow(np.swapaxes(features, 0, 1), sr=fs, x_axis='time', y_axis='mel')
#     #display.specshow(features, sr=fs, x_axis='time', y_axis='mel')
#     #plt.plot(features)
#     plt.title('MFCC_ORIG')
#     plt.colorbar()
#     plt.tight_layout()
#
#
#     # One stride per time step in the input
#     num_strides = len(features)
#
#     # Add empty initial and final contexts
#     empty_context = np.zeros((numcontext, numcep), dtype=features.dtype)
#     features = np.concatenate((empty_context, features, empty_context))
#
#     # Create a view into the array with overlapping strides of size
#     # numcontext (past) + 1 (present) + numcontext (future)
#     window_size = 2 * numcontext + 1
#     train_inputs = np.lib.stride_tricks.as_strided(
#         features,
#         (num_strides, window_size, numcep),
#         (features.strides[0], features.strides[0], features.strides[1]),
#         writeable=False)
#
#     # Flatten the second and third dimensions
#     train_inputs = np.reshape(train_inputs, [num_strides, -1])
#
#     # Whiten inputs (TODO: Should we whiten?)
#     # Copy the strided array so that we can write to it safely
#     train_inputs = np.copy(train_inputs)
#     train_inputs = (train_inputs - np.mean(train_inputs)) / np.std(train_inputs)
#
#     plt.figure(figsize=(12 / 2, 4 / 2))
#     display.specshow(np.swapaxes(train_inputs, 0, 1), sr=fs, x_axis='time', y_axis='mel')
#     #display.specshow(train_inputs, sr=fs, x_axis='time', y_axis='mel')
#     #plt.plot(orig_inputs)
#     plt.title('MFCC_ORIG')
#     plt.colorbar()
#     plt.tight_layout()
#
#
#     # Return results
#     return train_inputs



# def audiofile_to_input_vector(audio_filename, numcep, numcontext):
#     '''
#     Turn an audio file into feature representation.
#     This function has been modified from Mozilla DeepSpeech:
#     https://github.com/mozilla/DeepSpeech/blob/master/util/audio.py
#     # This Source Code Form is subject to the terms of the Mozilla Public
#     # License, v. 2.0. If a copy of the MPL was not distributed with this
#     # file, You can obtain one at http://mozilla.org/MPL/2.0/.
#     '''
#
#     # Load wav files
#     fs, audio = wav.read(audio_filename)
#
#     # Get mfcc coefficients
#     #orig_inputs = sf.mfcc(audio, samplerate=fs, numcep=numcep)
#     orig_inputs = sf.mfcc(audio, samplerate=fs, numcep=numcep)
#
#     plt.figure(figsize=(12 / 2, 4 / 2))
#     #display.specshow(np.swapaxes(orig_inputs, 0, 1), sr=fs, x_axis='time', y_axis='mel')
#     plt.plot(orig_inputs)
#     plt.title('MFCC_ORIG')
#     # plt.colorbar()
#     # plt.tight_layout()
#
#     # We only keep every second feature (BiRNN stride = 2)
#     orig_inputs = orig_inputs[::2]
#
#     # For each time slice of the training set, we need to copy the context this makes
#     # the numcep dimensions vector into a numcep + 2*numcep*numcontext dimensions
#     # because of:
#     #  - numcep dimensions for the current mfcc feature set
#     #  - numcontext*numcep dimensions for each of the past and future (x2) mfcc feature set
#     # => so numcep + 2*numcontext*numcep
#     train_inputs = np.array([], np.float32)
#     train_inputs.resize((orig_inputs.shape[0], numcep + 2 * numcep * numcontext))
#
#     # Prepare pre-fix post fix context
#     empty_mfcc = np.array([])
#     empty_mfcc.resize((numcep))
#
#     # Prepare train_inputs with past and future contexts
#     time_slices = range(train_inputs.shape[0])
#     context_past_min = time_slices[0] + numcontext
#     context_future_max = time_slices[-1] - numcontext
#     for time_slice in time_slices:
#         # Reminder: array[start:stop:step]
#         # slices from indice |start| up to |stop| (not included), every |step|
#
#         # Add empty context data of the correct size to the start and end
#         # of the MFCC feature matrix
#
#         # Pick up to numcontext time slices in the past, and complete with empty
#         # mfcc features
#         need_empty_past = max(0, (context_past_min - time_slice))
#         empty_source_past = list(empty_mfcc for empty_slots in range(need_empty_past))
#         data_source_past = orig_inputs[max(0, time_slice - numcontext):time_slice]
#         assert(len(empty_source_past) + len(data_source_past) == numcontext)
#
#         # Pick up to numcontext time slices in the future, and complete with empty
#         # mfcc features
#         need_empty_future = max(0, (time_slice - context_future_max))
#         empty_source_future = list(empty_mfcc for empty_slots in range(need_empty_future))
#         data_source_future = orig_inputs[time_slice + 1:time_slice + numcontext + 1]
#         assert(len(empty_source_future) + len(data_source_future) == numcontext)
#
#         if need_empty_past:
#             past = np.concatenate((empty_source_past, data_source_past))
#         else:
#             past = data_source_past
#
#         if need_empty_future:
#             future = np.concatenate((data_source_future, empty_source_future))
#         else:
#             future = data_source_future
#
#         past = np.reshape(past, numcontext * numcep)
#         now = orig_inputs[time_slice]
#         future = np.reshape(future, numcontext * numcep)
#
#         train_inputs[time_slice] = np.concatenate((past, now, future))
#         assert(len(train_inputs[time_slice]) == numcep + 2 * numcep * numcontext)
#
#     plt.figure(figsize=(12 / 2, 4 / 2))
#     plt.plot(train_inputs)
#     #display.specshow(np.swapaxes(train_inputs, 0, 1), sr=fs, x_axis='time', y_axis='mel')
#     plt.title('MFCC')
#     # plt.colorbar()
#     # plt.tight_layout()
#
#     # Scale/standardize the inputs
#     # This can be done more efficiently in the TensorFlow graph
#     train_inputs = (train_inputs - np.mean(train_inputs)) / np.std(train_inputs)
#
#     return train_inputs



# def stack_frame(input_list, num_stack, num_skip, progressbar=False):
#     """Stack & skip some frames. This implementation is based on
#        https://arxiv.org/abs/1507.06947.
#            Sak, Hasim, et al.
#            "Fast and accurate recurrent neural network acoustic models for speech recognition."
#            arXiv preprint arXiv:1507.06947 (2015).
#     Args:
#         input_list (list): list of input data
#         num_stack (int): the number of frames to stack
#         num_skip (int): the number of frames to skip
#         progressbar (bool, optional): if True, visualize progressbar
#     Returns:
#         input_list_new (list): list of frame-stacked inputs
#     """
#     if num_stack == 1 and num_stack == 1:
#         return input_list
#
#     if num_stack < num_skip:
#         raise ValueError('num_skip must be less than num_stack.')
#
#     batch_size = len(input_list)
#
#     input_list_new = []
#     #for i_batch in wrap_iterator(range(batch_size), progressbar):
#     for i_batch in range(batch_size):
#
#         frame_num, input_size = input_list[i_batch].shape
#         frame_num_new = math.ceil(frame_num / num_skip)
#
#         stacked_frames = np.zeros((frame_num_new, input_size * num_stack))
#         stack_count = 0  # counter
#         stack = []
#         for t, frame_t in enumerate(input_list[i_batch]):
#             #####################
#             # final frame
#             #####################
#             if t == len(input_list[i_batch]) - 1:
#                 # Stack the final frame
#                 stack.append(frame_t)
#
#                 while stack_count != int(frame_num_new):
#                     # Concatenate stacked frames
#                     for i_stack in range(len(stack)):
#                         stacked_frames[stack_count][input_size *
#                                                     i_stack:input_size * (i_stack + 1)] = stack[i_stack]
#                     stack_count += 1
#
#                     # Delete some frames to skip
#                     for _ in range(num_skip):
#                         if len(stack) != 0:
#                             stack.pop(0)
#
#             ########################
#             # first & middle frames
#             ########################
#             elif len(stack) < num_stack:
#                 # Stack some frames until stack is filled
#                 stack.append(frame_t)
#
#                 if len(stack) == num_stack:
#                     # Concatenate stacked frames
#                     for i_stack in range(num_stack):
#                         stacked_frames[stack_count][input_size *
#                                                     i_stack:input_size * (i_stack + 1)] = stack[i_stack]
#                     stack_count += 1
#
#                     # Delete some frames to skip
#                     for _ in range(num_skip):
#                         stack.pop(0)
#
#         input_list_new.append(stacked_frames)
#
#     return np.array(input_list_new)