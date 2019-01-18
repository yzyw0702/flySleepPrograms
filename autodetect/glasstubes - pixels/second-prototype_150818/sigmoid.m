function g = sigmoid(z)
% sigmoid / logistic function
% g(i) = 1 / (1 + exp(-z(i)))

g = 1.0 ./ (1.0 + exp(-z));

end
