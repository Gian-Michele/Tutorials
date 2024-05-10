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
import datetime

create_model = True
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
    model.build([None, 244, 244, 3])  # Batch input shape (244, 244, 3).

    return model


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
    # creating a model starting from url_model
    external_model = create_model(efficientnet_url, 10)
    external_model.summary()# Compile the model using typical configuration for Multiclass classification
   
    #Compile the model
    # Compile the model using typical configuration for Multiclass classification
    external_model.compile(loss="categorical_crossentropy",
                    optimizer=tf.keras.optimizers.Adam(),
                    metrics=["accuracy"])
    
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
    train_datagen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1./255)
    # this class can help in normalizing images of different dimension
    test_datagen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1./255)

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

    history_model = external_model.fit(train_data,
                        epochs=5,
                        steps_per_epoch=len(train_data),
                        validation_data=test_data,
                        validation_steps=len(test_data),
                        # Add TensorBoard callback to model (callbacks parameter takes a list)
                        callbacks=[create_tensorboard_callback(dir_name="tensorflow_hub", # save experiment logs here
                                                                experiment_name="resnet50V2")]) # name of log files


    plot_loss(history_model)
    external_model.save('exploring_model/'+model_name)
    