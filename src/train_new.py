import sys
import time
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
import yaml

from src import DataSet

from src.model.LSTMCTC import LSTMCTC

#from DataSet import read_number_data_sets


train_home_dictionary = '/Users/adamzvada/Documents/School/BP/SpeechRecognition/audio_numbers'

# HYPER PARAMETERS

# mfcc
# num_features =  247
num_features = 13
num_context = 4


# Accounting the 0th index +  space + blank label = 28 characters
num_classes = ord('z') - ord('a') + 1 + 1 + 1
num_epoches = 100
num_hidden = 100
num_layers = 3
batch_size = 8

FIRST_INDEX = ord('a') - 1  # 0 is reserved to space

tf.logging.set_verbosity(tf.logging.INFO)

logs_path = "./tensorboard"


def train_network(dataset):

    graph = tf.Graph()

    lstm_ctc = LSTMCTC(num_hidden, num_layers, num_classes, num_features)
    lstm_ctc.define()
    loss_operation = lstm_ctc.loss_funtion()
    optimizer_operation = lstm_ctc.train_optimizer()
    decode_operation = lstm_ctc.decoder()
    ler_operation = lstm_ctc.compute_label_error_rate(decode_operation)

    # set TF logging verbosity
    tf.logging.set_verbosity(tf.logging.INFO)

    with tf.Session() as session:

        session.run(tf.global_variables_initializer())

        writer = tf.summary.FileWriter(logs_path, graph=session.graph)

        for epoch in range(num_epoches):

            epoch_loss = 0
            ler_loss = 0

            start = time.time()

            current_state = np.zeros((num_layers, 2, batch_size, num_hidden))

            for batch in range(int(dataset.train.num_examples / batch_size)):

                #summary_op = tf.summary.merge(lstm_ctc.summaries)
                summary_op = tf.summary.merge_all()

                train_x, train_y_sparse, train_sequence_length = dataset.train.next_batch(batch_size)

                feed = {
                    lstm_ctc.input_placeholder : train_x,
                    lstm_ctc.label_sparse_placeholder : train_y_sparse,
                    lstm_ctc.input_seq_len_placeholder : train_sequence_length,
                }

                batch_cost, _, summary = session.run([loss_operation, optimizer_operation, summary_op], feed)
                #batch_cost, _, _, summary = session.run([cost, optimizer, state, summary_op], feed)

                epoch_loss += batch_cost * batch_size

                writer.add_summary(summary, epoch * batch_size + batch)

                ler_loss += session.run(ler_operation, feed) * batch_size

                # Decoding
                d = session.run(decode_operation, feed_dict=feed)
                str_decoded = ''.join([chr(x) for x in np.asarray(d[1]) + FIRST_INDEX])
                # Replacing blank label to none
                str_decoded = str_decoded.replace(chr(ord('z') + 1), '')
                # Replacing space label to space
                str_decoded = str_decoded.replace(chr(ord('a') - 1), ' ')

                print('Decoded: %s' % str_decoded)

            epoch_loss /= dataset.train.num_examples
            ler_loss /= dataset.train.num_examples

            log = "Epoch {}/{}, train_cost = {:.3f}, train_ler = {:.3f}, " \
                  "val_cost = {:.3f}, val_ler = {:.3f}, time = {:.3f}"

            print(log.format(epoch + 1, num_epoches, epoch_loss, ler_loss,
                             0, 0, time.time() - start))


def main(config_path=None):

    if config_path is None:
        print("Processing default config.")

        dataset = DataSet.read_number_data_sets(train_home_dictionary)

        train_network(dataset)
    else:
        print("Processing CONFIG in filename: %s", config_path)

        with open(config_path, 'r') as f:
            config = yaml.load(f)

            model_name = config_path['model_name']
            corpus = config_path['corpus']



if __name__ == "__main__":
    args = sys.argv
    if len(args) == 2:
        main(config_path=args[1])
    else:
        main()

