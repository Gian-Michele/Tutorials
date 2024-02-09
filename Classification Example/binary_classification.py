# Import required libraries
import tensorflow as tf
import pandas as pd
import numpy as np
from sklearn.datasets import make_circles
import matplotlib.pyplot as plt
from os import getcwd

show_figure = True

## Generic function for tensor flow generation model for binary classification
def generic_tf_model(X_train, X_test, y_train, y_test, seed: int=None) -> tf.keras.Model:
    """ A Generic function to create a valid model for Binary Classification
        - Relu as activation functin for 2 Dense layer
        - Sigmoid as activation function for the last layer (output Layer)
        - BinaryCrossentropy for Classification
        - Adam for optimization: optimal learning rate 0.01 - 0.001 (look to dinamic adapt the learning rate tf.keras.callbacks.LearningRateScheduler)
    """
    if seed is not None:
        tf.random.set_seed(seed) # to alway start with the same weights
    # --------------------------------------------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------- Model for Binary Classification
    # Try introducing non linearity in model using relu activation fuction: (number of layer and neuron can be increased)
    tf_model = tf.keras.Sequential([
        tf.keras.layers.Dense(100, activation="relu"),      # typical activation function used is Relu
        tf.keras.layers.Dense(10, activation="relu"),
        tf.keras.layers.Dense(1, activation="sigmoid")      # the output has to be sigmoid for binary classification
       
    ])
    # Accuracy can be used for classification, similarly to the type of loss function
    # metric could be:
    # - accuracy: default value for classification -> metrics=tf.keras.metrics.Accuracy()
    # - precision: less false positive -> metrics=tf.keras.metrics.Precision()
    # - recall: less false negative -> metrics=tf.keras.metrics.Recall()
    tf_model.compile(loss=tf.keras.losses.BinaryCrossentropy(), optimizer=tf.keras.optimizers.Adam(learning_rate=0.001), metrics=[tf.keras.metrics.Accuracy()])
    # --------------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------------
    tf_history = tf_model.fit(X_train,y_train, epochs=100, verbose=0)
    print('Generic Model training result:')
    loss, accuracy = tf_model.evaluate(X_test,y_test)
    print(f"Loss is {loss}, accuracy is {accuracy}")
    pd.DataFrame(tf_history.history).plot()
    plt.grid()
    plt.title('training history')
    return tf_model


# Questa funzione e' rilevante per capire il funzionamento del mio modello perche' mostra il boudary
# information can be found in https://cs231n.github.io/neural-networks-case-study/
def plot_decision_boundary(model :tf.keras.Model, X, y):
    """ To evalue the prediction of model exploing input and outpunt
    """
    # dimension of the plot
    x_min, x_max = X[:,0].min() - 0.1, X[:,0].max()
    y_min, y_max = X[:,1].min() - 0.1, X[:,1].max()

    # mesh grid of x e y value in 2D dimension
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 100), np.linspace(y_min, y_max, 100))

    x_in = np.c_[xx.ravel(), yy.ravel()] # put together the 2 array in a single input array similar to X

    y_predict = model.predict(x_in)

    if len(y_predict[0]) > 1:
        print("\nThis is a Multi Class Classification")
        # this is a multi class classification
        y_predict = np.argmax(y_predict, axis=1).reshape(xx.shape)
    else:
        # this is a binary classification
        print("\nThis is a Binary Class Classification")
        y_predict = np.round(y_predict).reshape(xx.shape)

    # plot the decision boundary
    plt.contourf(xx,yy,y_predict, cmap=plt.cm.RdYlBu, alpha=0.7)
    plt.scatter(X[:,0], X[:,1], c=y, cmap=plt.cm.RdYlBu)
    plt.xlim(xx.min(), xx.max())
    plt.ylim(yy.min(), yy.max())


def castom_confusion_matrix(y_test, y_preds):
    """ Provide a Confusion matrix starting from the y label original and y label predicted """
    # Note: The following confusion matrix code is a remix of Scikit-Learn's
    # plot_confusion_matrix function - https://scikit-learn.org/stable/modules/generated/sklearn.metrics.plot_confusion_matrix.html
    # and Made with ML's introductory notebook - https://github.com/GokuMohandas/MadeWithML/blob/main/notebooks/08_Neural_Networks.ipynb
    import itertools
    from sklearn.metrics import confusion_matrix

    figsize = (10, 10)

    # Create the confusion matrix ( y_preds has to be turn from proability to 0 and 1)
    cm = confusion_matrix(y_test, tf.round(y_preds))
    cm_norm = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis] # normalize it
    n_classes = cm.shape[0]

    # Let's prettify it
    fig, ax = plt.subplots(figsize=figsize)
    # Create a matrix plot
    cax = ax.matshow(cm, cmap=plt.cm.Blues) # https://matplotlib.org/3.2.0/api/_as_gen/matplotlib.axes.Axes.matshow.html
    fig.colorbar(cax)

    # Create classes
    classes = False

    if classes:
        labels = classes
    else:
        labels = np.arange(cm.shape[0])

    # Label the axes
    ax.set(title="Confusion Matrix",
        xlabel="Predicted label",
        ylabel="True label",
        xticks=np.arange(n_classes),
        yticks=np.arange(n_classes),
        xticklabels=labels,
        yticklabels=labels)

    # Set x-axis labels to bottom
    ax.xaxis.set_label_position("bottom")
    ax.xaxis.tick_bottom()

    # Adjust label size
    ax.xaxis.label.set_size(20)
    ax.yaxis.label.set_size(20)
    ax.title.set_size(20)

    # Set threshold for different colors
    threshold = (cm.max() + cm.min()) / 2.

    # Plot the text on each cell
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, f"{cm[i, j]} ({cm_norm[i, j]*100:.1f}%)",
            horizontalalignment="center",
            color="white" if cm[i, j] > threshold else "black",
            size=15)

#-------------------------------------------------------
# Start  Things
if __name__ == '__main__':
    print(f"TF version: {tf.__version__}")
    # define a path where save output
    path_where_save = getcwd()+'/../'
    print(f'the ouput will be saved on {path_where_save}')

    n_samples = 10000

    X, y = make_circles(n_samples=n_samples, noise=0.03, random_state=42)

    print(f'shape of input {X.shape}. Example of info: \n{X[:10]}')
    print(f'shape of input {y.shape}. Example of info: \n{y[:10]}')
    
    circles = pd.DataFrame({"X0":X[:,0], "X1": X[:,1], "label": y})

    print(f'DataFreme is: \n{circles}')

    X_train = X[:800]
    X_test = X[800:]
    y_train = y[:800]
    y_test = y[800:]

    # Bisogna definire la struttura degli input per le immagini settando le 2 dimensioni(244, 244,3) 3 e' per RGB i 3 colori porincipali
    # Loss function da musare nella classifica e' CategoricalCrossentropy
    # optimization Adam optimizer e' un buon ottimizatore (oppure SGD)

    tf.random.set_seed(42) # to alway start with the same weights

    model_1 = tf.keras.Sequential([
        tf.keras.layers.Dense(10),
        tf.keras.layers.Dense(1)
    ])
    # accuracy can be used for classification, similarly to the type of loss function
    model_1.compile(loss=tf.keras.losses.BinaryCrossentropy(), optimizer=tf.keras.optimizers.Adam(), metrics=["accuracy"])

    history = model_1.fit(X_train,y_train, epochs=100, verbose=0)
    
    print('Model 1 training result:')
    model_1.evaluate(X_test, y_test)  # if you use verbose=0 you can print the final result

    y_predict = model_1.predict(X_test)

    
    #function to generate the model
    model_2 = generic_tf_model(X_train, X_test, y_train, y_test, 42)
    
    # ----------------------------------------------------------------------------------   
    # Model 1 does not have a good accuracy even increasing the number of layer. It is important in this case print the predictions to observe what is happening
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.title("Model 1")
    # figure showing the decision boundary
    plot_decision_boundary(model_1, X=X_test, y=y_test)
    plt.subplot(1, 2, 2)
    plt.title("Model 2")
    # figure showing the decision boundary
    plot_decision_boundary(model_2, X=X_test, y=y_test)
    
    # ----------------------------------------------------------------------------------
    # Confusion Matric to evalue the accuracy of binary prediction
    # ----------------------------------------------------------------------------------
    from sklearn.metrics import confusion_matrix
    y_predict = model_2.predict(X_test)
    print(f"label y to find: {y[:5]}, predicted label y_predict: {y_predict[:5]}")
    castom_confusion_matrix(y_test, y_predict)

    if show_figure is True:
        plt.show()