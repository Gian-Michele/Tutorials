# Import required libraries
import tensorflow as tf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from os import getcwd

show_figure = True


## Generic function for tensor flow generation model for multiclass classification (respect binary calssification loss function is CategoricalCrossenstropy)
def generic_tf_model(X_train, X_test, y_train, y_test, seed: int=None) -> tf.keras.Model:
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
        tf.keras.layers.Dense(4, activation="relu"),      # typical activation function used is Relu
        tf.keras.layers.Dense(4, activation="relu"),
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
    tf_history = tf_model.fit(X_train,y_train, epochs=10)
    print('Generic Model training result:')
    loss, accuracy = tf_model.evaluate(X_test,y_test)
    print(f"Loss is {loss}, accuracy is {accuracy}")
    pd.DataFrame(tf_history.history).plot()
    plt.grid()
    plt.title('training history')
    return tf_model

## Generic function for tensor flow generation model for multiclass classification (respect binary calssification loss function is CategoricalCrossenstropy)
def generic_tf_model_one_hot(X_train, X_test, y_train, y_test, seed: int=None) -> tf.keras.Model:
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
        tf.keras.layers.Dense(4, activation="relu"),      # typical activation function used is Relu
        tf.keras.layers.Dense(4, activation="relu"),
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
    tf_history = tf_model.fit(X_train,tf.one_hot(y_train, depth=10), epochs=10)
    print('Generic Model training result:')
    loss, accuracy = tf_model.evaluate(X_test,tf.one_hot(y_train, depth=10))
    print(f"Loss is {loss}, accuracy is {accuracy}")
    pd.DataFrame(tf_history.history).plot()
    plt.grid()
    plt.title('training history')
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
    # tf_model_1 = generic_tf_model(train_data, test_data, train_labels, test_labels, 42)
    tf_model_2 = generic_tf_model_one_hot(train_data, test_data, train_labels, test_labels, 42)
    if show_figure is True:
        plt.show()

    