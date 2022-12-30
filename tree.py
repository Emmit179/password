import pandas as pd
import matplotlib.pyplot as plt
# For text feature extraction
from sklearn.feature_extraction.text import TfidfVectorizer
# For creating a pipeline
from sklearn.pipeline import Pipeline
# Classifier Model (Decision Tree)
from sklearn.tree import DecisionTreeRegressor
import pickle


# Read the File
data = pd.read_csv('data/training.csv')


features = data.values[:, 1].astype('str')

labels = data.values[:, -1].astype('float')

# Sequentially apply a list of transforms and a final estimator
classifier_model = Pipeline([
                ('tfidf', TfidfVectorizer(analyzer='char')),
                ('decisionTree',DecisionTreeRegressor()),
])


# Fit the Model
classifier_model.fit(features, labels)

df= pd.read_csv('data/cleanpasswordlist.csv')
X = df.values[:, 0].astype('str')
y = df.values[:, 1].astype('int')

print('Testing Accuracy: ',classifier_model.score(X, y)*100)

# print(classifier_model.predict(["test"]))
# exit()
pickle.dump(classifier_model, open('svm_models/tree.pkl', 'wb'))