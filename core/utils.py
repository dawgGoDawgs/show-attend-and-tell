import numpy as np
#import cPickle as pickle
import six; from six.moves import cPickle as pickle
#import hickle
import h5py
import time
import os
from PIL import Image


def load_coco_data(data_path='./data', split='train'):
    data_path = os.path.join(data_path, split)
    start_t = time.time()
    data = {}
    
    print("begin loading pickled data.")
    with open(os.path.join(data_path, '%s.file.names.pkl' %split), 'rb') as f:
        data['file_names'] = pickle.load(f)   
        print("finished loading file names.")
    with open(os.path.join(data_path, '%s.captions.pkl' %split), 'rb') as f:
        data['captions'] = pickle.load(f)
        print("finished loading captions.")
    with open(os.path.join(data_path, '%s.image.idxs.pkl' %split), 'rb') as f:
        data['image_idxs'] = pickle.load(f)
        print("finished loading image indexes.")
            
    if split == 'train':       
        with open(os.path.join(data_path, 'word_to_idx.pkl'), 'rb') as f:
            data['word_to_idx'] = pickle.load(f)
            print("finished loading word to indexes.")
    
    # load the image features.
    # data['features'] = hickle.load(os.path.join(data_path, '%s.features.hkl' %split))
    h5f = h5py.File(os.path.join(data_path, '%s.features.h5' %split),'r')
    data['features'] = h5f['image_feature'][:]
    h5f.close()
    print("finished loading features.")
          
    for k, v in data.items():
        if type(v) == np.ndarray:
            print( k, type(v), v.shape, v.dtype)
        else:
            print( k, type(v), len(v))
    end_t = time.time()
    print( "Elapse time: %.2f" %(end_t - start_t) )
    return data

def decode_captions(captions, idx_to_word):
    if captions.ndim == 1:
        T = captions.shape[0]
        N = 1
    else:
        N, T = captions.shape

    decoded = []
    for i in range(N):
        words = []
        for t in range(T):
            if captions.ndim == 1:
                word = idx_to_word[captions[t]]
            else:
                word = idx_to_word[captions[i, t]]
            if word == '<END>':
                words.append('.')
                break
            if word != '<NULL>':
                words.append(word)
        decoded.append(' '.join(words))
    return decoded

def resize_image(image):
    width, height = image.size
    if width > height:
        left = (width - height) / 2
        right = width - left
        top = 0
        bottom = height
    else:
        top = (height - width) / 2
        bottom = height - top
        left = 0
        right = width
    image = image.crop((left, top, right, bottom))
    image = image.resize([224, 224], Image.ANTIALIAS)
    return image

def sample_coco_minibatch(data, batch_size):
    data_size = data['features'].shape[0]
    mask = np.random.choice(data_size, batch_size)
    features = data['features'][mask]
    file_names = data['file_names'][mask]
    return features, file_names

def write_bleu(scores, path, epoch):
    if epoch == 0:
        file_mode = 'w'
    else:
        file_mode = 'a'
    with open(os.path.join(path, 'val.bleu.scores.txt'), file_mode) as f:
        f.write('Epoch %d\n' %(epoch+1))
        f.write('Bleu_1: %f\n' %scores['Bleu_1'])
        f.write('Bleu_2: %f\n' %scores['Bleu_2'])
        f.write('Bleu_3: %f\n' %scores['Bleu_3'])  
        f.write('Bleu_4: %f\n' %scores['Bleu_4']) 
        f.write('METEOR: %f\n' %scores['METEOR'])  
        f.write('ROUGE_L: %f\n' %scores['ROUGE_L'])  
        f.write('CIDEr: %f\n\n' %scores['CIDEr'])

def load_pickle(path):
    with open(path, 'rb') as f:
        file = pickle.load(f)
        print('Loaded %s..' %path)
        return file  

def save_pickle(data, path):
    with open(path, 'wb') as f:
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
        print('Saved %s..' %path)
