# -*- coding: utf-8 -*-
"""Cracking the Apple: Predicting Stock Prices

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/#fileId=https%3A//storage.googleapis.com/kaggle-colab-exported-notebooks/cracking-the-apple-predicting-stock-prices-b9f3e235-f8ff-4005-9095-49e7d1de5afa.ipynb%3FX-Goog-Algorithm%3DGOOG4-RSA-SHA256%26X-Goog-Credential%3Dgcp-kaggle-com%2540kaggle-161607.iam.gserviceaccount.com/20240129/auto/storage/goog4_request%26X-Goog-Date%3D20240129T160837Z%26X-Goog-Expires%3D259200%26X-Goog-SignedHeaders%3Dhost%26X-Goog-Signature%3D08fcf10840909b1bf54c1563e7d2d13eef30ba6d39c376d6a957731e0c24a15d662c2eb62bdf082e60774440e17556bae0474fc48be219e8607a42d46a049a100c1c7a563cc1ee5b6bb2af7fe8e3f0b08048ba34d8c995bf5c6cae9953507962eaad2c2dcf47a96fd918d2d0eb5c6fa6a3a8c3d1f3549dff0c7b37353683cfe6046e81438e5fb2b319ff700f04fba392c82bd81d423cd95defa4fc6b1ebb8634575c280a1715c66180044226f9e6b1f0a65cbea5ddf96a72e3ab52169681a63cfab7913544217d9093858e56d2ad947b1b29bc1684d333eff6e9f6562fb0a65068286c9338d5baaa4ff55f0fe328abb28c3ae7392c36940b3f75c8eca00f69da
"""

# IMPORTANT: RUN THIS CELL IN ORDER TO IMPORT YOUR KAGGLE DATA SOURCES
# TO THE CORRECT LOCATION (/kaggle/input) IN YOUR NOTEBOOK,
# THEN FEEL FREE TO DELETE THIS CELL.
# NOTE: THIS NOTEBOOK ENVIRONMENT DIFFERS FROM KAGGLE'S PYTHON
# ENVIRONMENT SO THERE MAY BE MISSING LIBRARIES USED BY YOUR
# NOTEBOOK.

import os
import sys
from tempfile import NamedTemporaryFile
from urllib.request import urlopen
from urllib.parse import unquote, urlparse
from urllib.error import HTTPError
from zipfile import ZipFile
import tarfile
import shutil

CHUNK_SIZE = 40960
DATA_SOURCE_MAPPING = 'apple-stock-price-from-19802021:https%3A%2F%2Fstorage.googleapis.com%2Fkaggle-data-sets%2F1579572%2F3839314%2Fbundle%2Farchive.zip%3FX-Goog-Algorithm%3DGOOG4-RSA-SHA256%26X-Goog-Credential%3Dgcp-kaggle-com%2540kaggle-161607.iam.gserviceaccount.com%252F20240129%252Fauto%252Fstorage%252Fgoog4_request%26X-Goog-Date%3D20240129T160837Z%26X-Goog-Expires%3D259200%26X-Goog-SignedHeaders%3Dhost%26X-Goog-Signature%3D93e26716e31cf04370650eb0538ce8212672c846bda7f710bcd0d96c94791321c44ff192afdf74545eceb431148584a8986ffb3bdf67711cd07d70411463af9fa9845ba1ff721dc8059ac510e52aa50a2f6b4c0705988d23e1f3549640a1a870d983e1a97784a9636b05a5b964140236620e4678d3453f5a54c87350cd2cd568dfe8e11356db0d71605076f1e51494d23f32b901832d3ee19c03ec2efd6e16f3c380022201d7a1ea068514508900c6454fc05c8c9aed41b0b9ef877edfd159cc42d01ee6f1e00ec3f5979ba40b579056b3b3516532286fd7d0b4d00449a867c2c8b221d2731c65cad836237c994ea2b75ecf4877312beb2e716dca826a0ef9ef'

KAGGLE_INPUT_PATH='/kaggle/input'
KAGGLE_WORKING_PATH='/kaggle/working'
KAGGLE_SYMLINK='kaggle'

!umount /kaggle/input/ 2> /dev/null
shutil.rmtree('/kaggle/input', ignore_errors=True)
os.makedirs(KAGGLE_INPUT_PATH, 0o777, exist_ok=True)
os.makedirs(KAGGLE_WORKING_PATH, 0o777, exist_ok=True)

try:
  os.symlink(KAGGLE_INPUT_PATH, os.path.join("..", 'input'), target_is_directory=True)
except FileExistsError:
  pass
try:
  os.symlink(KAGGLE_WORKING_PATH, os.path.join("..", 'working'), target_is_directory=True)
except FileExistsError:
  pass

for data_source_mapping in DATA_SOURCE_MAPPING.split(','):
    directory, download_url_encoded = data_source_mapping.split(':')
    download_url = unquote(download_url_encoded)
    filename = urlparse(download_url).path
    destination_path = os.path.join(KAGGLE_INPUT_PATH, directory)
    try:
        with urlopen(download_url) as fileres, NamedTemporaryFile() as tfile:
            total_length = fileres.headers['content-length']
            print(f'Downloading {directory}, {total_length} bytes compressed')
            dl = 0
            data = fileres.read(CHUNK_SIZE)
            while len(data) > 0:
                dl += len(data)
                tfile.write(data)
                done = int(50 * dl / int(total_length))
                sys.stdout.write(f"\r[{'=' * done}{' ' * (50-done)}] {dl} bytes downloaded")
                sys.stdout.flush()
                data = fileres.read(CHUNK_SIZE)
            if filename.endswith('.zip'):
              with ZipFile(tfile) as zfile:
                zfile.extractall(destination_path)
            else:
              with tarfile.open(tfile.name) as tarfile:
                tarfile.extractall(destination_path)
            print(f'\nDownloaded and uncompressed: {directory}')
    except HTTPError as e:
        print(f'Failed to load (likely expired) {download_url} to path {destination_path}')
        continue
    except OSError as e:
        print(f'Failed to load {download_url} to path {destination_path}')
        continue

print('Data source import complete.')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense, LSTM

""" <a id="1.2"></a>
###  Load the dataset


"""

df = pd.read_csv('../input/apple-stock-price-from-19802021/AAPL.csv') # Load Dataset

""" <a id="1.3"></a>
###   Data Describtion
"""

df.info()
df.head()

## Statistical summary of the data
df.describe()

"""Some observation from the data statitics:

    1. There are 10,468 observations in the dataset.
    2. The minimum and maximum values for Open, High, Low, Close, and Adj Close prices are significantly different,   indicating a large range of values for these variables.
    3. The standard deviation for each variable is also quite large, indicating a high degree of variability in the data.
    4. The volume values in the dataset also have a large range of values, with a mean value of 3.3 billion.
   
<a id='2'></a>
<div class="list-group" id="list-tab" role="tablist">
<p style="background-color:#000000;font-family:candaralight;color:#ffffff;font-size:175%;text-align:center;border-radius:10px 10px;"> DATA PREPROCESSING </p>

In this notebook, we will be exploring and analyzing the Apple stock prices dataset. We will start by importing important libraries, loading the data, and giving a brief description of the dataset.

<a id="2.1"></a>
### Data cleaning
    
The data set was found to be free of missing values or duplicated rows.
"""

# check for missing values
df.isnull().sum()

# check for duplicate rows
df.duplicated().sum()

# drop duplicate rows
df.drop_duplicates(inplace=True)

"""<a id="2.2"></a>
###  Data transformation
    
The column data types were examined and the date type was corrected from object to date. and set the 'Date' column as the index
"""

# check the data types of the columns
df.dtypes

# convert 'Date' column to datetime format
df['Date'] = pd.to_datetime(df['Date'])

# set the 'Date' column as the index
#df.set_index('Date', inplace=True)

"""<a id='3'></a>
<div class="list-group" id="list-tab" role="tablist">
<p style="background-color:#000000;font-family:candaralight;color:#ffffff;font-size:175%;text-align:center;border-radius:10px 10px;"> FEATURE EMGINEERING </p>

In this section, I extracted relevant information from the data and create new features that can potentially improve the performance of my models. By transforming and combining existing features, I aim to provide my models with more meaningful and informative data to make accurate predictions.
    
<a id="3.1"></a>
### Define a function to add new features to the data

    
I define a function add_features that adds several new features to the data, including day of the week, month, quarter, year, week of the year, day of the year, and lagged features. We then apply this function to the data and drop any rows with missing values. This code is flexible and easy to modify to add or remove features as needed.
"""

def add_features(data):
    # Add day of the week feature
    data['day_of_week'] = data['Date'].dt.dayofweek

    # Add month feature
    data['month'] = data['Date'].dt.month

    # Add quarter feature
    data['quarter'] = data['Date'].dt.quarter

    # Add year feature
    data['year'] = data['Date'].dt.year

    # Add week of the year feature
    data['week_of_year'] = data['Date'].dt.isocalendar().week

    # Add day of the year feature
    data['day_of_year'] = data['Date'].dt.dayofyear

    # Add lagged features
    data['lag_1'] = data['Close'].shift(1)
    data['lag_2'] = data['Close'].shift(2)
    data['lag_3'] = data['Close'].shift(3)
    data['lag_4'] = data['Close'].shift(4)
    data['lag_5'] = data['Close'].shift(5)

    return data

"""<a id="3.1"></a>
###  Apply the function to the data
Apply the function to the stock prices data and dropping any row with missing values

"""

# Apply the function to the data
df = add_features(df)

# Drop rows with missing values
df.dropna(inplace=True)

df.head()

"""<a id='4'></a>
<div class="list-group" id="list-tab" role="tablist">
<p style="background-color:#000000;font-family:candaralight;color:#ffffff;font-size:175%;text-align:center;border-radius:10px 10px;"> EXPLORATORY DATA ANALYSIS </p>

This section explores the dataset using various visualizations such as distribution plots, line plots, heatmaps, and pairplots to gain insights into the relationships between features and the target variable.
    
"""

import seaborn as sns
plt.figure(figsize=(10, 6))

# Distribution of the target variable
sns.displot(data=df, x='Close', kde=True)
plt.title('Distribution of Close Prices')
plt.show()

# Line plot of close prices over time
sns.lineplot(data=df, x='Date', y='Close')
plt.title('Close Prices Over Time')
plt.xlabel('Date')
plt.ylabel('Close Price')
plt.xticks(rotation=45)
plt.show()

# Heatmap of correlation between features
corr = df.corr()
sns.heatmap(corr, cmap='coolwarm', annot=True)
plt.title('Correlation Between Features')
plt.show()

# Pairplot of features

sns.pairplot(data=df, vars=['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume'])
plt.title('Pairplot of Features')
plt.show()

"""Observation

    1. Distribution plot of Close Prices:

*  Shows the distribution of Close Prices
*  Indicates that the majority of the Close Prices are in the range of 0 to 35
*  Significant skewed to the right

    2. Line plot of Close Prices over time:
    

*  Shows how the Close Prices have changed over time
*  Indicates that there has been significant fluctuation in the Close Prices, with a few major peaks and troughs from 2005
*  There is a huge uptrend since 2015 and still going.

    3. Heatmap of correlation between features:
    

*  Shows the correlation between all the features in the dataset
*  Indicates that the Close Price has a strong positive correlation with Open, High, Low, and Adj Close prices, but a weak negative correlation with Volume
*  Also indicates that the Open, High, Low, and Adj Close prices are highly correlated with each other

    4. Pairplot of features:
    

* Shows the pairwise relationships between all the features in the dataset

* Indicates that the Open, High, Low, and Close prices are strongly positively correlated with each other, with a linear relationship

* Also indicates that the Volume feature is not strongly correlated with any of the other features

<a id='5'></a>
<div class="list-group" id="list-tab" role="tablist">
<p style="background-color:#000000;font-family:candaralight;color:#ffffff;font-size:175%;text-align:center;border-radius:10px 10px;"> MODELING </p>

The modeling section is where I explore different algorithms to predict the stock prices. I start with a baseline model and gradually move towards more complex models like Linear Regression, Support Vector Regression, Random Forest Regression, and LSTM. Each model is evaluated for its performance and compared with the others to choose the best one.
    
<a id='5.1'></a>
###  Baseline model

Building a baseline model is good start to compare the performance of other models against.
"""

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(df[['Open', 'High', 'Low', 'Volume']], df['Close'], test_size=0.2, random_state=42)

# Baseline model
y_pred_baseline = np.full((len(y_test),), y_train.mean())
mse_baseline = mean_squared_error(y_test, y_pred_baseline)
rmse_baseline = np.sqrt(mse_baseline)
mae_baseline = mean_absolute_error(y_test, y_pred_baseline)
mape_baseline = np.mean(np.abs((y_test - y_pred_baseline) / y_test)) * 100
r2_baseline = r2_score(y_test, y_pred_baseline)

print('Baseline Model:')
print(f'MSE: {mse_baseline:.2f}')
print(f'RMSE: {rmse_baseline:.2f}')
print(f'MAE: {mae_baseline:.2f}')
print(f'MAPE: {mape_baseline:.2f}%')
print(f'R2 Score: {r2_baseline:.2f}\n')

"""What the model tell us:

    I would say that the baseline model is not performing well. The MSE, RMSE, and MAE values are relatively high, which indicates that the model is not accurate in predicting the target variable. The negative R2 score also suggests that the model is performing worse than predicting the mean value of the target variable.

<a id='5.2'></a>
###  Linear Regression Model
"""

# Linear Regression Model
lr_model = LinearRegression()
lr_model.fit(X_train, y_train)
y_pred_lr = lr_model.predict(X_test)
mse_lr = mean_squared_error(y_test, y_pred_lr)
rmse_lr = np.sqrt(mse_lr)
mae_lr = mean_absolute_error(y_test, y_pred_lr)
mape_lr = np.mean(np.abs((y_test - y_pred_lr) / y_test)) * 100
r2_lr = r2_score(y_test, y_pred_lr)

print('Linear Regression Model:')
print(f'MSE: {mse_lr:.2f}')
print(f'RMSE: {rmse_lr:.2f}')
print(f'MAE: {mae_lr:.2f}')
print(f'MAPE: {mape_lr:.2f}%')
print(f'R2 Score: {r2_lr:.2f}\n')

"""What the model tell us:

    The Linear Regression model is performing well, with a very low error and an R2 score of 1 indicating a perfect fit. However, it is important to note that overfitting is possible and further evaluation may be necessary.

<a id='5.3'></a>
###  Support Vector Regression Model
"""

# Support Vector Regression Model
scaler = MinMaxScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

svr_model = SVR(kernel='linear')
svr_model.fit(X_train_scaled, y_train)
y_pred_svr = svr_model.predict(X_test_scaled)
mse_svr = mean_squared_error(y_test, y_pred_svr)
rmse_svr = np.sqrt(mse_svr)
mae_svr = mean_absolute_error(y_test, y_pred_svr)
mape_svr = np.mean(np.abs((y_test - y_pred_svr) / y_test)) * 100
r2_svr = r2_score(y_test, y_pred_svr)

print('Support Vector Regression Model:')
print(f'MSE: {mse_svr:.2f}')
print(f'RMSE: {rmse_svr:.2f}')
print(f'MAE: {mae_svr:.2f}')
print(f'MAPE: {mape_svr:.2f}%')
print(f'R2 Score: {r2_svr:.2f}\n')

"""What does this model tell us:

- The SVR model is fit to the training data using a linear kernel.

- Based on the evaluation, the model has an RMSE of 0.40, which means that, on average, the predicted values are off by about 0.40 units.

- The model has an MAPE of 20.31%, which means that, on average, the predicted values are off by about 20.31% of the true values.

- The R2 score of 1.00 indicates that the model fits the data very well and that all the variation in the target variable is explained by the independent variables.

- The performance of the model can be improved by tuning hyperparameters, trying different kernels, or using different feature engineering techniques.

<a id='5.4'></a>
### Random Forest Regression Model
"""

# Random Forest Regression Model
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)
y_pred_rf = rf_model.predict(X_test)
mse_rf = mean_squared_error(y_test, y_pred_rf)
rmse_rf = np.sqrt(mse_rf)
mae_rf = mean_absolute_error(y_test, y_pred_rf)
mape_rf = np.mean(np.abs((y_test - y_pred_rf) / y_test)) * 100
r2_rf = r2_score(y_test, y_pred_rf)

print('Random Forest Regression Model:')
print(f'MSE: {mse_rf:.2f}')
print(f'RMSE: {rmse_rf:.2f}')
print(f'MAE: {mae_rf:.2f}')
print(f'MAPE: {mape_rf:.2f}%')
print(f'R2 Score: {r2_rf:.2f}\n')

"""What does this model tell us:

-  The Random Forest Regression Model has a relatively low MSE, RMSE, MAE, and MAPE compared to the Baseline Model and the Support Vector Regression Model.
-  The R2 Score is 1.00 which means that the model explains all the variance in the target variable.

<a id='5.5'></a>
### LSTM Model
"""

from keras.layers import Dropout

# Create a new dataframe with only the 'Close column
data = df.filter(['Close'])
# Convert the dataframe to a numpy array
dataset = data.values
# Get the number of rows to train the model on
len_train_data = int(np.ceil( len(dataset) * .95 ))

len_train_data

# Scale the data
from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler(feature_range=(0,1))
trained_scaled_data = scaler.fit_transform(dataset)

trained_scaled_data

# Create the training data set
# Create the scaled training data set
train_data = trained_scaled_data[0:int(len_train_data), :]
# Split the data into x_train and y_train data sets
x_train = []
y_train = []

for i in range(60, len(train_data)):
    x_train.append(train_data[i-60:i, 0])
    y_train.append(train_data[i, 0])
    if i<= 61:
        print(x_train)
        print(y_train)
        print()

# Convert the x_train and y_train to numpy arrays
x_train, y_train = np.array(x_train), np.array(y_train)

# Reshape the data
x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
# x_train.shape

from keras.models import Sequential
from keras.layers import Dense, LSTM

# Build the LSTM model
model = Sequential()
model.add(LSTM(128, return_sequences=True, input_shape= (x_train.shape[1], 1)))
model.add(LSTM(64, return_sequences=False))
model.add(Dense(25))
model.add(Dense(1))

# Compile the model
model.compile(optimizer='adam', loss='mean_squared_error')

# Train the model
model.fit(x_train, y_train, batch_size=32, epochs=14)

# Create the testing data set
# Create a new array containing scaled values from index 1543 to 2002
test_data = trained_scaled_data[len_train_data - 60: , :]
# Create the data sets x_test and y_test
x_test = []
y_test = dataset[len_train_data:, :]
for i in range(60, len(test_data)):
    x_test.append(test_data[i-60:i, 0])

# Convert the data to a numpy array
x_test = np.array(x_test)

# Reshape the data
x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1 ))

# Get the models predicted price values
predictions = model.predict(x_test)
predictions = scaler.inverse_transform(predictions)

# Get the root mean squared error (RMSE)
rmse = np.sqrt(np.mean(((predictions - y_test) ** 2)))
rmse
# Baseline model
mse_lstm = mean_squared_error(y_test, predictions)
rmse_lstm = np.sqrt(mse_lstm)
mae_lstm = mean_absolute_error(y_test, predictions)
mape_lstm = np.mean(np.abs((y_test - predictions) / y_test)) * 100
r2_lstm = r2_score(y_test, predictions)

print('lstm Model:')
print(f'MSE: {mse_lstm:.2f}')
print(f'RMSE: {rmse_lstm:.2f}')
print(f'MAE: {mae_lstm:.2f}')
print(f'MAPE: {mape_lstm:.2f}%')
print(f'R2 Score: {r2_lstm:.2f}\n')

plt.plot(y_test, color = 'red', label = 'Real Stock Price')
plt.plot(predictions, color = 'green', label = 'Predicted Stock Price')
plt.title(' Stock Price Prediction')
plt.xlabel('Time')
plt.ylabel(' Stock Price')
plt.legend()
plt.show()

"""The LSTM model shows promising performance

1. Low prediction errors (MSE and RMSE) and relatively small deviations from the actual values (MAE).

2. The MAPE indicates a low average percentage difference, suggesting accurate predictions in relative terms.

3. The high R2 score indicates a strong relationship between the predictors and the target variable, indicating a good fit of the model to the data.

<a id='6'></a>
<div class="list-group" id="list-tab" role="tablist">
<p style="background-color:#000000;font-family:candaralight;color:#ffffff;font-size:175%;text-align:center;border-radius:10px 10px;"> Model Comparison </p>

By comparing the results of different models, we can determine which approach yields the best performance for our specific problem. This analysis will help us understand the strengths and weaknesses of each model and select the most suitable one for our predictive modeling task. Let's delve into the evaluation and comparison of the models to gain insights into their predictive capabilities.
"""

models = ['Baseline', 'Linear Regression', 'Support Vector Regression', 'Random Forest Regression', 'LSTM']
mse_scores = [mse_baseline, mse_lr, mse_svr, mse_rf, mse_lstm]
rmse_scores = [rmse_baseline, rmse_lr, rmse_svr, rmse_rf, rmse_lstm]
mae_scores = [mae_baseline, mae_lr, mae_svr, mae_rf, mae_lstm]
mape_scores = [mape_baseline, mape_lr, mape_svr, mape_rf, mape_lstm]
r2_scores = [r2_baseline, r2_lr, r2_svr, r2_rf, r2_lstm]

# Create a dataframe to store the evaluation metrics
evaluation_df = pd.DataFrame({'Model': models, 'MSE': mse_scores, 'RMSE': rmse_scores, 'MAE': mae_scores, 'MAPE': mape_scores, 'R2 Score': r2_scores})
evaluation_df.set_index('Model', inplace=True)

# Print the evaluation metrics
print(evaluation_df)

"""The table presents the evaluation metrics for different models:

**1. Baseline:** This model has a high MSE of 965.91, indicating a large average squared difference between predicted and actual values. The RMSE of 31.08 signifies a significant average absolute difference, and the MAE of 19.45 represents a substantial average absolute error. The MAPE of 4091.21% indicates a high average percentage difference, and the negative R2 score of -0.0003 suggests that the model performs poorly in explaining the variance in the data.

**2. Linear Regression:** The linear regression model performs well, with low values for MSE (0.062), RMSE (0.249), MAE (0.072), and MAPE (0.813%). The high R2 score of 0.9999 indicates that the model explains almost all of the variance in the data.

**3. Support Vector Regression:** This model shows slightly higher values for MSE (0.165), RMSE (0.406), MAE (0.157), and MAPE (21.41%). The R2 score of 0.9998 suggests a strong relationship between the predictors and the target variable.

**4. Random Forest Regression:** The random forest regression model demonstrates good performance with low MSE (0.130), RMSE (0.361), MAE (0.100), and MAPE (0.867%) values. The R2 score of 0.9999 indicates a high degree of variance explained by the model.

**5. LSTM:** The LSTM model performs reasonably well, with an MSE of 12.414, RMSE of 3.523, MAE of 2.742, and MAPE of 1.995%. The R2 score of 0.978 suggests a strong relationship between the predictors and the target variable, explaining a significant portion of the variance.

Overall, the linear regression, support vector regression, random forest regression, and LSTM models outperform the baseline model in terms of prediction accuracy, with the LSTM model exhibiting good performance across multiple evaluation metrics.
"""

