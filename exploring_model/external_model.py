# Classification of best model for images: https://paperswithcode.com/sota/image-classification-on-imagenet
# other model in https://www.kaggle.com/models
# Image classification model: 
#   - https://www.kaggle.com/models/tensorflow/resnet-50 (https://www.kaggle.com/models/google/resnet-v2/tensorFlow2/50-feature-vector/1)
#   - https://www.kaggle.com/models/google/efficientnet-v2 (https://www.kaggle.com/models/tensorflow/efficientnet/tensorFlow2/b0-feature-vector/1)

import tensorflow as tf
import tensorflow_hub as hub
import zipfile
import os
import wget
import matplotlib.pyplot as plt
from tensorflow import keras
import datetime

model_generation = True
download_dataset = True

def create_tensorboard_callback(dir_name, experiment_name):
  log_dir = dir_name + "/" + experiment_name + "/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
  tensorboard_callback = tf.keras.callbacks.TensorBoard(
      log_dir=log_dir
  )
  print(f"Saving TensorBoard log files to: {log_dir}")
  return tensorboard_callback

def create_model(model_url: str, num_classes: int) -> tf.keras.Model:
    """ 
    function to create a model from a url and with the dimension of the multi class classification
    Input:
        url: web address of the model
        num_classes: Number of output neurons
    Output:
        keras 
    """

    model = tf.keras.Sequential([
        hub.KerasLayer(model_url,
                   trainable=False,
                   ),  # Can be True, see below.
        tf.keras.layers.Dense(num_classes, activation='softmax')
    ])
    model.build([None, 224, 224, 3])  # Batch input shape (224, 224, 3).

    return model

def decode_img(img):
  # Convert the compressed string to a 3D uint8 tensor
  img = tf.io.decode_jpeg(img, channels=3)
  img_height = 224
  img_width = 224
  # Resize the image to the desired size
  return tf.image.resize(img, [img_height, img_width])

def process_path(file_path):
  # Load the raw data from the file as a string
  img = tf.io.read_file(file_path)
  img = decode_img(img)



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


#-------------------------------------------------------
# Start  Things
if __name__ == '__main__':
    print(f"TF version: {tf.__version__}")
    resnet_url = "https://www.kaggle.com/models/google/resnet-v2/tensorFlow2/50-feature-vector/1"
    efficientnet_url = "https://www.kaggle.com/models/tensorflow/efficientnet/tensorFlow2/b0-feature-vector/1"

    model_name = 'efficient_net'
        
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
    
    train_dir = '10_food_classes_all_data/train'
    test_dir = '10_food_classes_all_data/test'
    # this class can help in normalizing images of different dimension 
    train_datagen = keras.preprocessing.image.ImageDataGenerator(rescale=1./255)
    # this class can help in normalizing images of different dimension
    test_datagen = keras.preprocessing.image.ImageDataGenerator(rescale=1./255)

    train_data = train_datagen.flow_from_directory(train_dir,
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

    if model_generation is True:
        # Creating a model starting from url_model
        external_model = create_model(efficientnet_url, 10)
    
        # Compile the model using typical configuration for Multiclass classification
        external_model.compile(loss="categorical_crossentropy",
                        optimizer=tf.keras.optimizers.Adam(),
                        metrics=["accuracy"])
        
        # Fit the model with the hold dataset
        history_model = external_model.fit(train_data,
                            epochs=5,
                            steps_per_epoch=len(train_data),
                            validation_data=test_data,
                            validation_steps=len(test_data),
                            # Add TensorBoard callback to model (callbacks parameter takes a list)
                            callbacks=[create_tensorboard_callback(dir_name="tensorflow_hub",       # save experiment logs here
                                                                    experiment_name=model_name)])   # name of log files
    
        # Save new model
        external_model.save(model_name)

        # plot fitting process
        plot_loss(history_model)
    
    else:
        # load model
        external_model :keras.Model = keras.models.load_model(model_name)
        # model evaluation: https://www.tensorflow.org/tutorials/load_data/images
        #import pathlib
        #train_imag_dir = pathlib.Path(train_dir)
        #image_count = len(list(train_imag_dir.glob('*/*.jpg')))
        #train_ds = tf.data.Dataset.list_files(str(train_imag_dir/'*/*'), shuffle=False)
        #train_ds.reduce
        
        #test_imag_dir = pathlib.Path(test_dir)
        #image_count = len(list(test_imag_dir.glob('*/*.jpg')))
        #list_ds = tf.data.Dataset.list_files(str(train_imag_dir/'*/*'), shuffle=False)
    

        #train_imag_list = get_images(train_dir)
        #test_imag_list = get_images(test_dir)
        #train_imag = tf.convert_to_tensor(train_imag_list)
        #test_imag = tf.convert_to_tensor(test_imag_list)

        #evaluation_result = external_model.evaluate(train_imag_list, test_imag_list)
        #print(evaluation_result)
    
    # model summary
    external_model.summary()
     
    