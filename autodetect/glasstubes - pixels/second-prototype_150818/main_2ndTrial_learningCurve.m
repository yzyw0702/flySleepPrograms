clear; close all; clc

% Part-1 load dataset and read its properties
load('dataset_ori.mat');  % load original dataset
load('dataset_enh.mat');  %load derived dataset
ds = [dsOri; dsEnh];  % merge
[nData, nPix] = size(ds);  % read dataset size

% Part-2 preprocess dataset
dsReshuff = reshuffleDataset(ds);  % reshuffle data order
[dsTrain, dsValid, dsTest] = splitDataset(dsReshuff);  % allocate three data groups

% Part-3 draw learning curve at training phase
lambda = 1;
[error_train, error_valid, Theta1, Theta2] = learningCurve(dsTrain, dsValid, lambda);


% Part-4 save parameters
X = dsTrain(:, 1:(end-1));
y = dsTrain(:, end) + 1;
Mu = mean(X, 1);
Sigma = std(X, 1);
save parameters_2ndTrial.m
