function [lambda_vec, error_train, error_valid] = validationCurve(dsTrain, dsValid)
% input parameters
lambda_vec = [0 0.2 1 2 10 20]';
nLambda = length(lambda_vec);
error_train = zeros(nLambda, 1);
error_valid = zeros(nLambda, 1);
Theta1 = zeros(1,1);
Theta2 = zeros(1,1);
cost = 0;

% lambda select loop
for i=1:nLambda
	lambda = lambda_vec(i);
	[Theta1, Theta2, cost] = trainForwardNeuralNetwork(dsTrain, lambda);
	error_train(i) = computeCost(dsTrain, Theta1, Theta2);
	error_valid(i) = computeCost(dsValid, Theta1, Theta2);
end

end
