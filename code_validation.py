import keras
import numpy
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation
from keras.optimizers import SGD
from utils import dataset_generator
from utils import total_number
from utils import weight_class
from utils import static_dataset
from sklearn.metrics import confusion_matrix
from keras.layers.normalization import BatchNormalization



numpy.set_printoptions(threshold=numpy.inf)


trainable = 'True'


#emotions = ['ang','dis','exc','fea','fru','hap','neu','oth','sad','sur','xxx']
emotions = ['hap','sad','ang','exc']
size_batch2 = 32
frame_number = 50

x,y,class_weight_dict = static_dataset('train','M',emotions,frame_number)
x_test,y_test,class_weight_dict_test = static_dataset('test','M',emotions,frame_number)


x = tf.keras.utils.normalize(x,    axis=-1,    order=2)

#search parameters for hyperparameter optimization
batch_sizes = [16, 32, 64, 128, 256]
epochs = [10, 50, 100]
#optimizers = [sgd, rmsdrop, adagrad, adadelta, adam, adamax, nadam]
learn_rates = [0.00001, 0.0001, 0.001, 0.01, 0.1, 0.2]
activations = ['softmax', 'softplus', 'softsign', 'relu', 'tanh', 'sigmoid', 'hard_sigmoid', 'linear']
dropout_rates = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
hidden1_neurons = [16, 32, 64, 128, 256]
hidden2_neurons = [16, 32, 64, 128, 256]
hidden3_neurons = [16, 32, 64, 128, 256]
hidden4_neurons = [16, 32, 64, 128, 256]


for activation in activations:
	for dropout in dropout_rates:
		for hidden1 in hidden1_neurons:
			for hidden2 in hidden2_neurons:
				for hidden3 in hidden3_neurons:
					for hidden4 in hidden4_neurons:
						model = Sequential()
						model.add(Dense(256, activation='relu', input_dim=frame_number*33, name='dense_1',kernel_initializer='glorot_normal'))
						model.add(Dropout(0.5))
						model.add(Dense(128, activation='relu', name='dense_2',kernel_initializer='glorot_normal'))
						model.add(Dropout(0.5))
						model.add(Dense(64, activation='relu', name='dense_3',kernel_initializer='glorot_normal'))
						model.add(Dropout(0.5))
						model.add(Dense(32, activation='relu', name='dense_4',kernel_initializer='glorot_normal'))

						model.add(Dense(len(emotions), activation='softmax',name='dense_f'))

						for learn_rate in learn_rates:
							sgd = SGD(lr=learn_rate, decay=1e-6, momentum=0.9, nesterov=False)
							rmsdrop = keras.optimizers.RMSprop(lr=learn_rate, rho=0.9, epsilon=None, decay=0.0)
							adagrad = keras.optimizers.Adagrad(lr=learn_rate, epsilon=None, decay=0.0)
							adadelta = keras.optimizers.Adadelta(lr=learn_rate, rho=0.95, epsilon=None, decay=0.0)
							adam =keras.optimizers.Adam(lr=learn_rate, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0, amsgrad=False)
							adamax = keras.optimizers.Adamax(lr=learn_rate, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0)
							nadam = keras.optimizers.Nadam(lr=learn_rate, beta_1=0.9, beta_2=0.999, epsilon=None, schedule_decay=0.004)

							optimizers = [sgd, rmsdrop, adagrad, adadelta, adam, adamax, nadam]

							#optimizer
							#adam =keras.optimizers.Adam(lr=0.0005, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0, amsgrad=False)
							#sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)

							for batchSize in batch_sizes:
								for epoch in epochs:
									for optimizer in optimizers:

									model.compile(loss='categorical_crossentropy',
									              optimizer=adam,
									              metrics=['accuracy'])

									with open("code_validation_results.txt", 'a') as outputFile:
										outputFile.write("\n   ---training---")
										outputFile.write(numpy.sum(model.predict(x=x,batch_size=1)> 1/len(emotions),axis=0))


									model.fit(x=x,y=y,batch_size=size_batch2, epochs=300,shuffle=True,class_weight=class_weight_dict)

									with open("code_validation_results.txt", 'a') as outputFile:
										outputFile.write("\n   ---training---")
										outputFile.write(numpy.sum(model.predict(x=x,batch_size=1)> 1/len(emotions),axis=0))

										outputFile.write("\n   ---test---  ")
										outputFile.write(numpy.sum(model.predict(x=x_test,batch_size=1)> 1/len(emotions),axis=0))
										outputFile.write(model.evaluate(x=x_test,y=y_test,batch_size=1))
