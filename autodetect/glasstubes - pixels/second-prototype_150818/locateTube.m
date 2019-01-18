function [map] = locateTube(img, winSize, Theta1, Theta2, mu, sigma)
% step1: compute matrices size
[H W] = size(img);
h = winSize(1);
w = winSize(2);
map = zeros(H-h+1, W-w+1);
[hMap, wMap] = size(map);  % size of label map
m = hMap * wMap;  % number of all sliding windows

% step2: reshape each slide window into a row vector
X = zeros(m, h*w);
for i=1:m
	iW = mod(i, (h*w));
	iH = i / (h*w) + 1;
	
end

for iH=1:hMap
	for iW = 1:wMap
		
	end
end

end
