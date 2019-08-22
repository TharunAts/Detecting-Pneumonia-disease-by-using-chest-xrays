# -*- coding: utf-8 -*-
"""pneumonia-xray-detection.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ijP1sPvLPfbPTUmoGsP3RNJHc-4DD842
"""

# Commented out IPython magic to ensure Python compatibility.
#Importing Necessary Libraries and Checking out input data
import pandas
import os
import cv2
from tensorflow.keras.preprocessing.image import load_img,img_to_array,ImageDataGenerator,array_to_img
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense,Dropout,Flatten,Conv2D,BatchNormalization,MaxPooling2D,Activation
from sklearn.metrics import classification_report
from IPython.display import Image, display
import matplotlib
import matplotlib.pyplot as plt
# %matplotlib inline 
import numpy as np
print(os.listdir("/kaggle/input/chest-xray-pneumonia/chest_xray/chest_xray/"))

#Analysing Data and getting insights.
#Displaying images from both classes
train_pneum=os.listdir("/kaggle/input/chest-xray-pneumonia/chest_xray/chest_xray/train/PNEUMONIA")
train_pneum=list(map(lambda x: "/kaggle/input/chest-xray-pneumonia/chest_xray/chest_xray/train/PNEUMONIA/" + x ,train_pneum))
i = 0
plt.rcParams['figure.figsize'] = (10.0, 10.0)
plt.subplots_adjust(wspace=0.2, hspace=0.2)
for l in train_pneum[:10]:
    im = cv2.imread(l)
    im = cv2.resize(im, (128, 128)) 
    plt.subplot(5, 5, i+1).set_title("PNEUMONIA")
    plt.imshow(im); plt.axis('off')
    i = i + 1
train_normal=os.listdir("/kaggle/input/chest-xray-pneumonia/chest_xray/chest_xray/train/NORMAL")
train_normal=list(map(lambda x: "/kaggle/input/chest-xray-pneumonia/chest_xray/chest_xray/train/NORMAL/" + x ,train_normal))
for l in train_normal[:10]:
    im = cv2.imread(l)
    im = cv2.resize(im, (128, 128)) 
    plt.subplot(5, 5, i+1).set_title("NORMAL")
    plt.imshow(im); plt.axis('off')
    i = i + 1

#Analysing Data in train dataset
print("Total number of images in train dataset: " + str(len(train_pneum) + len(train_normal)))
print("Number of xrays containing pneumonia in train dataset " + str(len(train_pneum)))
print("Number of xrays not containing pneumonia in train dataset " + str(len(train_normal)))

#Analysing and preparing test and Validation data
test_pneum=os.listdir("/kaggle/input/chest-xray-pneumonia/chest_xray/chest_xray/test/PNEUMONIA")
test_norm=os.listdir("/kaggle/input/chest-xray-pneumonia/chest_xray/chest_xray/test/NORMAL")
val_pneum=os.listdir("/kaggle/input/chest-xray-pneumonia/chest_xray/chest_xray/val/PNEUMONIA")
val_norm=os.listdir("/kaggle/input/chest-xray-pneumonia/chest_xray/chest_xray/val/NORMAL")
print("Total number of images in test dataset: " + str(len(test_pneum) + len(test_norm) ))
print("Number of xrays containing pneumonia in test dataset " + str(len(test_pneum)))
print("Number of xrays not containing pneumonia in test dataset " + str(len(test_norm)))

#Initialising ImageDataGenerator
Image_gen=ImageDataGenerator(rescale=1/255)
#Preparing train data
traindata_gen=Image_gen.flow_from_directory('../input/chest-xray-pneumonia/chest_xray/chest_xray/train',target_size=[300,300],batch_size=64,class_mode='binary',shuffle=True)
#Preparing test data
testdata_gen=Image_gen.flow_from_directory('../input/chest-xray-pneumonia/chest_xray/chest_xray/test',target_size=[300,300],batch_size=64,class_mode='binary',shuffle=True)
#Preparing Validation data
validation_gen=Image_gen.flow_from_directory('../input/chest-xray-pneumonia/chest_xray/chest_xray/val',target_size=[300,300],batch_size=64,class_mode='binary',shuffle=True)

#Stops training when train and validation accuracy reaches 95%
class myCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('val_acc')>0.95 and logs.get('acc')> 0.95):
      print("\n achieved 90% accuracy on test data so cancelling training!")
      self.model.stop_training = True
callbacks = myCallback()

model=Sequential([
    Conv2D(16,(3,3),input_shape=[300,300,3],activation="relu"),
    MaxPooling2D(2,2),
    Conv2D(32,(3,3),activation="relu"),
    MaxPooling2D(2,2),
    Conv2D(64,(3,3),activation="relu"),
    MaxPooling2D(2,2),
    Conv2D(128,(3,3),activation="relu"),
    MaxPooling2D(2,2),
    Flatten(),
    Dense(512,activation="relu"),
    Dense(1,activation="sigmoid")
])

#compiling model
model.compile(optimizer="adam",loss="binary_crossentropy",metrics=['accuracy'])

#fitting model
history=model.fit_generator(traindata_gen,epochs=5,validation_data=validation_gen,steps_per_epoch=82,validation_steps=1,callbacks=[callbacks])

#Summary of model
model.summary()

#Evaluating accuracy of model
scores = model.evaluate_generator(testdata_gen,624) #624 testing images
print("Accuracy on test model  = ", scores[1])

#Predictions for test data
predictions=model.predict_generator(testdata_gen)
predictions=predictions.round()

#Classification report
y_true = np.array([0] * 234 + [1] * 390)
target_names=["NORMAL","PNEUMONIA"]
print(classification_report(y_true, predictions, target_names=target_names))

#Testing model with a pneumonia sample
image_path="../input/chest-xray-pneumonia/chest_xray/chest_xray/test/PNEUMONIA/person147_bacteria_706.jpeg"
img1=load_img(image_path,target_size=[300,300])
k1=img_to_array(img1)
k1 = k1.reshape((1,k1.shape[0], k1.shape[1],k1.shape[2]))
display(Image(image_path,width=150, height=150))
model.predict_classes(k1)

#Testing model with Normal Sample
image_path="../input/chest-xray-pneumonia/chest_xray/chest_xray/test/NORMAL/NORMAL2-IM-0272-0001.jpeg"
img1=load_img(image_path,target_size=[300,300])
k1=img_to_array(img1)
k1 = k1.reshape((1,k1.shape[0], k1.shape[1],k1.shape[2]))
display(Image(image_path,width=150, height=150))
model.predict_classes(k1)