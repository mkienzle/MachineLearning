import numpy
import tensorflow as tf
from tensorflow import keras
import argparse
import cv2
import glob
import pandas
import re

parser = argparse.ArgumentParser(description='Count features.')
parser.add_argument('--seed', type=int, default=13435, 
                    help='Random seed')
parser.add_argument('--trainDir', default='../../Data/Synthetic/Dots/train',
                    help='Path to the training data directory')
parser.add_argument('--testDir', default='../../Data/Synthetic/Dots/test',
                    help='Path to the testing data directory')
parser.add_argument('--save', default='',
                    help='Turn plot in file')

args = parser.parse_args()


numpy.random.seed(args.seed)


def loadImages(filenames):
    """
    Load image files as grey data arrays
    @param filenames list of file images
    @return array of grey pixel data (1=white, 0=black)
    """
    # open first file to get the image size
    im = cv2.imread(filenames[0])
    n0, n1 = im.shape[:2]
    numImages = len(filenames)
    inputData = numpy.zeros((numImages, n0, n1, 1), numpy.float32)
    for fn in filenames:
        # extract the index from the file name, note: the index starts with 1
        im = cv2.imread(fn)
        index = int(re.search('img(\d+)\.', fn).group(1)) - 1
        inputData[index,...] = im.mean(axis=2).reshape(n0, n1, 1) / 255.
    return inputData

def getImageSizes(filenames):
    """
    Get the number of x and y pixels
    @parameter filenames file names
    @return nx, ny
    """
    im = cv2.imread(filenames[0])
    return im.shape[:2]


trainingDir = args.trainDir

df = pandas.read_csv(trainingDir + '/train.csv')
categories = df['numberOfFeatures'].unique()
categories.sort()
minNumFeatures = min(categories)
maxNumFeatures = max(categories)

# labels start at zero
trainingOutput = numpy.array(df['numberOfFeatures'], numpy.int8) - minNumFeatures
filenames = glob.glob(trainingDir + '/img*.???')
trainingInput = loadImages(filenames)
n0, n1 = getImageSizes(filenames)

testingDir = args.testDir
df = pandas.read_csv(testingDir + '/test.csv')
numCategories = len(categories)
# labels start at zero
testingOutput = numpy.array(df['numberOfFeatures'], numpy.int8) - minNumFeatures
testingInput = loadImages(glob.glob(testingDir + '/img*.???'))

# train the model
print('Number of training images: {}'.format(trainingInput.shape[0]))
print('Number of testing images : {}'.format(testingInput.shape[0]))
print('Image size               : {} x {}'.format(n0, n1))
print('Categories               : {} min/max = {}/{}'.format(categories, minNumFeatures, maxNumFeatures))


clf = keras.Sequential()

clf.add( keras.layers.Conv2D(64, kernel_size=(3,3), strides=(1,1),
                             padding='same', data_format='channels_last', activation='relu') )
clf.add( keras.layers.MaxPooling2D(pool_size=(2, 2)) )

clf.add( keras.layers.Conv2D(128, kernel_size=(3,3), strides=(1,1),
                             padding='same', data_format='channels_last', activation='relu') )
clf.add( keras.layers.MaxPooling2D(pool_size=(2, 2)) )

clf.add( keras.layers.Conv2D(256, kernel_size=(3,3), strides=(1,1),
                             padding='same', data_format='channels_last', activation='relu') )
clf.add( keras.layers.MaxPooling2D(pool_size=(2, 2)) )

clf.add( keras.layers.Flatten() )
clf.add( keras.layers.Dense(numCategories, activation='softmax') )

#clf.add( keras.layers.Activation('softmax') )

clf.compile(optimizer='adam',
            loss='sparse_categorical_crossentropy', 
            metrics=['accuracy'])

# now train
clf.fit(trainingInput, trainingOutput, epochs=40)

print(clf.summary())

# test
predictions = clf.predict(testingInput)
numPredictions = predictions.shape[0]
bestInds = numpy.argmax(predictions, axis=1)

print('bestInds = ', bestInds)
predictedNumFeatures = bestInds + minNumFeatures
print('predictedNumFeatures = ', predictedNumFeatures)
exactNumFeatures = testingOutput + minNumFeatures
print('exact num Features = ', exactNumFeatures)

# compute varError
diffs = (numpy.round(predictedNumFeatures) - exactNumFeatures)**2
varError = diffs.sum()
numFailures = (diffs != 0).sum()

print('variance of error = {} number of failures = {} ({} %)'.format(varError, numFailures, 
      100*float(numFailures) / float(exactNumFeatures.size)))

print('known number of features for the first 5 images   : {}'.format(exactNumFeatures[:5]))
print('inferred number of features for the first 5 images: {}'.format(predictedNumFeatures[:5]))

# plot training/test dataset
import matplotlib
if args.save:
    # does not require X
    matplotlib.use('Agg')
from matplotlib import pylab
n = 50
for i in range(n):
    pylab.subplot(n//10, 10, i + 1)
    pylab.imshow(testingInput[i,...].mean(axis=2))
    titleColor = 'black'
    if int(exactNumFeatures[i]) != numpy.round(predictedNumFeatures[i]):
        titleColor = 'red'
    pylab.title('{} ({})'.format(int(exactNumFeatures[i]), predictedNumFeatures[i]),
        fontsize=8, color=titleColor)
    pylab.axis('off')
if not args.save:
    pylab.show()
else:
    pylab.savefig(args.save, dpi=300)
