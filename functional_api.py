import tensorflow as tf
from tensorflow import keras
from keras import layers
import wget
print(f"TensorFlow version: {tf.__version__}")
# Import helper functions we're going to use
from extras.helper_functions import create_tensorboard_callback, plot_loss_curves, unzip_data, walk_through_dir
import matplotlib.pyplot as plt

save_model = True
regen_model0 = True
regen_model1 = True
download_data = False

# Get 10% of the data of the 10 
if download_data is True:
    wget.download("https://storage.googleapis.com/ztm_tf_course/food_vision/10_food_classes_10_percent.zip")
    unzip_data("10_food_classes_10_percent.zip")
# Walk through 10 percent data directory and list number of files
walk_through_dir("10_food_classes_10_percent")
# Create training and test directories
train_dir = "10_food_classes_10_percent/train/"
test_dir = "10_food_classes_10_percent/test/"

IMG_SIZE = (224, 224) # define image size
train_data_10_percent = tf.keras.preprocessing.image_dataset_from_directory(directory=train_dir,
                                                                            image_size=IMG_SIZE,
                                                                            label_mode="categorical", # what type are the labels?
                                                                            batch_size=32) # batch_size is 32 by default, this is generally a good number
test_data_10_percent = tf.keras.preprocessing.image_dataset_from_directory(directory=test_dir,
                                                                           image_size=IMG_SIZE,
                                                                           label_mode="categorical")

# 1. Create base model with "https://www.tensorflow.org/api_docs/python/tf/keras/applications"
# https://www.tensorflow.org/api_docs/python/tf/keras/applications/EfficientNetB0
base_model = tf.keras.applications.efficientnet_v2.EfficientNetV2B0(include_top=False)

# OLD
# base_model = tf.keras.applications.EfficientNetB0(include_top=False)

# 2. Freeze the base model (so the pre-learned patterns remain)
base_model.trainable = False
####################################################################################
## Below the sequence of creation, compile and fit a model using Functional API
if regen_model0 is True:
 
    # 3. Create inputs into the base model
    inputs = tf.keras.layers.Input(shape=(224, 224, 3), name="input_layer")

    # 4. If using ResNet50V2, add this to speed up convergence, remove for EfficientNetV2 because rescale in is already in the model)
    # x = tf.keras.layers.experimental.preprocessing.Rescaling(1./255)(inputs)

    # 5. Pass the inputs to the base_model (note: using tf.keras.applications, EfficientNetV2 inputs don't have to be normalized)
    x = base_model(inputs)
    # Check data shape after passing it to base_model
    print(f"Shape after base_model: {x.shape}")
    # x is a "feature vector", this means a learned representation of the input data

    # 6. Average pool the outputs of the base model (aggregate all the most important information, reduce number of computations)
    # see https://stackoverflow.com/questions/49295311/what-is-the-difference-between-flatten-and-globalaveragepooling2d-in-keras
    # https://saturncloud.io/blog/understanding-the-difference-between-flatten-and-globalaveragepooling2d-in-keras/
    x = tf.keras.layers.GlobalAveragePooling2D(name="global_average_pooling_layer")(x)
    print(f"After GlobalAveragePooling2D(): {x.shape}")

    # 7. Create the output activation layer
    outputs = tf.keras.layers.Dense(10, activation="softmax", name="output_layer")(x)

    # 8. Combine the inputs with the outputs into a model
    model_0 = tf.keras.Model(inputs, outputs)

    ########################################################################
    # Step 9 and 10 are the same of traditional model creation
    # 9. Compile the model
    model_0.compile(loss='categorical_crossentropy',
                optimizer=tf.keras.optimizers.Adam(),
                metrics=["accuracy"])

    # Setup checkpoint path
    checkpoint_path = "ten_percent_model0_checkpoints_weights/checkpoint.ckpt" # note: remember saving directly to Colab is temporary

    # Create a ModelCheckpoint callback that saves the model's weights only
    checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_path,
                                                            save_weights_only=True, # set to False to save the entire model
                                                            save_best_only=True, # save only the best model weights instead of a model every epoch
                                                            save_freq="epoch", # save every epoch
                                                            verbose=1)
    
    # 10. Fit the model (we use less steps for validation so it's faster)
    history_10_percent = model_0.fit(train_data_10_percent,
                                    epochs=5,
                                    steps_per_epoch=len(train_data_10_percent),
                                    validation_data=test_data_10_percent,
                                    # Go through less of the validation data so epochs are faster (we want faster experiments!)
                                    validation_steps=int(0.25 * len(test_data_10_percent)),
                                    # Track our model's training logs for visualization later
                                    callbacks=[create_tensorboard_callback("transfer_learning", "10_percent_feature_extract"), checkpoint_callback]
                                    )
    

    # Check out our model's training curves
    plot_loss_curves(history_10_percent)

    if save_model is True:
            # the new model name
            model_0.save("model_0")
else:
    # load the model name: model_0
    model_0 = tf.keras.models.load_model("model_0")
    print('model_0 loaded')


####################################################################################
## Below the sequence of creation, compile and fit a model using Functional API
if regen_model1 is True:
    # 1. Create base model with "https://www.tensorflow.org/api_docs/python/tf/keras/applications"
    # https://www.tensorflow.org/api_docs/python/tf/keras/applications/EfficientNetB0
    #base_model = tf.keras.applications.efficientnet_v2.EfficientNetV2B0(include_top=False)

    # OLD
    # base_model = tf.keras.applications.EfficientNetB0(include_top=False)

    # 2. Freeze the base model (so the pre-learned patterns remain)
    #base_model.trainable = False


    # NEW: Newer versions of TensorFlow (2.10+) can use the tensorflow.keras.layers API directly for data augmentation
    data_augmentation = keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.2),
    layers.RandomZoom(0.2),
    layers.RandomHeight(0.2),
    layers.RandomWidth(0.2),
    # preprocessing.Rescaling(1./255) # keep for ResNet50V2, remove for EfficientNet
    ], name ="data_augmentation")


    # 3. Create inputs into the base model
    inputs = tf.keras.layers.Input(shape=(224, 224, 3), name="input_layer")
    x = data_augmentation(inputs)

    # 4. If using ResNet50V2, add this to speed up convergence, remove for EfficientNetV2 because rescale in is already in the model)
    # x = tf.keras.layers.experimental.preprocessing.Rescaling(1./255)(inputs)

    # 5. Pass the inputs to the base_model (note: using tf.keras.applications, EfficientNetV2 inputs don't have to be normalized)
    x = base_model(x)
    # Check data shape after passing it to base_model
    print(f"Shape after base_model: {x.shape}")
    # x is a "feature vector", this means a learned representation of the input data

    # 6. Average pool the outputs of the base model (aggregate all the most important information, reduce number of computations)
    # see https://stackoverflow.com/questions/49295311/what-is-the-difference-between-flatten-and-globalaveragepooling2d-in-keras
    # https://saturncloud.io/blog/understanding-the-difference-between-flatten-and-globalaveragepooling2d-in-keras/
    x = tf.keras.layers.GlobalAveragePooling2D(name="global_average_pooling_layer")(x)
    print(f"After GlobalAveragePooling2D(): {x.shape}")

    # 7. Create the output activation layer
    outputs = tf.keras.layers.Dense(10, activation="softmax", name="output_layer")(x)

    # 8. Combine the inputs with the outputs into a model
    model_1 = tf.keras.Model(inputs, outputs)

    ########################################################################
    # Step 9 and 10 are the same of traditional model creation
    # 9. Compile the model
    model_1.compile(loss='categorical_crossentropy',
                optimizer=tf.keras.optimizers.Adam(),
                metrics=["accuracy"])

    # Setup checkpoint path
    checkpoint_path = "ten_percent_model1_checkpoints_weights/checkpoint.ckpt" # note: remember saving directly to Colab is temporary

    # Create a ModelCheckpoint callback that saves the model's weights only
    checkpoint_callback_1 = tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_path,
                                                            save_weights_only=True, # set to False to save the entire model
                                                            save_best_only=True, # save only the best model weights instead of a model every epoch
                                                            save_freq="epoch", # save every epoch
                                                            verbose=1)
    
    # 10. Fit the model (we use less steps for validation so it's faster)
    history_10_percent = model_1.fit(train_data_10_percent,
                                    epochs=5,
                                    steps_per_epoch=len(train_data_10_percent),
                                    validation_data=test_data_10_percent,
                                    # Go through less of the validation data so epochs are faster (we want faster experiments!)
                                    validation_steps=int(0.25 * len(test_data_10_percent)),
                                    # Track our model's training logs for visualization later
                                    callbacks=[create_tensorboard_callback("transfer_learning", "10_percent_feature_extract"), checkpoint_callback_1]
                                    )
    

    # Check out our model's training curves
    plot_loss_curves(history_10_percent)

    if save_model is True:
            # the new model name
            model_0.save("model_1")
else:
    # load the model name: model_1
    model_1= tf.keras.models.load_model("model_1")
    print('model_1 loaded')

print('Evaluation of model 0')
model_0.evaluate(test_data_10_percent)

print('Evaluation of model 1')
model_1.evaluate(test_data_10_percent)

plt.show()