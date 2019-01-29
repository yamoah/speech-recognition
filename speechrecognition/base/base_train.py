import os
import tensorflow as tf
from tqdm import trange
from speechrecognition.helper.tensor_logger import TensorLogger

class BaseTrain(object):

    def __init__(self, session, model, dataset, config):
        self.session = session
        self.model = model
        self.dataset = dataset
        self.config = config

    def train(self):

        model_inputs = self.prepare_dataset()

        self.model.build_model(model_inputs)

        self.init = tf.group(tf.global_variables_initializer(), tf.local_variables_initializer())
        self.session.run(self.init)

        logger = TensorLogger(log_path=self.config.get_tensorboard_logs_path(), session=self.session)

        # tqdm progress bar looping through all epoches
        t_epoches = trange(self.model.cur_epoch_tensor.eval(self.session), self.config.num_epoches() + 1, 1,
                           desc=f'Training {self.config.model_name()}')
        for cur_epoch in t_epoches:
            # run epoch training
            decoded, mean_loss, mean_error = self.train_epoch()

            # Log the loss in the tqdm progress bar
            t_epoches.set_postfix(
                decoded=f'{decoded}',
                epoch_mean_loss='{:05.3f}'.format(mean_loss),
                epoch_mean_error='{:05.3f}'.format(mean_error)
            )

            # log scalars to tensorboard
            summaries_dict = {
                'mean_loss': mean_loss,
                'mean_error': mean_error,
            }
            logger.log_scalars(cur_epoch, summaries_dict=summaries_dict)

            # increase epoche counter
            self.session.run(self.model.increment_cur_epoch_tensor)

    def train_epoch(self):
        raise NotImplementedError

    def train_step(self):
        raise NotImplementedError

    def prepare_dataset(self):
        raise NotImplementedError
