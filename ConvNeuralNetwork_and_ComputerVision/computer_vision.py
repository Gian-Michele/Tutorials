# Computer Vision is algorithm that find pattarn in the images
import zipfile
import wget
import os
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator

import pathlib
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import random

download_dataset = False
gen_model = False


def gen_cnn_model(train_data, valid_data):
    # Create a CNN model (same as Tiny VGG - https://poloclub.github.io/cnn-explainer/)
    model_cnn = tf.keras.models.Sequential([
    tf.keras.layers.Conv2D(filters=10, 
                           kernel_size=3,  # can also be (3, 3)
                           activation="relu", 
                           input_shape=(224, 224, 3)),     # first layer specifies input shape (height, width, colour channels)
    tf.keras.layers.Conv2D(30, 3, activation="relu"),
    tf.keras.layers.MaxPool2D(pool_size=2,      # pool_size can also be (2, 2)
                              padding="valid"), # padding can also be 'same'
    tf.keras.layers.Conv2D(20, 3, activation="relu"),
    tf.keras.layers.Conv2D(10, 3, activation="relu"), # activation='relu' == tf.keras.layers.Activations(tf.nn.relu)
    tf.keras.layers.MaxPool2D(2),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(1, activation="sigmoid") # binary activation output
    ])

    # Compile the model using typical configuration for binary classification
    model_cnn.compile(loss="binary_crossentropy",
                optimizer=tf.keras.optimizers.Adam(),
                metrics=["accuracy"])

    # Fit the model
    history_cnn = model_cnn.fit(train_data,
                            epochs=10,
                            steps_per_epoch=len(train_data),
                            validation_data=valid_data,
                            validation_steps=len(valid_data))
    
    if path_where_save is not None:
        model_cnn.save(path_where_save+'/cnn_model')
    
    return model_cnn, history_cnn


def view_random_image(target_dir: str, target_class: str):
  """ Read an images from a directory for a specific class (witch is a subdurectory)"""
  # Setup target directory (we'll view images from here)
  target_folder = target_dir+target_class

  # Get a random image path
  random_image = random.sample(os.listdir(target_folder), 1)

  # Read in the image and plot it using matplotlib
  img = mpimg.imread(target_folder + "/" + random_image[0])
  plt.imshow(img)
  plt.title(target_class)
  plt.axis("off");

  return img



#-------------------------------------------------------
# Start  Things
if __name__ == '__main__':
    print(f"TF version: {tf.__version__}")
    # define a path where save output
    path_where_save = os.getcwd()+'/ConvNeuralNetwork_and_ComputerVision'
    print(f'the ouput will be saved on {path_where_save}')

    if download_dataset is True:
        # Download zip file of pizza_steak images
        url = "https://storage.googleapis.com/ztm_tf_course/food_vision/pizza_steak.zip"
        filename = wget.download(url)
        print(f'downloaded: {filename}')

        # Unzip the downloaded file
        zip_ref = zipfile.ZipFile(filename, "r")
        zip_ref.extractall()
        zip_ref.close()

    for dirpath, dirnames, filename in os.walk('pizza_steak'):
        print(f'there are {len(filename)} files in directories: {dirnames} in the path: {dirpath}')

    # Classification based on the name of the subdirectories
    data_dir = pathlib.Path("pizza_steak/train/")   # turn our training path into a Python path
    class_names = np.array(sorted([item.name for item in data_dir.glob('*')])) # created a list of class_names from the subdirectories
    print(class_names)

    # look an image from training dataset
    examle_of_steak_img = view_random_image(target_dir='pizza_steak/train/', target_class='steak')

    examle_of_pizza_img = view_random_image(target_dir='pizza_steak/train/', target_class='pizza')

    print(f'steak image value: {examle_of_steak_img} the dimension is: {examle_of_steak_img.shape} ')

    print(f'pizza image value: {examle_of_pizza_img} the dimension is: {examle_of_pizza_img.shape} ')
    
    

    # Set the seed
    tf.random.set_seed(42)

    # Preprocess data (get all of the pixel values between 1 and 0, also called scaling/normalization)
    # this class can help in format images of different dimension
    train_datagen = ImageDataGenerator(rescale=1./255)
    valid_datagen = ImageDataGenerator(rescale=1./255)


    # Setup the train and test directories
    train_dir = "pizza_steak/train/"
    test_dir = "pizza_steak/test/"

    # Import data from directories and turn it into batches 
    # Put images in pool of batches to save memory of the machine
    train_data = train_datagen.flow_from_directory(train_dir,
                                                batch_size=32,  # number of images to process at a time 
                                                target_size=(224, 224), # convert all images to be 224 x 224
                                                class_mode="binary",    # type of problem we're working on
                                                seed=42)

    valid_data = valid_datagen.flow_from_directory(test_dir,
                                                batch_size=32,  # number of images to process at a time 
                                                target_size=(224, 224), # convert all images to be 224 x 224
                                                class_mode="binary",    # type of problem we're working on
                                                seed=42)

    
    if gen_model is True:
        cnn_model, model_history = gen_cnn_model(train_data, valid_data)
    else:
        cnn_model = tf.keras.models.load_model(path_where_save+"/cnn_model")

    #loss, accuracy = cnn_model.evaluate(train_data, valid_data)
    cnn_model.summary()