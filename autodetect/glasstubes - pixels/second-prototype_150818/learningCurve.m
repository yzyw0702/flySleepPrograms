function [error_train, error_val, Theta1, Theta2] = ...
    learningCurve(dsTrain, dsValid, lambda)
%LEARNINGCURVE Generates the train and cross validation set errors needed 
%to plot a learning curve
%   [error_train, error_val] = ...
%       LEARNINGCURVE(X, y, Xval, yval, lambda) returns the train and
%       cross validation set errors for a learning curve. In particular, 
%       it returns two vectors of the same length - error_train and 
%       error_val. Then, error_train(i) contains the training error for
%       i examples (and similarly for error_val(i)).
%
%   In this function, you will compute the train and test errors for
%   dataset sizes from 1 up to m. In practice, when working with larger
%   datasets, you might want to do this in larger intervals.

% Number of training examples
m = size(dsTrain, 1);

% You need to return these values correctly
stepsize = 100;
error_train = zeros(m/stepsize, 1);
error_val   = zeros(m/stepsize, 1);
Theta1 = zeros(1,1);
Theta2 = zeros(1,1);

% ---------------------- Sample Solution ----------------------
for nT = 1:m/stepsize
	printf("sample/all = %d/%d point on learning curve:\n", nT*stepsize, m)
	[Theta1, Theta2, cost] = trainForwardNeuralNetwork(dsTrain(1:(nT*stepsize), :), lambda);
	% nnParams = [Theta1(:); Theta2(:)];
	error_train(nT) = computeCost(dsTrain(1:(nT*stepsize), :), Theta1, Theta2);
	error_val(nT) = computeCost(dsValid, Theta1, Theta2);
	
	% close all;
	m = size(dsTrain, 1);
	plot(1:size(error_train,1), error_train, 1:size(error_val,1), error_val, 'linestyle', '-');
	title(sprintf('FNN Learning Curve (lambda = %f)', lambda));
	xlabel('Number coefficient of training examples');
	ylabel('Error');
	legend('Train', 'Cross Validation');
	pause(1);
end
% -------------------------------------------------------------

% =========================================================================

end
