import argparse
from api.resnet_model import prepare_resnet_model
from api.encode_fits import load_fits_data
import random
import numpy as np
import matplotlib.pyplot as plt
import time

parser = argparse.ArgumentParser(description='Process some integers.')

parser.add_argument('data_directory', type=str,
                    help='directory of the training data')
parser.add_argument('save_directory', type=str,
                    help='directory to save the plots and trained model from the data')
parser.add_argument('-batch_size', type=int, default=128,
                    help='batch size for the training')
parser.add_argument('-epochs', type=int, default=120,
                    help='number of epochs to train for')
parser.add_argument('-test_samples', type=int, default=100,
                    help='number of test samples')
parser.add_argument('-validation_split', type=int, default=0.2,
                    help='split as a percentage of the data to be split into the validation set')
parser.add_argument('-image_size', type=int, default=1,
                    help='the size to input into the model')
parser.add_argument('-threads', type=int, default=4,
                    help='number of threads to use when loading in the training data')

args = parser.parse_args()

START_SIZE = 256
PLOT_SAVE_DIRECTORY = args.save_directory
TRAIN_DATA_DIR = args.data_directory
EPOCHS = args.epochs
BATCH_SIZE = args.batch_size
VALIDATION_SPLIT = args.validation_split
TEST_SAMPLE_SIZE = args.test_sample_size
IMAGE_SIZE = args.image_size
THREADS = args.threads

model = prepare_resnet_model(IMAGE_SIZE)

print(f"Loading test data from {TRAIN_DATA_DIR}")

fits_data, expected_results = load_fits_data(TRAIN_DATA_DIR, THREADS, IMAGE_SIZE)
record_count = expected_results.shape[0]

print(f"Found {record_count} total values for training data.")

print(f"Starting model training...")
history = model.fit(fits_data, expected_results, 
    epochs=EPOCHS, 
    batch_size=BATCH_SIZE,
    validation_split=VALIDATION_SPLIT)

now = int(time.time())

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
plt.savefig(f"{PLOT_SAVE_DIRECTORY}{now}_loss.png")
plt.clf()

# Create Accuracy plot
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Model Accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train', 'Validation'], loc='upper left')
plt.savefig(f"{PLOT_SAVE_DIRECTORY}{now}_accuracy.png")