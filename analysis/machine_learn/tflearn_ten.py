""" An example showing how to save/restore models and retrieve weights. """

from __future__ import absolute_import, division, print_function

import unittest
import numpy as np
import pandas
import pandas as pd
import tflearn
import tensorflow as tf


class MyTestCase(unittest.TestCase):
    def test_train_model(self):
        pickle = pandas.read_pickle('select_col_fillna0_learn.pkl')
        pickle.info()
        # 将    thal    列（数据帧（dataframe）中的    object ）转换为离散数值。
        pickle['学历'] = pd.Categorical(pickle['学历'])
        pickle['学历'] = pickle['学历'].cat.codes

        pickle['工作城市'] = pd.Categorical(pickle['工作城市'])
        pickle['工作城市'] = pickle['工作城市'].cat.codes

        pickle['用工制'] = pd.Categorical(pickle['用工制'])
        pickle['用工制'] = pickle['用工制'].cat.codes

        pickle['kw'] = pd.Categorical(pickle['kw'])
        pickle['kw'] = pickle['kw'].cat.codes

        pickle['工作城市'] = pd.Categorical(pickle['工作城市'])
        pickle['工作城市'] = pickle['工作城市'].cat.codes
        print(pickle.head())  # 查看数据
        pickle['薪酬'] = pickle['薪酬'].apply(lambda x: 1 if x < 3000 else 2 if x < 6000 else 3 if x < 9000 else 4)
        print(f"量化后：{pickle.head()}")  # 查看数据
        target = pickle['薪酬']  # 取出预测的
        print(f'series target.describe()：{target.describe()}')
        train_data = pickle.drop('薪酬', axis=1)  # 去掉预测的
        train_data.info()
        print(
            f'是否为空pickle:{pickle.isnull().values.any()}, sum : {pickle.isnull().sum().sum()} target: {target.isnull().values.any()}  ')

        np_zeros = np.zeros((train_data.shape[0], 4), dtype=np.int)
        for index, value in target.items():
            np_zeros[index][value - 1] = 1

        # dataset = tf.data.Dataset.from_tensor_slices((train_data.values, target.values))

        # Model
        input_layer = tflearn.input_data(shape=[None, 6], name='input')
        dense1 = tflearn.fully_connected(input_layer, 128, name='dense1')
        dense2 = tflearn.fully_connected(dense1, 256, name='dense2')
        softmax = tflearn.fully_connected(dense2, 4, activation='softmax')
        regression = tflearn.regression(softmax, optimizer='adam',
                                        learning_rate=0.001,
                                        loss='categorical_crossentropy')

        # Define classifier, with model checkpoint (autosave)
        model = tflearn.DNN(regression, checkpoint_path='model.tfl.ckpt')

        # Train model, with model checkpoint every epoch and every 200 training steps.
        XX = np.array(train_data)

        model.fit(XX, np_zeros, n_epoch=1,
                  # validation_set=(testX, testY),
                  show_metric=True,
                  snapshot_epoch=True,  # Snapshot (save & evaluate) model every epoch.
                  snapshot_step=1500,  # Snapshot (save & evalaute) model every 500 steps.
                  run_id='model_and_weights')

        # ---------------------
        # Save and load a model
        # ---------------------

        # Manually save model
        model.save("model.tfl")

    def test_predict(self):
        # Load a model
        input_layer = tflearn.input_data(shape=[None, 6], name='input')
        dense1 = tflearn.fully_connected(input_layer, 128, name='dense1')
        dense2 = tflearn.fully_connected(dense1, 256, name='dense2')
        softmax = tflearn.fully_connected(dense2, 4, activation='softmax')
        regression = tflearn.regression(softmax, optimizer='adam',
                                        learning_rate=0.001,
                                        loss='categorical_crossentropy')
        # Define classifier, with model checkpoint (autosave)
        model = tflearn.DNN(regression, checkpoint_path='model.tfl.ckpt')
        model.load("model.tfl")
        test_json = [1, '本科', '北京', '全职', 0, '物业经理', ]
        pd_json = pd.Series([1, '本科', '北京', '全职', 0, '物业经理'])

        pd_json[1] = pd.Categorical(pd_json[1])
        test_json[1] = pd_json[1].codes
        pd_json[2] = pd.Categorical(pd_json[2])
        test_json[2] = pd_json[2].codes
        pd_json[3] = pd.Categorical(pd_json[3])
        test_json[3] = pd_json[3].codes
        pd_json[5] = pd.Categorical(pd_json[5])
        test_json[5] = pd_json[5].codes

        result = model.predict([test_json])
        print(f'预测结果{result}')

    def re_train_model(self):
        # Load a model
        model.load("model.tfl")

        # Or Load a model from auto-generated checkpoint
        # >> model.load("model.tfl.ckpt-500")

        # Resume training
        model.fit(X, Y, n_epoch=1,
                  validation_set=(testX, testY),
                  show_metric=True,
                  snapshot_epoch=True,
                  run_id='model_and_weights')

        # ------------------
        # Retrieving weights
        # ------------------

        # Retrieve a layer weights, by layer name:
        dense1_vars = tflearn.variables.get_layer_variables_by_name('dense1')
        # Get a variable's value, using model `get_weights` method:
        print("Dense1 layer weights:")
        print(model.get_weights(dense1_vars[0]))
        # Or using generic tflearn function:
        print("Dense1 layer biases:")
        with model.session.as_default():
            print(tflearn.variables.get_value(dense1_vars[1]))

        # It is also possible to retrieve a layer weights through its attributes `W`
        # and `b` (if available).
        # Get variable's value, using model `get_weights` method:
        print("Dense2 layer weights:")
        print(model.get_weights(dense2.W))
        # Or using generic tflearn function:
        print("Dense2 layer biases:")
        with model.session.as_default():
            print(tflearn.variables.get_value(dense2.b))
