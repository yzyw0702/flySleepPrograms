function [dsTrain, dsValid, dsTest] = splitDataset(ds)
% split dataset into three groups
% [ds] original dataset, m x (n+1) matrix, with last column as labeling
% [return] three different data groups

% read dataset size
[nData, nFeature] = size(ds);

% allocate three data groups
nTrain = round(0.6 * nData);  % size of training dataset
nValid = round(0.2 * nData);  % size of cross-validation dataset
% nTest = nData - nTrain - nValid;  % size of test dataset

% split dataset into three groups
dsTrain = ds(1:nTrain, :);  % training data
dsValid = ds((nTrain+1):(nTrain+nValid), :);  % cross-validation data
dsTest = ds((nTrain+nValid+1):end, :);  % test data

end
