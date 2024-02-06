import os
import numpy as np
from numpy.linalg import norm
from tqdm import tqdm
import os
import PIL
import time
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
import math
from sklearn.neighbors import NearestNeighbors
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from sklearn.decomposition import PCA

UPLOADS_DIR = '/home/everythinginssu/Path-to-Pet-Server/data'
# UPLOADS_DIR = '/Users/ggona/Documents/GitHub/Google Solution Challenge 2023/Path-to-Pet-Server/data'
GCS_BUCKET_NAME = 'path_to_pet_bucket'

def search_similar_images(gcs_url, is_dog):
    destination_blob_name = gcs_url.split(f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/")[1]

    img_path = os.path.join(UPLOADS_DIR, destination_blob_name)

    img_size =224

    # 검색 이미지 저장
    model = ResNet50(weights='imagenet', include_top=False,input_shape=(img_size, img_size, 3),pooling='max')

    batch_size = 256

    if is_dog:
        root_dir = '/home/everythinginssu/Path-to-Pet-Server/data/dog'
    else:
        root_dir = '/home/everythinginssu/Path-to-Pet-Server/data/cat'
    print(root_dir)
    img_gen = ImageDataGenerator(preprocessing_function=preprocess_input)

    datagen = img_gen.flow_from_directory(root_dir,
                                            target_size=(img_size, img_size),
                                            batch_size=batch_size,
                                            class_mode=None,
                                            shuffle=False)

    num_images = len(datagen.filenames)
    num_epochs = int(math.ceil(num_images / batch_size))

    print("Num images   = ", len(datagen.classes))

    feature_list = model.predict_generator(datagen, num_epochs,verbose = 1)

    print("Shape of feature_list = ", feature_list.shape)

    neighbors = NearestNeighbors(n_neighbors=5,
                                 algorithm='ball_tree',
                                 metric='euclidean')
    neighbors.fit(feature_list)

    # Get full path for all the images in our dataset

    filenames = [root_dir + '/' + s for s in datagen.filenames]
    # print(filenames) file 이름 절대경로 출력

    pca = PCA(n_components=100)
    pca.fit(feature_list)
    compressed_features = pca.transform(feature_list)

    neighbors_pca_features = NearestNeighbors(n_neighbors=5,
                                 algorithm='ball_tree',
                                 metric='euclidean').fit(compressed_features)

    # 검색 이미지 경로
    input_shape = (img_size, img_size, 3)
    img = image.load_img(img_path, target_size=(input_shape[0], input_shape[1]))
    img_array = image.img_to_array(img)
    expanded_img_array = np.expand_dims(img_array, axis=0)
    preprocessed_img = preprocess_input(expanded_img_array)

    test_img_features = model.predict(preprocessed_img, batch_size=1)

    _, indices = neighbors.kneighbors(test_img_features)

    test_img_compressed = pca.transform(test_img_features)
    distances, indices = neighbors_pca_features.kneighbors(test_img_compressed)
    print(indices.shape)
    plt.imshow(mpimg.imread(img_path), interpolation='lanczos')
    plt.xlabel(img_path.split('.')[0] + '_Original Image',fontsize=20)
    plt.show()
    print('********* Predictions  after PCA ***********')
    # similar_images(indices[0])

    result = []
    for index in indices[0]:
        similarity_score = cosine_similarity_pca(test_img_features.flatten(), feature_list[index])
        last_two_elements = '/'.join(filenames[index].split('/')[5:])
        result.append((last_two_elements, f"{similarity_score:.2}"))
        print(f"유사 이미지: {filenames[index]}, similarity score: {similarity_score:.2%}")

    # 검색 이미지 삭제
    return result

def similar_images(indices):
    plt.figure(figsize=(15,10), facecolor='white')
    plotnumber = 1
    for index in indices:
        if plotnumber<=len(indices):
            ax = plt.subplot(2,4,plotnumber)
            plt.imshow(mpimg.imread(filenames[index]), interpolation='lanczos')
            plotnumber+=1
    plt.tight_layout()

def cosine_similarity_pca(vector1, vector2):
    dot_product = np.dot(vector1, vector2)
    norm1 = np.linalg.norm(vector1)
    norm2 = np.linalg.norm(vector2)
    similarity = dot_product / (norm1 * norm2)
    return similarity
