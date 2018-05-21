import keras
import numpy
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation
from keras.optimizers import SGD
from utils import dataset_generator
from utils import total_number
from utils import weight_class
from sklearn.metrics import confusion_matrix

numpy.set_printoptions(threshold=numpy.inf)

#41 -- 51

trainable = 'True'


#emotions = ['ang','dis','exc','fea','fru','hap','neu','oth','sad','sur','xxx']
emotions = ['sad','hap']#,'ang','exc']
size_batch = 32
frame_number = 20


model = Sequential()
model.add(Dense(64, activation='sigmoid', input_dim=frame_number*33, name='dense_1',kernel_initializer='VarianceScaling'))
#model.add(Dropout(0.5))
model.add(Dense(32, activation='sigmoid', name='dense_2',kernel_initializer='VarianceScaling'))
#model.add(Dropout(0.5))
model.add(Dense(16, activation='sigmoid', name='dense_3',kernel_initializer='VarianceScaling'))
#model.add(Dropout(0.5))
model.add(Dense(8, activation='sigmoid', name='dense_4',kernel_initializer='VarianceScaling'))
#model.add(Dropout(0.5))
#model.add(Dense(100, activation='sigmoid', trainable=trainable,name='dense_5'))
#model.add(Dense(64, activation='sigmoid', trainable=trainable,name='dense_6'))
#model.add(Dense(32, activation='sigmoid', trainable=trainable,name='dense_7'))
#model.add(Dense(16, activation='sigmoid', trainable=trainable,name='dense_8'))
#model.add(Dense(8, activation='sigmoid', trainable=trainable,name='dense_9'))
#model.add(Dropout(0.5))
model.add(Dense(len(emotions), activation='softmax',name='dense_55j'))


#some possible optimizer

adam =keras.optimizers.Adam(lr=0.0000001, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0, amsgrad=False)
sgd = SGD(lr=0.00000005, decay=1e-6, momentum=0.9, nesterov=True)

#lr=0.0000001
model.compile(loss='categorical_crossentropy',
              optimizer=sgd,
              metrics=['accuracy'])

train_size,_,_ = total_number('train','M',emotions,size_batch,frame_number)
validation_size,_,_ = total_number('test','M',emotions,size_batch,frame_number)
test_size,_,_ = total_number('test','M',emotions,size_batch,frame_number)

print("\nsize of train "+str(train_size)+"\n")
print("size of test_size "+str(test_size)+"\n")


train_generator = dataset_generator(size_batch,'train','M',emotions,frame_number)
validation_generator = dataset_generator(size_batch,'validation','M',emotions,frame_number)
test_generator = dataset_generator(size_batch,'test','M',emotions,frame_number)
train_generator_overfit = dataset_generator(size_batch,'test','M',emotions,frame_number)

class_weight_dict = weight_class('train',emotions,'M')



model.fit_generator(train_generator, steps_per_epoch=train_size, epochs=200,shuffle=True,class_weight=class_weight_dict)

pred = model.predict_generator( train_generator_overfit, steps=test_size)

print(numpy.sum(pred > 1/len(emotions),axis=0))


print(model.evaluate_generator( train_generator_overfit, steps=test_size))


#model.load_weights('weights',by_name=False)
#model.save_weights("weights")




