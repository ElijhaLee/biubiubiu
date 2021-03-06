from other_functions import *


def _construct(input_tensor, name, reuse):
    with tf.variable_scope(name, reuse):
        # 224, 1
        net = ly.conv2d(input_tensor, num_outputs=64, kernel_size=4, stride=2, normalizer_fn=None,
                        activation_fn=leaky_relu,
                        weights_initializer=tf.random_normal_initializer(stddev=STDDEV))
        # 112, 64
        net = ly.conv2d(net, num_outputs=128, kernel_size=4, stride=2, normalizer_fn=ly.batch_norm,
                        activation_fn=leaky_relu,
                        weights_initializer=tf.random_normal_initializer(stddev=STDDEV))
        # 56, 128
        net = ly.conv2d(net, num_outputs=256, kernel_size=4, stride=2, normalizer_fn=ly.batch_norm,
                        activation_fn=leaky_relu,
                        weights_initializer=tf.random_normal_initializer(stddev=STDDEV))
        # 28, 256
        net = ly.conv2d(net, num_outputs=256, kernel_size=3, stride=2, normalizer_fn=ly.batch_norm,
                        activation_fn=leaky_relu,
                        weights_initializer=tf.random_normal_initializer(stddev=STDDEV))
        # 14, 256
        net = ly.conv2d(net, num_outputs=512, kernel_size=3, stride=2, normalizer_fn=ly.batch_norm,
                        activation_fn=leaky_relu,
                        weights_initializer=tf.random_normal_initializer(stddev=STDDEV))
        # 7, 512
        net = ly.conv2d(net, num_outputs=256, kernel_size=2, stride=1, normalizer_fn=ly.batch_norm,
                        activation_fn=leaky_relu,
                        weights_initializer=tf.random_normal_initializer(stddev=STDDEV))
        # 14, 256
        net = ly.conv2d_transpose(net, num_outputs=128, kernel_size=3, stride=2, activation_fn=leaky_relu,
                                  normalizer_fn=ly.batch_norm,
                                  weights_initializer=tf.random_normal_initializer(stddev=STDDEV))
        # 14, 128
        net = ly.conv2d_transpose(net, num_outputs=64, kernel_size=3, stride=2, activation_fn=leaky_relu,
                                  normalizer_fn=ly.batch_norm,
                                  weights_initializer=tf.random_normal_initializer(stddev=STDDEV))
        # 28, 64
        net = ly.conv2d_transpose(net, num_outputs=1, kernel_size=3, stride=1, activation_fn=tf.nn.sigmoid,
                                  normalizer_fn=None,
                                  weights_initializer=tf.random_normal_initializer(stddev=STDDEV))
        # 28, 1

    return net


class Generator():
    def __init__(self, input_tensor, name, reuse=False):
        with tf.name_scope(name):
            self.generated_img = _construct(input_tensor, name, reuse)
            self.variables = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=name)

            tf.summary.image('cervix',input_tensor,max_outputs=BATCH_SIZE)
            self.summaries = tf.get_collection(tf.GraphKeys.SUMMARIES,scope=name)   # 生成的图片也summary


class GeneratorOptimizer():
    def __init__(self, generator, discriminator_list, learning_rate, name):
        with tf.name_scope(name):
            real_type=0
            self.global_step = tf.Variable(1, trainable=False, name='global_step')
            loss = -discriminator_list[real_type].score_fake    #(batch_size,1)
            self.variables = generator.variables
            self.optimizer = self._create_optimizer(loss, real_type, learning_rate)
            self.summaries = tf.get_collection(tf.GraphKeys.SUMMARIES, scope=name)  # 这里也包括了Generator里面的summary

    def _create_optimizer(self,loss, real_type, learning_rate):
        loss = tf.reduce_mean(loss)
        # tf.summary.scalar('loss~'+str(real_type),loss)
        # g. matmul's oprand must be rank 2!
        # loss = tf.matmul(tf.convert_to_tensor([loss]),  # [1,3]
        #                  2 * (label - 0.5), transpose_b=True)  # [1.3]
        # cross_entropy = tf.nn.softmax_cross_entropy_with_logits(labels=label,
        #                                                         logits=[1 / tf.reduce_mean(score_fake[0]),
        #                                                                 1 / tf.reduce_mean(score_fake[1]),
        #                                                                 1 / tf.reduce_mean(score_fake[2])])
        # loss = tf.reshape(loss, shape=()) + cross_entropy  # ()
        # loss = tf.reshape(loss, shape=())  # ()
        optimizer = ly.optimize_loss(loss=loss, global_step=self.global_step, learning_rate=learning_rate,
                                     optimizer=tf.train.RMSPropOptimizer, variables=self.variables,
                                     summaries=OPTIMIZER_SUMMARIES)

        # tf.summary.scalar('cross_entropy', tf.reduce_mean(cross_entropy))

        return optimizer
