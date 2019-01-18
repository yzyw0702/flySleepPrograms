XTest = dsTest(:, 1:(end-1));  % extract feature component
XTest = normalizeFeature(XTest);  % normalize feature component
yTest = dsTest(:, end) + 1;  % extract label component, y=1 means negative, y=2 means positive

pred = predict(Theta1, Theta2, XTest);
fprintf('\nTest Set Accuracy: %f\n', mean(double(pred == yTest)) * 100);
