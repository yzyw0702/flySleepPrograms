function dsReshuff = reshuffleDataset(dataset)
% reshuffle dataset along the row dimension
% [dataset] is m x (n+1) matrix
% [return] dsReshuff is m x (n+1) matrix, only its order is different

% read size
[m, r] = size(dataset);

% get order of reshuffling
sel = randperm(m);

% copy each line with order shown above
dsReshuff = dataset(sel, :);

end
