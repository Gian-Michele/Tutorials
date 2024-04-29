
import zipfile
import wget
import os
import tensorflow as tf
#from tensorflow.keras.preprocessing.image import ImageDataGenerator

import pathlib
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import random
import pandas as pd
import sys

PATH = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + '..' + os.path.sep 
sys.path.append(PATH)
from Classification_Example import binary_classification
from Classification_Example.multi_class_classification import plot_random_image
from computer_vision_with_augmented_data import view_random_image, plot_loss, pred_and_plot

download_dataset = False
gen_model = True    # if False the cnn_model_2 will be used
model_name = "multiclass_cnn_2nd"



def gen_cnn_model(train_data, test_data):
    # Create a CNN model (same as Tiny VGG - https://poloclub.github.io/cnn-explainer/)
    # The number of filter could improve the performance from 10 to 32 or 64
    model_cnn = tf.keras.models.Sequential([
        tf.keras.layers.Conv2D(filters=10,              # Number of Filter per Layer will pass throught the immage
                               kernel_size=3,           # Measn (3, 3), is the dimension of the filter (typcal 3, 5, 7), larger value idefify larger thind
                               activation="relu", 
                               strides=1,               # means (1, 1) is default value, is the step of the filter in the image in the two image direction.
                               input_shape=(224, 224, 3)),     # first layer specifies input shape (height, width, colour channels)
        
        tf.keras.layers.MaxPool2D(pool_size=2,          # pool_size can also be (2, 2) -> take the max of a 2x2 matrix reducing the number of element find the most important element of the pixel
                                padding="valid"),       # padding can also be 'same' in case to maintain the same output inserting zeros, in case of valid the outpu is compressed
                                                        # using "valid" we lose the edge of the image
        tf.keras.layers.Conv2D(10, 3, activation="relu"),
        tf.keras.layers.MaxPool2D(pool_size=2,          # pool_size can also be (2, 2)
                                padding="valid"),       # padding can also be 'same' in case to maintain the same output inserting zeros, in case of valid the outpu is compressed
        tf.keras.layers.Conv2D(10, 3, activation="relu"), # activation='relu' == tf.keras.layers.Activations(tf.nn.relu)
        tf.keras.layers.MaxPool2D(),                    # default input similar to the others
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(10, activation="softmax") # MultiClass Classification activation output
    ])

    # Compile the model using typical configuration for Multiclass classification
    model_cnn.compile(loss="categorical_crossentropy",
                optimizer=tf.keras.optimizers.Adam(),
                metrics=["accuracy"])

    # Fit the model. 
    # The  number of epochs can improve the performance
    history_cnn = model_cnn.fit(train_data,
                            epochs=20,
                            steps_per_epoch=len(train_data),
                            validation_data=test_data,
                            validation_steps=len(test_data))
    
    # visualization of the training process
    plot_loss(history=history_cnn)
    if path_where_save is not None:
        # the new model name
        model_cnn.save(path_where_save+'/'+model_name)
    
    return model_cnn, history_cnn



#-------------------------------------------------------
# Start  Things
if __name__ == '__main__':
    print(f"TF version: {tf.__version__}")
    # define a path where save output
    path_where_save = os.getcwd()+'/ConvNeuralNetwork_and_ComputerVision'
    print(f'the ouput will be saved on {path_where_save}')

    if download_dataset is True:
        if os.path.exists('10_food_classes_all_data.zip') is False: 
            # Download zip file for food classification - more food image can be found in food-101: https://www.kaggle.com/datasets/dansbecker/food-101
            url = "https://storage.googleapis.com/ztm_tf_course/food_vision/10_food_classes_all_data.zip"
            filename = wget.download(url)
            print(f'downloaded: {filename}')

            # Unzip the downloaded file
            zip_ref = zipfile.ZipFile(filename, "r")
            zip_ref.extractall()
            zip_ref.close()
        else:
            print('the file already exist')
    
        for dirpath, dirname, filename in os.walk('10_food_classes_all_data'):
            print(f'therare {len(dirname)} directories and {len(filename)} files in {dirpath}')

    train_dir = '10_food_classes_all_data/train'
    test_dir = '10_food_classes_all_data/test'

    # in order to merge in a single directory the 10 directory containing differnt type of food
    data_train_dir = pathlib.Path(train_dir)
    class_name = np.array(sorted([item.name for item in data_train_dir.glob('*')]))
    print(class_name)

    # random viw images from the 10 classes
    for r in range(0,len(class_name)):
        plt.figure()
        img = view_random_image(target_dir=train_dir,
                                target_class=class_name[r])
    

    # Set the seed
    tf.random.set_seed(42)
     
    # Data Augmentation Class - in order to change the image format to obtain data augmentation   
    datagen_augmentation = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1./255,
                                                                    rotation_range=20,
                                                                    zoom_range=0.2,
                                                                    width_shift_range=0.2,
                                                                    height_shift_range=0.3,
                                                                    horizontal_flip=True
                                                                    )
 

    # this class can help in normalizing images of different dimension 
    train_datagen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1./255)
    # this class can help in normalizing images of different dimension
    test_datagen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1./255)

    train_data = datagen_augmentation.flow_from_directory(train_dir,
                                                batch_size=32,  # number of images to process at a time 
                                                target_size=(224, 224), # convert all images to be 224 x 224
                                                class_mode="categorical",    # type of problem we're working on
                                                seed=42)

    test_data = test_datagen.flow_from_directory(train_dir,
                                                batch_size=32,  # number of images to process at a time 
                                                target_size=(224, 224), # convert all images to be 224 x 224
                                                class_mode="categorical",    # type of problem we're working on
                                                seed=42)

    
    print(f'{train_data}')
    print(f'{test_data}')

    # select to generate or load the model from the saved one
    if gen_model is True:
        cnn_model, model_history = gen_cnn_model(train_data, test_data)
    else:
        # load the model name: cnn_model_2
        cnn_model = tf.keras.models.load_model(path_where_save+"/"+model_name)

    #loss, accuracy = cnn_model.evaluate(train_data, valid_data)
    cnn_model.summary()

    # image url"
    url1 = "https://raw.githubusercontent.com/mrdbourke/tensorflow-deep-learning/main/images/03-pizza-dad.jpeg"
    url2 = "https://raw.githubusercontent.com/mrdbourke/tensorflow-deep-learning/main/images/03-steak.jpeg"
    url3 = "https://raw.githubusercontent.com/mrdbourke/tensorflow-deep-learning/main/images/03-hamburger.jpeg"
    url4 = "https://raw.githubusercontent.com/mrdbourke/tensorflow-deep-learning/main/images/03-sushi.jpeg"

    if os.path.exists("03-pizza-dad.jpeg") is False:
        image1 = wget.download(url1)
    else:
        image1 = "03-pizza-dad.jpeg"
    #
    if os.path.exists("03-steak.jpeg") is False:
        image2 = wget.download(url2)
    else:
        image2 = "03-steak.jpeg"
    #
    if os.path.exists("03-hamburger.jpeg") is False:
        image3 = wget.download(url3)
    else:
        image3 = "03-hamburger.jpeg"
    #
    if os.path.exists("03-sushi.jpeg") is False:
        image4 = wget.download(url4)
    else:
        image4 = "03-sushi.jpeg"
    #        
    pred_and_plot(model=cnn_model,
                  filename=image1,
                  class_names=class_name,
                  train_data=train_data)
    
    pred_and_plot(model=cnn_model,
                  filename=image2,
                  class_names=class_name,
                  train_data=train_data)
    
    pred_and_plot(model=cnn_model,
                  filename=image3,
                  class_names=class_name,
                  train_data=train_data)
    
    pred_and_plot(model=cnn_model,
                  filename=image4,
                  class_names=class_name,
                  train_data=train_data)
    

    plt.show()