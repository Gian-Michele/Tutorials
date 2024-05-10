# Import required libraries
import tensorflow as tf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from os import getcwd
import os
import sys
import random
#import binary_classification as bc
PATH = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + '..' + os.path.sep 
sys.path.append(PATH)
from Classification_Example.binary_classification import custom_confusion_matrix

show_figure = True
already_saved_model = True

def normalization(data):
    max = data.max()
    data = data/max
    return data

# Create a function for plotting a random image along with its prediction
def plot_random_image(model, images, true_labels, classes):
    """Picks a random image, plots it and labels it with a predicted and truth label.

    Args:
        model: a trained model (trained on data similar to what's in images).
        images: a set of random images (in tensor form).
        true_labels: array of ground truth labels for images.
        classes: array of class names for images.

    Returns:
        A plot of a random image from `images` with a predicted class label from `model`
        as well as the truth class label from `true_labels`.
    """
    # Setup random integer
    i = random.randint(0, len(images))

    # Create predictions and targets
    target_image = images[i]
    pred_probs = model.predict(target_image.reshape(1, 28, 28)) # have to reshape to get into right size for model
    pred_label = classes[pred_probs.argmax()]
    true_label = classes[true_labels[i]]
    
    plt.figure()
    # Plot the target image
    plt.imshow(target_image, cmap=plt.cm.binary)

    # Change the color of the titles depending on if the prediction is right or wrong
    if pred_label == true_label:
        color = "green"
    else:
        color = "red"

    # Add xlabel information (prediction/true label)
    plt.xlabel("Pred: {} {:2.0f}% (True: {})".format(pred_label,
                                                    100*tf.reduce_max(pred_probs),
                                                    true_label),
                                                    color=color) # set the color to green or red

## Generic function for tensor flow generation model for multiclass classification (respect binary calssification loss function is CategoricalCrossenstropy)
def generic_tf_model(X_train, X_test, y_train, y_test, path:str=None, seed: int=None) -> tf.keras.Model:
    """ A Generic function to create a valid model for Binary Classification
        - Input is the size of the numeber of information (size of the images)
        - Relu as activation functin for 2 Dense layer
        - Sigmoid as activation function for the last layer (output Layer)
        - Output layer is the number of category
        - SparseCatecoricalCrossentropy for Classification (output 1,2 3 ...)  while CatecoricalCrossentropy require hot_one vector[0, 0, 1, 0, 0]
        - Adam for optimization: optimal learning rate 0.01 - 0.001 (look to dinamic adapt the learning rate tf.keras.callbacks.LearningRateScheduler)
    """
    if seed is not None:
        tf.random.set_seed(seed) # to alway start with the same weights
    # --------------------------------------------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------- Model for Binary Classification
    # Try introducing non linearity in model using relu activation fuction: (number of layer and neuron can be increased)
    tf_model = tf.keras.Sequential([
        tf.keras.layers.Flatten(input_shape=(28,28)),
        tf.keras.layers.Dense(100, activation="relu"),      # typical activation function used is Relu
        tf.keras.layers.Dense(20, activation="relu"),
        tf.keras.layers.Dense(10, activation=tf.keras.activations.softmax)      # the output has to be softmax for 10 categry 
       
    ])
    # Accuracy can be used for classification, similarly to the type of loss function
    # metric could be:
    # - accuracy: default value for classification -> metrics=tf.keras.metrics.Accuracy()
    # - precision: less false positive -> metrics=tf.keras.metrics.Precision()
    # - recall: less false negative -> metrics=tf.keras.metrics.Recall()
    tf_model.compile(loss=tf.keras.losses.SparseCategoricalCrossentropy(), optimizer=tf.keras.optimizers.Adam(learning_rate=0.001), metrics=["accuracy"])
    # --------------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------------
    tf_history = tf_model.fit(X_train,y_train, epochs=30)
    print('Generic Model training result:')
    loss, accuracy = tf_model.evaluate(X_test,y_test)
    print(f"Loss is {loss}, accuracy is {accuracy}")
    pd.DataFrame(tf_history.history).plot()
    plt.grid()
    plt.title('training history')
    if path is not None:
        tf_model.save(path+'generic_model_1')
    return tf_model

## Generic function for tensor flow generation model for multiclass classification (respect binary calssification loss function is CategoricalCrossenstropy)
def generic_tf_model_one_hot(X_train, X_test, y_train, y_test, path:str=None, seed: int=None) -> tf.keras.Model:
    """ A Generic function to create a valid model for Binary Classification
        - Input is the size of the numeber of information (size of the images)
        - Relu as activation functin for 2 Dense layer
        - Sigmoid as activation function for the last layer (output Layer)
        - Output layer is the number of category
        - SparseCatecoricalCrossentropy for Classification (output 1,2 3 ...)  while CatecoricalCrossentropy require hot_one vector[0, 0, 1, 0, 0]
        - Adam for optimization: optimal learning rate 0.01 - 0.001 (look to dinamic adapt the learning rate tf.keras.callbacks.LearningRateScheduler)
    """
    if seed is not None:
        tf.random.set_seed(seed) # to alway start with the same weights
    # --------------------------------------------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------- Model for Binary Classification
    # Try introducing non linearity in model using relu activation fuction: (number of layer and neuron can be increased)
    tf_model = tf.keras.Sequential([
        tf.keras.layers.Flatten(input_shape=(28,28)),
        tf.keras.layers.Dense(100, activation="relu"),      # typical activation function used is Relu
        tf.keras.layers.Dense(20, activation="relu"),
        tf.keras.layers.Dense(10, activation=tf.keras.activations.softmax)      # the output has to be softmax for 10 categry 
       
    ])
    # Accuracy can be used for classification, similarly to the type of loss function
    # metric could be:
    # - accuracy: default value for classification -> metrics=tf.keras.metrics.Accuracy()
    # - precision: less false positive -> metrics=tf.keras.metrics.Precision()
    # - recall: less false negative -> metrics=tf.keras.metrics.Recall()
    tf_model.compile(loss=tf.keras.losses.CategoricalCrossentropy(), optimizer=tf.keras.optimizers.Adam(learning_rate=0.001), metrics=["accuracy"])
    # --------------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------------
    tf_history = tf_model.fit(X_train,tf.one_hot(y_train, depth=10), epochs=30)
    print('Generic Model training result:')
    loss, accuracy = tf_model.evaluate(X_test,tf.one_hot(y_test, depth=10))
    print(f"Loss is {loss}, accuracy is {accuracy}")
    pd.DataFrame(tf_history.history).plot()
    plt.grid()
    plt.title('training history')
    if path is not None:
        tf_model.save(path+'hotone_model_2')
    return tf_model

# function to plot a list of data and labels randomly selected from the dataset
def plot_images(data, labels):
    import random
    plt.figure(figsize=(7, 7))
    for i in range(16):
        ax = plt.subplot(4, 4, i + 1)
        rand_index = random.choice(range(len(data)))
        plt.imshow(train_data[rand_index], cmap=plt.cm.binary)
        plt.title(class_names[labels[rand_index]])
        plt.axis(False)


#-------------------------------------------------------
# Start  Things
if __name__ == '__main__':
    print(f"TF version: {tf.__version__}")
    # define a path where save output
    path_where_save = getcwd()+'/../'
    print(f'the ouput will be saved on {path_where_save}')

    # Import the dataset for multi class classification
    (train_data, train_labels), (test_data, test_labels) = tf.keras.datasets.fashion_mnist.load_data()
    print(f"train data shape is {train_data[0].shape}")
    print(f"train labels shape is {train_labels[0].shape}")
    # Label: from 0 to 9
    # 0: is a T-shirt
    # 1: is a Trouser
    # ....
    # 9: is a Ankle boot

    class_names = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat', 'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']
    
    # need to transform the 28x28 images in flated data
    train_data_normalize = normalization(train_data)
    test_data_normalize = normalization(test_data)
    if already_saved_model is False:
        tf_model_1 = generic_tf_model(train_data_normalize, test_data_normalize, train_labels, test_labels, path_where_save, seed=42)
        tf_model_2 = generic_tf_model_one_hot(train_data_normalize, test_data_normalize, train_labels, test_labels, path_where_save, seed=42)
    else: 
        tf_model_1 = tf.keras.models.load_model(path_where_save+"generic_model_1")
        tf_model_2 = tf.keras.models.load_model(path_where_save+"hotone_model_2")
    
    # make some prediction with the model - remember to use the same type of data)
    y_predict = tf_model_1.predict(test_data_normalize)

    # Convert all of the predictions from probabilities to labels
    y_preds_index = y_predict.argmax(axis=1)

    # Create the confusion matrix
    custom_confusion_matrix(y_true=test_labels, 
                            y_preds=y_preds_index,
                            classes=class_names,
                            model_name="MODEL 1",
                            figsize=(15, 15),
                            text_size=10)
    

    # make some prediction with the model - remember to use the same type of data)
    y_predict = tf_model_2.predict(test_data_normalize)

    # Convert all of the predictions from probabilities to labels
    y_preds_index = y_predict.argmax(axis=1)

    # Create the confusion matrix
    custom_confusion_matrix(y_true=test_labels, 
                            y_preds=y_preds_index,
                            classes=class_names,
                            model_name="MODEL 2",
                            figsize=(15, 15),
                            text_size=10)
    

    # try 10 prediction selecting 10 images from the test_data_normalized
    for n in range(0, 10):
        plot_random_image(model=tf_model_2, 
                          images=test_data_normalize, 
                          true_labels=test_labels, 
                          classes=class_names)

    if show_figure is True:
        plt.show()

    