# This file contains the base class for a Lasagne model
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.initializers import HeNormal
from tensorflow.keras import layers
from encode_fits import load_fits_data
import random
import matplotlib.pyplot as plt

ACTIVATION = 'elu'
COMPRESSION = 4
EPOCHS = 60
BATCH_SIZE = 16
KNOWN_SAMPLE_SIZE = 100000
UNKNOWN_SAMPLE_SIZE = 1000000
TEST_SAMPLE_SIZE = 20
TRAIN_DATA_DIR = "files/debug_data/test/"
PLOT_SAVE_DIRECTORY = "files/model_stats/"
VALIDATION_SPLIT = 0.2

def pre_resnet_block(input, n_filters_in, n_filters_out, preactivated = False, downsampling = False):
    he_norm = HeNormal()
    n_filters =  n_filters_in
    increase_dim = n_filters_out != n_filters

    # Convolution branch
    # Pass through 1x1 filter
    stride = (2,2) if downsampling else (1,1)
    if preactivated:
        net_in = input
    else:
        net_in = layers.Activation(ACTIVATION)(layers.BatchNormalization()(input))
        

    net = layers.BatchNormalization()(layers.Conv2D(n_filters_in, 1, 
        padding="same",
        strides=stride,
        activation=ACTIVATION,
        kernel_initializer=he_norm
        )(net_in))

    # Pass through 3x3 filter
    net = layers.BatchNormalization()(layers.Conv2D(n_filters_in, 3, 
        padding="same",
        activation=ACTIVATION,
        kernel_initializer=he_norm
        )(net))

    # Pass through 1x1 filter
    net = layers.BatchNormalization()(layers.Conv2D(n_filters_in, 1,
        padding="same",
        activation=ACTIVATION,
        kernel_initializer=he_norm
        )(net))

    # Shortcut branch
    if downsampling or increase_dim:
        stride = 2 if downsampling else 1
        shortcut = layers.Conv2D(n_filters_in, 1,
            strides=stride,
            activation=ACTIVATION,
            kernel_initializer=he_norm
            )(net_in)
    else:
        shortcut = input

    # Merging branches
    output = layers.Add()([net, shortcut])
    return output

def prepare_resnet_model(image_size):
    input_layer = layers.Input(shape=(image_size,image_size,3), name="Image Input")

    net = layers.BatchNormalization()(layers.Conv2D(32, 7, padding='same', activation='relu')(input_layer))

    net = pre_resnet_block(net, n_filters_in=16, n_filters_out=32, preactivated=True)
    net = pre_resnet_block(net, n_filters_in=16, n_filters_out=32)
    net = pre_resnet_block(net, n_filters_in=16, n_filters_out=32)

    # First Resnet block
    net = pre_resnet_block(net, n_filters_in=32, n_filters_out=64, downsampling=True)
    net = pre_resnet_block(net, n_filters_in=32, n_filters_out=64)
    net = pre_resnet_block(net, n_filters_in=32, n_filters_out=64)

    # Second Resnet block
    net = pre_resnet_block(net, n_filters_in=64, n_filters_out=128, downsampling=True)
    net = pre_resnet_block(net, n_filters_in=64, n_filters_out=128)
    net = pre_resnet_block(net, n_filters_in=64, n_filters_out=128)

    # Third Resnet block
    net = pre_resnet_block(net, n_filters_in=128, n_filters_out=256, downsampling=True)
    net = pre_resnet_block(net, n_filters_in=128, n_filters_out=256)
    net = pre_resnet_block(net, n_filters_in=128, n_filters_out=256)

    #
    net = pre_resnet_block(net, n_filters_in=256, n_filters_out=512, downsampling=True)
    net = pre_resnet_block(net, n_filters_in=256, n_filters_out=512)
    net = pre_resnet_block(net, n_filters_in=256, n_filters_out=512)

    # output_layer = layers.Average()(net)
    pooled_layer = layers.AvgPool2D(pool_size=(image_size/16,image_size/16))(net)

    output_layer = layers.Dense(1, activation="sigmoid")(layers.Flatten()(pooled_layer))

    model = Model(input_layer, output_layer)
    model.summary()

    model.compile(loss=tf.keras.losses.BinaryCrossentropy(from_logits=False),
                    optimizer=tf.keras.optimizers.SGD(0.001),
                    metrics=["accuracy"])
    return model

if __name__ == "__main__":
    model = prepare_resnet_model(64)

    fits_data, expected_results = load_fits_data(TRAIN_DATA_DIR, KNOWN_SAMPLE_SIZE, UNKNOWN_SAMPLE_SIZE)
    record_count = expected_results.shape[0]

    print(f"Found {record_count} total values for training data.")

    history = model.fit(fits_data, expected_results, 
        epochs=EPOCHS, 
        batch_size=BATCH_SIZE,
        validation_split=VALIDATION_SPLIT)

    # Test examples
    for i in random.sample(range(record_count), TEST_SAMPLE_SIZE):
        print(f"Expected {expected_results[i]}, got {model(np.array([fits_data[i]]))[0,0]}")

    # Create Loss plot
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('Model Loss')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Validation'], loc='upper left')
    plt.savefig(PLOT_SAVE_DIRECTORY + "loss.png")
    plt.clf()
    
    # Create Accuracy plot
    plt.plot(history.history['accuracy'])
    plt.plot(history.history['val_accuracy'])
    plt.title('Model Accuracy')
    plt.ylabel('Accuracy')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Validation'], loc='upper left')
    plt.savefig(PLOT_SAVE_DIRECTORY + "accuracy.png")


