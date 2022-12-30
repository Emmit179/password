import time
from sklearn import svm
from sklearn.metrics import classification_report
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import pandas as pd
import numpy as np
from pandas import Series

df = pd.read_csv('data/data.csv')
df['split'] = np.random.randn(df.shape[0], 1)

msk = np.random.rand(len(df)) <= 0.7

trainData = df[msk]
testData = df[~msk]


# Create feature vectors
vectorizer = TfidfVectorizer(min_df = 5,
                            max_df = 0.8,
                            use_idf = True)
train_vectors = vectorizer.fit_transform(trainData['Content'].values.astype('U'))
test_vectors = vectorizer.transform(testData['Content'].values.astype('U'))


# print(preprocessing(trainData['Content'].values.astype('U')))

# exit()

# Perform classification with SVM, kernel=linear
classifier_linear = svm.SVC(kernel='rbf')
t0 = time.time()
classifier_linear.fit(train_vectors, trainData['Label'].values.astype('U'))
t1 = time.time()
prediction_linear = classifier_linear.predict(test_vectors)
t2 = time.time()
time_linear_train = t1-t0
time_linear_predict = t2-t1
# pickling the vectorizer
pickle.dump(vectorizer, open('svm_models/vectorizer.sav', 'wb'))
# pickling the model
pickle.dump(classifier_linear, open('svm_models/classifier.sav', 'wb'))
# results
print("Training time: %fs; Prediction time: %fs" % (time_linear_train, time_linear_predict))
report = classification_report(testData['Label'].values.astype('U'), prediction_linear, output_dict=True)
print(str(report['macro avg']))
# print('negative: ', report['neg'])
