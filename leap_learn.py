from __future__ import print_function
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.models import load_model
from keras.layers.core import Dense, Dropout, Activation
from keras.optimizers import SGD
from keras.utils import np_utils
#from __future__ import absolute_import
#from __future__ import unicode_literals
from time import gmtime, strftime
from keras.callbacks import TensorBoard
import os
import matplotlib.pyplot as plt


def make_tensorboard(set_dir_name=''):
    tictoc = strftime("%a_%d_%b_%Y_%H_%M_%S", gmtime())
    directory_name = tictoc
    log_dir = set_dir_name + '_' + directory_name
    os.mkdir(log_dir)
    tensorboard = TensorBoard(log_dir=log_dir, write_graph=True, )
    return tensorboard

np.random.seed(1671)  # for reproducibility

# network and training
DROPOUT = 0.2
category = ["グー", "チョキ", "パー"]

# data: shuffled and split between train and test sets
read_data0 = pd.read_csv('./20181211164814_0.csv', sep=',', index_col=0)
read_data1 = pd.read_csv('./20181211165353_1.csv', sep=',', index_col=0)
read_data2 = pd.read_csv('./20181211164924_2.csv', sep=',', index_col=0)
read_data = pd.concat([read_data0, read_data1, read_data2], ignore_index=True)
data = read_data.drop("label", axis=1).values
label = read_data["label"].values

x_train, x_test, y_train, y_test = train_test_split(data, label, test_size=0.2)

# normalize
print(x_train.shape[0], 'train samples')
print(x_test.shape[0], 'test samples')

# convert class vectors to binary class matrices
y_train = np_utils.to_categorical(y_train, len(category))
y_test = np_utils.to_categorical(y_test, len(category))

model = Sequential()
model.add(Dense(512, activation="relu", input_shape=(x_train.shape[1], )))
model.add(Dropout(DROPOUT))
model.add(Dense(512, activation="relu"))
model.add(Dropout(DROPOUT))
model.add(Dense(len(category), activation="softmax"))
model.summary()

model.compile(loss='categorical_crossentropy',
              optimizer=SGD(),
              metrics=['accuracy'])
model.save('./janken_model.h5')

# モデルを読み込む --- (*4)
model = load_model('./janken_model.h5')
# 既に学習データがあれば読み込む --- (*5)
if os.path.exists('./janken_weights.h5'):
    model.load_weights('./janken_weights.h5')

callbacks = [make_tensorboard(set_dir_name='TensorBoard')]

print("train start")
hist = model.fit(x_train, y_train,
                 batch_size=128, 
                 epochs=200,
                 callbacks=callbacks,
                 verbose=1, 
                 validation_split=0.2)

score = model.evaluate(x_test, y_test, verbose=1)
print("\nTest loss:", score[0])
print('Test accuracy:', score[1])
model.save_weights('janken_weights.h5')

# 学習の様子をグラフへ描画
# 正解率の推移をプロット
plt.plot(hist.history['acc'])
plt.plot(hist.history['val_acc'])
plt.title('Accuracy')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

# ロスの推移をプロット
plt.plot(hist.history['loss'])
plt.plot(hist.history['val_loss'])
plt.title('Loss')
plt.legend(['train', 'test'], loc='upper left')
plt.show()


