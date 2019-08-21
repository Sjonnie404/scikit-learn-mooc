# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: notebooks//ipynb,markdown_files//md,python_scripts//py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.2'
#       jupytext_version: 1.2.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Introduction to scikit-learn: basic preprocessing for basic model fitting
#
# In this notebook, we will aim at introducing a typical approach to build
# predictive models on tabular datasets.
#
# In particular we will highlight:
# * the difference between numerical and categorical variables;
# * the importance of scaling numerical variables;
# * typical ways to deal categorical variables;
# * train predictive models on different kinds of data;
# * evaluate the performance of a model via cross-validation.
#
# ## Introduce the dataset
#
# To this aim, we will use data from the 1994 Census bureau database. The goal
# with this data is to regress wages from heterogeneous data such as age,
# employment, education, family information, etc.
#
# Let's first load the data located in the `datasets` folder.

# %%
import pandas as pd

df = pd.read_csv('datasets/adult-census.csv')
# df = pd.read_csv("https://www.openml.org/data/get_csv/1595261/adult-census.csv")

# %% [markdown]
#
# Let's have a look at the first records of this data frame:

# %%
df.head()

# %% [markdown]
#
# The target variable in our study will be the "class" column while we will use
# the other columns as input variables for our model. This target column divides
# the samples (also known as records) into two groups: high income (>50K) vs low
# income (<=50K). The resulting prediction problem is therefore a binary
# classification problem.
#
# For simplicity, we will ignore the "fnlwgt" (final weight) column that was
# crafted by the creators of the dataset when sampling the dataset to be
# representative of the full census database.

# %%
target_name = "class"
target = df[target_name].to_numpy()
data = df.drop(columns=[target_name, "fnlwgt"])

# %% [markdown]
#
# We can check the number of samples and the number of features available in
# the dataset:

# %%
print(
    f"The dataset contains {data.shape[0]} samples and {data.shape[1]} "
    "features"
)

# %% [markdown]
#
# ## Working with numerical data
#
# The numerical data is the most natural type of data used in machine learning
# and can (almost) directly be fed to predictive models. We can quickly have a
# look at such data by selecting the subset of columns from the original data.
#
# We will use this subset of data to fit a linear classification model to
# predict the income class.

# %%
data.columns

# %%
data.dtypes

# %%
numerical_columns = ['age', 'education-num', 'hours-per-week',
                     'capital-gain', 'capital-loss']
data_numeric = data[numerical_columns]
data_numeric.head()

# %% [markdown]
# When building a machine learning model, it is important to leave out a
# subset of the data which we can use later to evaluate the trained model.
# The data used to fit a model a called training data while the one used to
# assess a model are called testing data.
#
# Scikit-learn provides an helper function `train_test_split` which will
# split the dataset into a training and a testing set. It will ensure that
# the data are shuffled randomly before splitting the data.

# %%
from sklearn.model_selection import train_test_split

data_train, data_test, target_train, target_test = train_test_split(
    data_numeric, target, random_state=42
)

print(
    f"The training dataset contains {data_train.shape[0]} samples and "
    f"{data_train.shape[1]} features"
)
print(
    f"The testing dataset contains {data_test.shape[0]} samples and "
    f"{data_test.shape[1]} features"
)

# %% [markdown] We will build a linear classification model called "Logistic
# Regression". The `fit` method is called to train the data and only the
# training data should be given for this purpose.
#
# In addition, we checking the time required to train the model and internally
# check the number of iterations done by the solver to find a solution.
# %%
from sklearn.linear_model import LogisticRegression
import time

model = LogisticRegression()
start = time.time()
model.fit(data_train, target_train)
elapsed_time = time.time() - start

print(
    f"The model {model.__class__.__name__} was trained in "
    f"{elapsed_time:.3f} seconds for {model.n_iter_} iterations"
)

# %% [markdown]
#
# Let's ignore the convergence warning for now and instead let's try
# to use our model to make some predictions on the first three records
# of the held out test set:

# %%

data_test[:3]

# %%

model.predict(data_test[:3])

# %%

target_test[:3]

# %% [markdown]
#
# To quantitatively evaluate our model, we can use the method `score`. It will
# compute the classification accuracy when dealing with a classificiation
# problem.

print(
    f"The test accuracy using a {model.__class__.__name__} is "
    f"{model.score(data_test, target_test):.3f}"
)

# %% [markdown]
#
# Let's now consider the `ConvergenceWarning` message that was raised previously
# when calling the `fit` method to train our model. This warning informs us that
# our model stopped learning becaused it reached the maximum number of
# iterations allowed by the user. This could potentially be detrimental for the
# model accuracy. We can follow the (bad) advice given in the warning message
# and increase the maximum number of iterations allowed.

# %%
model = LogisticRegression(max_iter=50000)
start = time.time()
model.fit(data_train, target_train)
elapsed_time = time.time() - start
print(
    f"The accuracy using a {model.__class__.__name__} is "
    f"{model.score(data_test, target_test):.3f} with a fitting time of "
    f"{elapsed_time:.3f} seconds in {model.n_iter_} iterations"
)

# %% [markdown]
#
# We can observe now a longer training time but not significant improvement in
# the predictive performance. Instead of increasing the number of iterations, we
# can try to help fit the model faster by scaling the data first. A range of
# preprocessing algorithms in scikit-learn allows to transform the input data
# before training a model. We can easily combine these sequential operation with
# a scikit-learn `Pipeline` which will chain the operations and can be used as
# any other classifier or regressor. The helper function `make_pipeline` will
# create a `Pipeline` by giving the successive transformations to perform.
#
# In our case, we will standardize the data and then train a new logistic
# regression model on that new version of the dataset set.

# %%
data_train.describe()

# %%
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
data_train_scaled = scaler.fit_transform(data_train)
data_train_scaled

# %%
data_train_scaled = pd.DataFrame(data_train_scaled, columns=data_train.columns)
data_train_scaled.describe()

# %%

from sklearn.pipeline import make_pipeline

model = make_pipeline(StandardScaler(), LogisticRegression())
start = time.time()
model.fit(data_train, target_train)
elapsed_time = time.time() - start
print(
    f"The accuracy using a {model.__class__.__name__} is "
    f"{model.score(data_test, target_test):.3f} with a fitting time of "
    f"{elapsed_time:.3f} seconds in {model[-1].n_iter_} iterations"
)

# %% [markdown]
#
# We can see that the training time and the number of iterations is much shorter
# while the predictive performance is equivalent.
#
# In the previous example, we split the original data into a training set and a
# testing set. This strategy has several issues: in the setting where the amount
# of data is limited, the subset of data used to train or test will be small;
# and the splitting was done in a random manner and we have no information
# regarding the confidence of the results obtained.
#
# Instead, we can use what cross-validation. Cross-validation consists in
# repeating this random splitting into training and testing sets and aggregate
# the model performance. By repeating the experiment, one can get an estimate of
# the variabilty of the model performance.
#
# The function `cross_val_score` allows for such experimental protocol by giving
# the model, the data and the target. Since there exists several
# cross-validation strategies, `cross_val_score` takes a parameter `cv` which
# defines the splitting strategy.

# %%
from sklearn.model_selection import cross_val_score

score = cross_val_score(model, data_numeric, target, cv=5)
print(f"The accuracy (mean +/- 1 std. dev.) is: "
      f"{score.mean():.3f} +/- {score.std():.3f}")
print(f"The different scores obtained are: \n{score}")

# %% [markdown]
#
# Setting `cv=5` created 5 distinct splits to get 5 variations for the training
# and testing sets. Each training set is used to fit one model which is then
# scored on the matching test set. This strategy is called K-fold
# cross-validation where `K` corresponds to the number of splits.

# %%

# TODO add CV diagram for 5-fold CV from the gallery

# %% [markdown]
# ## Work with categorical data
#
# In the previous section, we dealt with data for which numerical algorithms are
# mathematically designed to work natively. However, real datasets contain type
# of data which do not belong to this category and will require some
# preprocessing. Such preprocessing will transform these data to be numerical
# and thus natively handled by machine learning algorithms.
#
# Categorical data are broadly encountered in data science. Numerical data is a
# continuous quantity corresponding to a real numbers while categorical data are
# represented as discrete values. For instance, the variable `SEX` in our
# previous dataset is a categorical variable because it encodes the data with
# the two categories `male` and `female`.
#
# In the remainder of this section, we will present different strategies to
# encode categorical data into numerical data which can be used by a
# machine-learning algorithm.

# %%
data.dtypes


# %%
categorical_columns = [
    'workclass', 'education', 'marital-status', 'occupation', 'relationship',
    'race', 'sex', 'native-country'
]
data_categorical = data[categorical_columns]
print(data_categorical.head())

# %% [markdown]
# ### Encode categories having an ordering
#
# The most intuitive strategy is to encode each category by a numerical value.
# The `OrdinalEncoder` will transform the data in such manner.

# %%
from sklearn.preprocessing import OrdinalEncoder

print(data_categorical.head())
print(f"The datasets is composed of {data_categorical.shape[1]} features")
encoder = OrdinalEncoder()
data_encoded = encoder.fit_transform(data_categorical)

print(f"The dataset encoded contains {data_encoded.shape[1]} features")
print(data_encoded[:5])

# %% [markdown]
# We can see that all categories have been encoded for each feature
# independently. We can also notice that the number of feature before and after
# the encoding is the same.
#
# However, one has to be careful when using this encoding strategy. The
# encoding imposed an order regarding the categories: 0 is smaller than 1 which
# is smaller than 2, etc. If the original categories did not have such order
# then this encoding is not adequate and you should use one-hot encoding
# instead.
#
# ### Encode categories which do not have an ordering
#
# As previously stated, `OrdinalEncoder` is encoding categorical data having
# an ordering. In this case, the `OneHotEncoder` should be used. For a given
# feature, it will create as many new columns as categories. For a sample,
# the column corresponding to the category will be set to `1` while the other
# columns will be set to `0`.

# %%
from sklearn.preprocessing import OneHotEncoder

print(data_categorical.head())
print(f"The datasets is composed of {data_categorical.shape[1]} features")
encoder = OneHotEncoder(sparse=False)
data_encoded = encoder.fit_transform(data_categorical)

print(f"The dataset encoded contains {data_encoded.shape[1]} features")
print(data_encoded[:5])

# %% [markdown]
# One can notice that the number of features after the encoding is larger than
# in the original data.
#
# Once the encoding is done, we could integrate it inside a machine learning
# pipeline as in the case with numerical data. In the following, we train a
# linear classifier on the encoded data and check the performance of this
# machine learning pipeline using cross-validation.

# %%
model = make_pipeline(OneHotEncoder(handle_unknown='ignore'),
                      LogisticRegression(max_iter=1000))
score = cross_val_score(model, data_categorical, target)
print(f"The accuracy is: {score.mean():.3f} +/- {score.std():.3f}")
print(f"The different scores obtained are: \n{score}")

# %% [markdown]
# ## Combining different transformers used for different column types
#
# In the previous section, we saw that we need to treat data specifically
# depending of their nature (i.e. numerical or categorical) and trained one
# pipeline (transformer + classifier) for each kind of dataset.
#
# Scikit-learn provides a `ColumnTransformer` class which will dispatch some
# specific columns to a specific transformer making it easy to fit a single
# predictive model on a data that combines both kinds of variable together
# (heterogeneously typed tabular data).
#
# We can first define the columns depending on their data type:
# * **binary encoding** will be applied to categorical columns with only too
#   possible values (e.g. sex=male or sex=female in this example). Each binary
#   categorical columns will be mapped to one numerical columns with 0 or 1
#   values.
# * **one-hot encoding** will be applied to categorical columns with more that
#   two possible categories. This encoding will create one additional column for
#   each possible categorical value.
# * **numerical scaling** numerical features which will be standardized.

# %%
binary_encoding_columns = ['sex']
one_hot_encoding_columns = ['workclass', 'education', 'marital-status',
                            'occupation', 'relationship',
                            'race', 'native-country']
scaling_columns = ['age', 'education-num', 'hours-per-week',
                   'capital-gain', 'capital-loss']

# %% [markdown]
#
# We can now create our `ColumnTransfomer` by specifying a list of triplet
# (preprocessor name, transformer, columns). Finally, we can define a pipeline
# to stack this "preprocessor" with our classifier (logistic regression).

# %%
from sklearn.compose import ColumnTransformer

preprocessor = ColumnTransformer([
    ('binary-encoder', OrdinalEncoder(), binary_encoding_columns),
    ('one-hot-encoder', OneHotEncoder(handle_unknown='ignore'),
     one_hot_encoding_columns),
    ('standard-scaler', StandardScaler(), scaling_columns)
])
model = make_pipeline(preprocessor, LogisticRegression(max_iter=1000))
score = cross_val_score(model, data, target, cv=5)
print(f"The accuracy is: {score.mean():.3f} +- {score.std():.3f}")
print(f"The different scores obtained are: \n{score}")


# %% [markdown]
# One can notice that the model, even more complex than in the previous
# sections, follow the same API meaning that it `fit` is called to preprocess
# the data and `score` is used to predict and check the model performance.
