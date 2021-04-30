# https://cloud.google.com/ai-platform/prediction/docs/using-pipelines-for-preprocessing?hl=zh-cn#about-data

# from sklearn.externals import joblib 序列化对象
import json
import numpy as np
import os
import pandas as pd
import pickle

from sklearn import preprocessing
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectKBest
from sklearn.pipeline import FeatureUnion
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelBinarizer


def test_census(self):
        # Define the format of your input data, including unused columns.
        # These are the columns from the census data files.
        COLUMNS = (
            '公司规模', '学历', '工作城市', '用工制', '经验', 'kw',
            # '技能', '福利待遇',
            '薪酬'
        )
        # Categorical columns are columns that need to be turned into a numerical value to be used by scikit-learn
        CATEGORICAL_COLUMNS = (
            '学历', '工作城市', '用工制',
            'kw',
            # '技能', '福利待遇',
        )

        # Load the training census dataset
        if os.path.exists('./select_col_fillna0_learn.pkl'):
            with open('./select_col_fillna0_learn.pkl', 'rb') as train_data:
                raw_training_data = pd.read_pickle(train_data)
        else:
            with open('G:\\数据集\\zhaopincom\\DP\\storage_merge\\pickle_finally_elastic_merge_nan_file.pkl',
                      'rb') as train_data:
                raw_training_data = pd.read_pickle(train_data).loc[:, ['公司规模', '学历', '工作城市', '用工制', '经验', 'kw',
                                                                       # '技能', '福利待遇',
                                                                       '薪酬']].fillna(0)  # 填充0
                raw_training_data['kw'] = raw_training_data['kw'].apply(lambda x: str(x) if type(x) == int else x)  # 转换类型 有可能 上面的fillna  int 0 或者 str 0

                raw_training_data.to_pickle('./select_col_fillna0_learn.pkl')

        raw_training_data.info()
        # Remove the column we are trying to predict ('income-level') from our features list
        # Convert the Dataframe to a lists of lists
        train_features = raw_training_data.drop('薪酬', axis=1).values.tolist()

        # Create our training labels list, convert the Dataframe to a lists of lists
        train_labels = (raw_training_data['薪酬'] > 6000).values.tolist()

        # Since the census data set has categorical features, we need to convert
        # them to numerical values. We'll use a list of pipelines to convert each
        # categorical column and then use FeatureUnion to combine them before calling
        # the RandomForestClassifier.
        categorical_pipelines = []

        # Each categorical column needs to be extracted individually and converted to a numerical value.
        # To do this, each categorical column will use a pipeline that extracts one feature column via
        # SelectKBest(k=1) and a LabelBinarizer() to convert the categorical value to a numerical one.
        # A scores array (created below) will select and extract the feature column. The scores array is
        # created by iterating over the COLUMNS and checking if it is a CATEGORICAL_COLUMN.
        for i, col in enumerate(COLUMNS[:-1]):
            if col in CATEGORICAL_COLUMNS:
                # Create a scores array to get the individual categorical column.
                # Example:
                #  data = [39, 'State-gov', 77516, 'Bachelors', 13, 'Never-married', 'Adm-clerical',
                #         'Not-in-family', 'White', 'Male', 2174, 0, 40, 'United-States']
                #  scores = [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                #
                # Returns: [['Sate-gov']]
                scores = []
                # Build the scores array
                for j in range(len(COLUMNS[:-1])):
                    if i == j:  # This column is the categorical column we want to extract.
                        scores.append(1)  # Set to 1 to select this column
                    else:  # Every other column should be ignored.
                        scores.append(0)
                skb = SelectKBest(k=1)
                skb.scores_ = scores
                # Convert the categorical column to a numerical value
                lbn = LabelBinarizer()  #preprocessing.LabelEncoder() # 最好用one hot  换掉 ，https://github.com/ageron/handson-ml/issues/241  OneHotEncoder : LabelBinarizer() #Warning: earlier versions of the book used the LabelBinarizer or CategoricalEncoder classes to convert each categorical value to a one-hot vector. It is now preferable to use the OneHotEncoder class. Right now it can only handle integer categorical inputs, but in Scikit-Learn 0.20 it will also handle string categorical inputs (see PR #10521). So for now we import it from future_encoders.py, but when Scikit-Learn 0.20 is released, you can import it from sklearn.preprocessing instead:
                r = skb.transform(train_features)
                # print(i) 调试用
                lbn.fit(r)
                # Create the pipeline to extract the categorical feature
                categorical_pipelines.append(
                    ('categorical-{}'.format(i), Pipeline([
                        ('SKB-{}'.format(i), skb),
                        ('LBN-{}'.format(i), lbn)])))

        # Create pipeline to extract the numerical features
        skb = SelectKBest(k=2)
        # From COLUMNS use the features that are numerical
        skb.scores_ = [1, 0,  0,  0, 1, 0]
        categorical_pipelines.append(('numerical', skb))

        # Combine all the features using FeatureUnion
        preprocess = FeatureUnion(categorical_pipelines)

        # Create the classifier
        classifier = RandomForestClassifier()

        # Transform the features and fit them to the classifier
        classifier.fit(preprocess.transform(train_features), train_labels)

        # Create the overall model as a single pipeline
        pipeline = Pipeline([
            ('union', preprocess),
            ('classifier', classifier)
        ])

        # Export the model to a file
        # joblib.dump(pipeline, 'model.joblib')
        with open('model.pkl', 'wb') as f:
            pickle.dump(pipeline, f)

        print('Model trained and saved')
