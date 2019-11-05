clc, clear

flow = readmatrix('flow.csv');
sensor = readmatrix('sensors.csv');

%%

sensor_1 = sensor(:, 2);
sensor_2 = sensor(:, 3);
sensor_3 = sensor(:, 4);
sensor_4 = sensor(:, 5);
sensor_5 = sensor(:, 6);
sensor_6 = sensor(:, 7);
sensor_7 = sensor(:, 8);
sensor_8 = sensor(:, 9);

flow_undersampled = resample(flow, length(sensor_1), length(flow));
flow_undersampled(:,1) = flow_undersampled(:,1)*-1;

x = linspace(0, 9989, 9989);

%%

figure
plot(x(10:6000), flow_undersampled(10:6000, 1), 'LineWidth', 1.5)

figure
plot(x(10:6000), sensor_1(10:6000), 'LineWidth', 1.5)

%%

csvwrite('flow_training.csv', flow_undersampled);

