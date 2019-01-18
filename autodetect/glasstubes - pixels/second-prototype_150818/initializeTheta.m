function theta = initializeTheta(nIn, nOut)
% randomly initialize theta and ensure breaking the symmetry
% [nIn] is input number, [nOut] is output number
% [return] theta is randomly initialized

% return theta in the following dimension
theta = size(nOut, 1 + nIn);  % add the bias unit

% random initialization
epsilon_init = 0.12;  % sqrt(6) / sqrt(L_in + L_out)
theta = rand(nOut, nIn + 1) * epsilon_init * 2 - epsilon_init;  % [-e, +e]

end
