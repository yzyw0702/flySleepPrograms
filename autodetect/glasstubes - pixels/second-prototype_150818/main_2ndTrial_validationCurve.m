clear; close all; clc

% Part-1 load dataset and read its properties
load('dataset_ori.mat');  % load original dataset
load('dataset_enh.mat');  %load derived dataset
ds = [dsOri; dsEnh];  % merge
[nData, nPix] = size(ds);  % read dataset size

% Part-2 preprocess dataset
dsReshuff = reshuffleDataset(ds);  % reshuffle data order
[dsTrain, dsValid, dsTest] = splitDataset(dsReshuff);  % allocate three data groups

% Part-3 draw validation curve at training phase
[lambda_vec, error_train, error_valid] = validationCurve(dsTrain, dsValid);
close all;
plot(lambda_vec, error_train, lambda_vec, error_valid);
legend('Train', 'Cross Validation');
xlabel('lambda');
ylabel('Error');

fprintf('lambda\t\tTrain Error\tValidation Error\n');
for i = 1:length(lambda_vec)
	fprintf(' %f\t%f\t%f\n', ...
            lambda_vec(i), error_train(i), error_valid(i));
end
