# Computer Vision 2 is algorithm that find pattarn in the images
# this v2 is used to find a way to combat the overfitting problem that impact the version 1
# - use maxpool to reduce the dimension of the image maitaining only max values
# - data augmentation using ImageDataGeneration

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

download_dataset = False
gen_model = True    # if False the cnn_model_2 will be used


def gen_cnn_model(train_data, valid_data):
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
        tf.keras.layers.MaxPool2D(2),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(1, activation="sigmoid") # binary activation output
    ])

    # Compile the model using typical configuration for binary classification
    model_cnn.compile(loss="binary_crossentropy",
                optimizer=tf.keras.optimizers.Adam(),
                metrics=["accuracy"])

    # Fit the model. 
    # The  number of epochs can improve the performance
    history_cnn = model_cnn.fit(train_data,
                            epochs=10,
                            steps_per_epoch=len(train_data),
                            validation_data=valid_data,
                            validation_steps=len(valid_data))
    
    # visualization of the training process
    plot_loss(history=history_cnn)
    if path_where_save is not None:
        # the new model name
        model_cnn.save(path_where_save+'/cnn_model_2')
    
    return model_cnn, history_cnn


def view_random_image(target_dir: str, target_class: str):
  """ Read an images from a directory for a specific class (witch is a subdurectory)"""
  # Setup target directory (we'll view images from here)
  target_folder = target_dir+target_class

  # Get a random image path
  random_image = random.sample(os.listdir(target_folder), 1)

  # Read in the image and plot it using matplotlib
  img = mpimg.imread(target_folder + "/" + random_image[0])
  plt.figure()
  plt.imshow(img)
  plt.title(target_class)
  plt.axis("off");

  return img

def plot_loss(history):
    """ Return Loss curves and accuracy curve of the model
    """
    loss = history.history["loss"]
    val_loss = history.history["val_loss"]
    accuracy = history.history["accuracy"]
    val_accuracy = history.history["val_accuracy"]
    epochs = range(len( history.history["loss"]))
    # plot loss
    plt.figure()
    plt.plot(epochs, loss, label="training_loss")
    plt.plot(epochs, val_loss, label="val_loss")
    plt.title("loss")
    plt.xlabel("epochs")
    plt.legend()

    # plot accuracy
    plt.figure()
    plt.plot(epochs, accuracy, label="training_accuracy")
    plt.plot(epochs, val_accuracy, label="val_accuracy")
    plt.title("accuracy")
    plt.xlabel("epochs")
    plt.legend()

# Create a function to import an image and resize it to be able to be used with our model
def load_and_prep_image(filename, img_shape=224):
    """
    Reads an image from filename, turns it into a tensor  and reshapes it to (img_shape, img_shape, colour_channel).
    """
    # Read in target file (an image) and transform in a tensor
    img = tf.io.read_file(filename)

    # Decode the read file into a tensor & ensure 3 colour channels 
    # (our model is trained on images with 3 colour channels and sometimes images have 4 colour channels)
    img = tf.image.decode_image(img, channels=3)

    # Resize the image (to the same size our model was trained on)
    img = tf.image.resize(img, size = [img_shape, img_shape])

    # Rescale the image (get all values between 0 and 1)
    img = img/255.
    return img

# prediction and plot of the image
def pred_and_plot(model, filename, class_names, train_data):
    """
    Imports an image located at filename, makes a prediction on it with a trained model and plots the image with the predicted class as the title.
    Train_data are needed to check the dimension of the images
    """

    print("------------------------------------------")
    # this step is to format the image in the correct shape to use in our model
    if train_data.image_shape != steak.shape:
        resize_steak = load_and_prep_image(filename, img_shape=train_data.image_shape[0])
        print("Images have different shapes")
        if train_data.image_shape != resize_steak.shape:
            print("Images have allready different shapes")
            exit(1)
        else:
            print("Image now have the same shape")
    else:
        print("Image now have the same shape")
    print("-------------------------------------------")
    resize_steak_dimx_4 = tf.expand_dims(resize_steak, axis=0) # increase the size to 4 from [244, 244 ,3] to [ 1, 244, 244, 3] required to input in a prediction
    pred = model.predict(resize_steak_dimx_4)
    print(f"Probability of Result is {pred} this means that it is a: {class_names[int(tf.round(pred))]}")

    # Get the predicted class
    pred_class = class_names[int(tf.round(pred)[0][0])]

    # Plot the image and predicted class
    plt.figure()
    plt.imshow(resize_steak)
    plt.title(f"Prediction: {pred_class}")
    plt.axis(False);

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

    # Data Augmentation Class - in order to change the image format   
    train_datagen_augmentation = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1./255,
                                                                    rotation_range=0.2,
                                                                    zoom_range=0.2,
                                                                    width_shift_range=0.2,
                                                                    height_shift_range=0.3,
                                                                    horizontal_flip=True
                                                                    )
    # this class can help in normalizing images of different dimension 
    train_datagen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1./255)
    # this class can help in normalizing images of different dimension
    valid_datagen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1./255)

    # Setup the train and test directories
    train_dir = "pizza_steak/train/"
    test_dir = "pizza_steak/test/"

    # Import data from directories and turn it into batches 
    # Put images in pool of batches to save memory of the machine
    augmented_train_data = train_datagen_augmentation.flow_from_directory(train_dir,
                                                batch_size=32,  # number of images to process at a time 
                                                target_size=(224, 224), # convert all images to be 224 x 224
                                                class_mode="binary",    # type of problem we're working on
                                                seed=42)


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
    
    # select to generate or load the model from the saved one
    if gen_model is True:
        cnn_model, model_history = gen_cnn_model(augmented_train_data, valid_data)
    else:
        # load the model name: cnn_model_2
        cnn_model = tf.keras.models.load_model(path_where_save+"/cnn_model_2")

    #loss, accuracy = cnn_model.evaluate(train_data, valid_data)
    cnn_model.summary()

     # Additional immage to predict
    if download_dataset is True:
        url = "https://raw.githubusercontent.com/mrdbourke/tensorflow-deep-learning/main/images/03-steak.jpeg"
        new_stack_image = wget.download(url)
    else:
        new_stack_image = "03-steak.jpeg"    
    steak = mpimg.imread(new_stack_image)
    
    pred_and_plot(model=cnn_model,
                  filename=new_stack_image,
                  class_names=class_names,
                  train_data=train_data)

    plt.show()