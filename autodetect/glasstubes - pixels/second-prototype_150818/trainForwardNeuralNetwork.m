function [Theta1, Theta2, cost] = trainForwardNeuralNetwork(dsTrain, lambda)
% train a 2-layer FNN
% [dsTrain] m x (n+1) matrix, with the last column as labeling;
% it will initially be normalized and split into feature and
% label components
% [return] thetas are the weights of all logistic neurons, layer1
% is n x 1, and layer2 is n/40 x 1, and output is 2 x 1

% read size
[m r] = size(dsTrain);  % get data size
n = r-1;  % get feature size

% extract components
X = dsTrain(:, 1:(end-1));  % extract feature component
X = normalizeFeature(X);  % normalize feature component
y = dsTrain(:, end) + 1;  % extract label component, y=1 means negative, y=2 means positive

% initialize theta
nInput = n;  % size of input layer (no bias unit)
nHidden = n/20;  % size of hidden layer (no bias unit)
nOutput = 2;  % size of output layer
initial_Theta1 = initializeTheta(nInput, nHidden);  % n/40 x (n+1)
initial_Theta2 = initializeTheta(nHidden, nOutput);  % 3 x (n/40 + 1)
initial_nnParams = [initial_Theta1(:); initial_Theta2(:)];  % unroll thetas

% set training parameters
options = optimset('MaxIter', 50);  % iteration rules

% Create "lambda-expression" of the cost function to be minimized
costFunction = @(p) nnCostFunction(p, nInput, nHidden, nOutput, X, y, lambda);

% start training iteration
[nnParams, cost] = fmincg(costFunction, initial_nnParams, options);

% extract theta back from nnParams
Theta1 = reshape(nnParams(1:nHidden * (nInput + 1)), ...
                 nHidden, (nInput + 1));

Theta2 = reshape(nnParams((1 + (nHidden * (nInput + 1))):end), ...
                 nOutput, (nHidden + 1));

% evaluate training accuracy
pred = predict(Theta1, Theta2, X);
