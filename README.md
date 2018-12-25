# Speech Recognition

 🛠 __Work In Progress__ ❗️

Speech recognition implemented by using __Tensorflow__ for deep learning.
We are using __recurrent neural network__ with __LSTM__ nodes and in order to deal with sequencing problem we apply __CTC__(Connectionist Temporal Classification).

__MI-PYT TODO__:
- [ ] Code Refactor
- [ ] Improved sound preprocessing and feature extraction
- [ ] Training model based on Attention Mechanism
- [ ] Training model based on Neural Turing Machine
- [ ] Automated generation of datasets from audiobooks
- [ ] Documentation
- [ ] Tests


## Training data
In order to train our neural network we have to download training data.
I'm using __VCTK Corpus__ which will do the trick for my purpose. If you are aiming to lower error rates I strongly recommend using more training data.  
⚠️ VCTK Corpus - 15GB
```
# LINUX
wget http://homepages.inf.ed.ac.uk/jyamagis/release/VCTK-Corpus.tar.gz
# MAC
curl -O http://homepages.inf.ed.ac.uk/jyamagis/release/VCTK-Corpus.tar.gz
```

## Requirements
```
# TODO
```

## Run Training Phase
```
# TODO: MAGIC so far ❤️
```

### Tensorboard
For better monitoring and visualization of training phase run tensorboard command.
```
tensorboard --logdir ./tensorboard    
```
