# Load the test census dataset 评估数据集
# with open('./census_data/adult.test', 'r') as test_data:
#     raw_testing_data = pd.read_csv(test_data, names=COLUMNS, skiprows=1)
# # Remove the column we are trying to predict ('income-level') from our features list
# # Convert the Dataframe to a lists of lists
# test_features = raw_testing_data.drop('income-level', axis=1).as_matrix().tolist()
# # Create our training labels list, convert the Dataframe to a lists of lists
# test_labels = (raw_testing_data['income-level'] == ' >50K.').as_matrix().tolist()

# test
# test_json = [1, '本科', '哈尔滨', '兼职', 0, '物业经理', ] 为false
import os
import pickle

import pandas as pd

import tflearn
from utils.parse_yaml import global_config


def get_predict_result(test_json=None):
    if test_json is None:
        test_json = [1, '本科', '北京', '全职', 0, '物业经理', ]
    if global_config.get('machine_learn').get('model_pkl_dir'):
        if os.path.exists(global_config.get('machine_learn').get('model_pkl_dir')):
            model = pd.read_pickle(global_config.get('machine_learn').get('model_pkl_dir'))  # 这样快
        else:
            model = pd.read_pickle('../../Data/model.pkl.bz2.001', 'bz2')
    else:
        model = pd.read_pickle('../../Data/model.pkl.bz2.001', 'bz2')

    label = model.predict([test_json])
    prob = model.predict_proba([test_json])
    log_prob = model.predict_log_proba([test_json])
    print(
        'Predict class for X: {}, Predict class probabilities for X: {}, Predict class log-probabilities for X: {}'.format(
            label,
            prob,
            log_prob
        ))
    return (label,
            prob,
            log_prob)


def get__dnn_predict_result(test_json=None):
    if test_json is None:
        test_json = [1, '本科', '哈尔滨', '全职', 0, '物业经理']

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
    model.load(global_config.get('machine_learn').get('deep_learn').get('dnn_model_tfl')+"model.tfl")
    pd_json = pd.DataFrame(test_json, columns=['公司规模', '学历', '工作城市', '用工制', '经验', 'kw'])

    with open(global_config.get('machine_learn').get('deep_learn').get('dnn_catagorical'), 'rb') as f:
        _CATEGORICAL_TYPES_ = pickle.load(f)
    cat_columns = pd_json.select_dtypes(['object']).columns
    pd_json[cat_columns] = pd_json[cat_columns].apply(lambda x: x.astype(
        pd.api.types.CategoricalDtype(categories=_CATEGORICAL_TYPES_[x.name], ordered=True)))

    for col in cat_columns:
        pd_json[col] = pd_json[col].cat.codes

    pd_json.fillna(0)  # 未知属性填为0
    result = model.predict([pd_json.loc[0].to_list()])
    print(f'预测结果{result}')
    return result
