from __future__ import print_function
import keras
import numpy
from keras.models import Sequential, Model
from keras.layers import Dense, Dropout, Activation, LSTM
from keras.optimizers import SGD
from utils import dataset_generator
from utils import total_number, weight_class
import h5py
import os
from utils import Categorical_label
import math
from RNN import getData
from hyperopt import Trials, STATUS_OK, tpe
from hyperas import optim
from hyperas.distributions import choice, uniform
from keras.preprocessing import sequence
from keras.layers.embeddings import Embedding
# from keras.layers.recurrent import LSTM
from keras.callbacks import EarlyStopping, ModelCheckpoint




batch_size = 128
nb_feat = 33
nb_class = 4
emotions = ['sad','ang', 'neu', 'exc']
frame_number = 50


# def getData(self, sets, emotions, genders, frame_number):
#     data_y = []
#     data_x = []

#     for subset in sets:
#         for emotion in emotions:
#             for gender in genders:
#                 file_name = subset+'_'+emotion+'_'+gender
#                 h5f = h5py.File(os.getcwd()+'/data/'+file_name+'.h5','r')

#                 tmp = h5f[file_name][:]
#                 h5f.close()
#                 hot_encoded_emotion = Categorical_label(emotion, emotions)
#                 a, b = tmp.shape

#                 if data_x == []:
#                     data_x = tmp

#                     data_y = np.tile(hot_encoded_emotion,[a, 1])
					
#                 else:
#                     data_x = np.vstack((tmp, data_x))
#                     temp = np.tile(hot_encoded_emotion, [a, 1])
#                     data_y = np.vstack((data_y, temp))

#     samples = data_x.shape
#     newsize = math.trunc(samples[0]/frame_number)
#     x = np.reshape(data_x[0:newsize*frame_number,:], (newsize, frame_number, 33))
#     # print(y[::20,:].shape)
#     y = data_y[::frame_number,:]
#     y = y[0:newsize,:]
#     return x, y
				
def data():
	# maxlen = 100
	# max_features = 20000
	frame_number= 50
	emotions = ['sad','ang', 'neu', 'exc']
	print('Loading data...')
	X_train, y_train = getData(['train'], emotions, 'M', frame_number)
	X_test, y_test = getData(['test'], emotions, 'M', frame_number)
	print(len(X_train), 'train sequences')
	print(len(X_test), 'test sequences')

	print("Pad sequences (samples x time)")
	# X_train = sequence.pad_sequences(X_train, maxlen=maxlen)
	# X_test = sequence.pad_sequences(X_test, maxlen=maxlen)
	print('X_train shape:', X_train.shape)
	print('X_test shape:', X_test.shape)

	return X_train, X_test, y_train, y_test

def model(X_train, X_test, y_train, y_test):
	frame_number = 50
	nb_feat = 33
	nb_class = 4
	emotions = ['sad','ang', 'neu', 'exc']

	model = Sequential()
	# model.add(Embedding(max_features, 128, input_length=maxlen))
	model.add(LSTM({{choice([128,256,512])}}, return_sequences = True, input_shape=(frame_number, nb_feat)))
	model.add(Activation('tanh'))
	model.add(LSTM({{choice([64, 128,256])}}, return_sequences = False))
	model.add(Activation('tanh'))
	model.add(Dense({{choice([128,256,512])}}))
	model.add(Dropout({{uniform(0, 1)}}))
	model.add(Activation('tanh'))
	model.add(Dense(nb_class))
	model.add(Activation('softmax'))
	class_weight_dict = weight_class('train',emotions,'M')
	model.compile(loss='categorical_crossentropy', optimizer='Adadelta', metrics=['accuracy'])


	early_stopping = EarlyStopping(monitor='val_loss', patience=4)
	checkpointer = ModelCheckpoint(filepath='keras_weights.hdf5',
								   verbose=1,
								   save_best_only=True)

	model.fit(X_train, y_train,
			  batch_size={{choice([32, 64, 128])}},
			  nb_epoch=1,
			  validation_split=0.08,
			  callbacks=[early_stopping, checkpointer])

	score, acc = model.evaluate(X_test, y_test, verbose=0)

	print('Test accuracy:', acc)
	return {'loss': -acc, 'status': STATUS_OK, 'model': model}

best_run, best_model = optim.minimize(model=model,
										  data=data,
										  algo=tpe.suggest,
										  max_evals=10,
										  trials=Trials())
print(best_run)
