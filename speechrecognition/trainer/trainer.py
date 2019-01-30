from speechrecognition.trainer.base_train import BaseTrain
from speechrecognition.utils import text_utils


class SpeechTrainer(BaseTrain):

    def __init__(self, session, model, dataset, config):
        super(SpeechTrainer, self).__init__(session, model, dataset, config)

    def train_epoch(self, cur_epoche):
        num_iterations = self.config.num_iterations()

        mean_loss = 0
        mean_error = 0
        for i in range(num_iterations):
            decoded, loss, error = self.train_step()
            mean_loss += loss
            mean_error += error

            if i % 10 == 0:
                step_num = cur_epoche*num_iterations + i
                decoded_str = self.decode_transcript(decoded)
                self.log_progress(input=(decoded_str, loss, error), num_iteration=step_num, mode='train')

        mean_loss /= num_iterations
        mean_error /= num_iterations

        decoded_str = self.decode_transcript(decoded)

        return decoded_str, mean_loss, mean_error

    def train_step(self):

        loss, _, decoded, error = self.session.run([
            self.model.loss, self.model.optimizer, self.model.decoder, self.model.label_error
        ], feed_dict={
            self.model.dropout_placeholder: self.config.dropout_prob(),
            self.iterator.handle_placeholder: self.train_handle
        })

        # increase global step counter
        self.session.run(self.model.increment_global_step_tensor)

        return decoded, loss, error

    def test_step(self):

        loss, decoded, error = self.session.run([
            self.model.loss, self.model.decoder, self.model.label_error
        ], feed_dict={
            self.model.dropout_placeholder: 1,
            self.iterator.handle_placeholder: self.test_handle
        })

        decoded_str = self.decode_transcript(decoded)

        return decoded_str, loss, error

    def log_progress(self, input, num_iteration, mode):

        summaries_dict = {
            'text': input[0],
            'loss': input[1],
            'error': input[2],
        }

        self.logger.log_scalars(num_iteration, summarizer=mode, summaries_dict=summaries_dict)

    def update_progress_bar(self, t_bar, train_input, test_input):

        # Log the loss in the tqdm progress bar
        t_bar.set_postfix(
            #decoded=f'{train_input[0]}',
            train_loss='{:05.3f}'.format(train_input[1]),
            train_error='{:05.3f}'.format(train_input[2]),
            test_loss='{:05.3f}'.format(test_input[1]),
            test_error='{:05.3f}'.format(test_input[2]),
        )

    def decode_transcript(self, decode_sparse):

        decoded_str = text_utils.index_to_text(decode_sparse[1])

        return decoded_str