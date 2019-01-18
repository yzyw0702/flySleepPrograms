function XNorm = normalizeFeature(X)
% normalize feature by XNorm = (X - Mu) ./ Sigma
% [X] is m x n matrix, m data point, n-dimention feature
% [return] XNorm is m x n matrix, all feature normalized

% compute Mean and Std for each feature
Mu = mean(X, 1);
Sigma = std(X, 1);

% normalize all column data
XNorm = bsxfun(@minus, X, Mu);
XNorm = bsxfun(@rdivide, XNorm, Sigma);

end
