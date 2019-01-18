function cost = computeCost(ds, Theta1, Theta2)
% compute properties
nInput = size(Theta1, 2) - 1;
nHidden = size(Theta1, 1);
nOutput = size(Theta2, 1);
% extract X and y components
X = ds(:, 1:(end-1));
X = normalizeFeature(X);  % normalize feature component
y = ds(:, end) + 1;
% compute cost with current unroll thetas and dataset
nnParams = [Theta1(:); Theta2(:)];
cost = nnCostFunction(nnParams, nInput, nHidden, nOutput, X, y, 0);
end
