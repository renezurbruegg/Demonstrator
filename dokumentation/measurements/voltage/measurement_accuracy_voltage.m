files = [
    % file name                 % appliled voltage
    "meas_VM1_0.999984_V.csv",  0.999984;
    "meas_VM1_1.999983_V.csv",  1.999983;
    "meas_VM1_2.99998_V.csv",   2.99998;
    "meas_VM1_4.00001_V.csv",   4.00001;
    "meas_VM1_5.00001_V.csv",   5.00001
    ];
files(:, :, 2) = [
    "meas_VM2_1.000007_V.csv",  1.000007;
    "meas_VM2_2.000007_V.csv",  2.000007;
    "meas_VM2_2.99999_V.csv",   2.99999;
    "meas_VM2_4.0_V.csv",       4.0;
    "meas_VM2_5.00016_V.csv",   5.00016
    ];
files(:, :, 3) = [
    "meas_VM1_99.9977_mV.csv",  99.9977;
    "meas_VM1_199.9926_mV.csv", 199.9926;
    "meas_VM1_300.003_mV.csv",  300.003;
    "meas_VM1_399.997_mV.csv",  399.997;
    "meas_VM1_500.01_mV.csv",   500.01
    ];
files(:,:, 4) = [
    "meas_VM2_100.0109_mV.csv", 100.0109;
    "meas_VM2_200.0095_mV.csv", 200.095;
    "meas_VM2_300.005_mV.csv",  300.005;
    "meas_VM2_399.999_mV.csv",  399.999;
    "meas_VM2_500.005_mV.csv",  500.005
    ];
files(:, :, 5) = [
    "meas_VM1_9.9856_mV.csv",   9.9856;
    "meas_VM1_19.9834_mV.csv",  19.9834;
    "meas_VM1_30.0075_mV.csv",  30.0075;
    "meas_VM1_40.0022_mV.csv",  40.0022;
    "meas_VM1_49.9825_mV.csv",  49.9825
    ];
% files(:, :, 5) = [
%     "meas_VM1_10.0018_mV.csv",  10.0018;
%     "meas_VM1_19.9989_mV.csv",  19.9989;
%     "meas_VM1_30.0024_mV.csv",  30.0024;
%     "meas_VM1_40.001_mV.csv",   40.001;
%     "meas_VM1_50.0004_mV.csv",  50.0004
%     ];
files(:,:, 6) = [
    "meas_VM2_10.0028_mV.csv",  10.0028;
    "meas_VM2_20.0051_mV.csv",  20.0051;
    "meas_VM2_29.9819_mV.csv",  29.9819;
    "meas_VM2_39.9963_mV.csv",  39.9963;
    "meas_VM2_50.0047_mV.csv",  50.0047
    ];

plotTitles = [
    "voltage measurement 1 - 1V range";
    "voltage measurement 2 - 1V range";
    "voltage measurement 1 - 500mV range";
    "voltage measurement 2 - 500mV range";
    "voltage measurement 1 - 50mV range";
    "voltage measurement 2 - 50mV range"
    ];

for voltageIndex = 1:size(files, 3)
    % save the diffrent voltages
    measurements = [];
    meanValues = [];
    stdDevis = [];
    maxDevis = [];
    
    % mV or V range??
    if voltageIndex > 2
        voltageRange = "mV";
    else
        voltageRange = "V";
    end
    
    % move text down in 50mV range
    if voltageIndex > 4
        up = 10;
        down = 10;
    else
        up = 0;
        down = 0;
    end
    
    xMargin = 0.3;
    lastMargin = 3.5;
    
    plotTitle = plotTitles(voltageIndex);
    for measIndex = 1:5
        appliedVoltage  = str2double(files(measIndex, 2, voltageIndex));
        fileName        = files(measIndex, 1, voltageIndex);
        data            = dlmread(fileName, ';', 1, 0);
        data(:,2) = [];
        meanValue = mean(data);
        stdDevi   = std(data);
        maxValue = abs(max(data) - appliedVoltage);
        minValue = abs(min(data) - appliedVoltage);
        if maxValue > minValue
            minMax = maxValue;
        else
            minMax = minValue;
        end
        maxDevis = [maxDevis, minMax];
        meanValues = [meanValues, meanValue];
        stdDevis = [stdDevis, stdDevi];
        data = [appliedVoltage; data];
        % first save the applied voltage then 
        measurements = [measurements, data];
    end
    
    fig = figure('Position', get(0, 'Screensize'));
    hold on
    
    title({plotTitle, "1000 measurements per applied voltage"}, 'FontSize', 25);
    labelString = ['applied voltage [' voltageRange ']'];
    xlabel(join(labelString), 'FontSize', 20);

    boxplot(measurements, measurements(1,:));
    labelString = ['measured voltage [' voltageRange ']'];
    ylabel(join(labelString), 'FontSize', 20);
    for ii = 1:4
        tmpStr = {
            join(['mean value: '  num2str(meanValues(ii))  voltageRange]),
            join(['standard deviation: ' num2str(stdDevis(ii)) voltageRange]),
            join(['max. deviation: '  num2str(maxDevis(ii))  voltageRange])};
        %sprintf("mean Value: %f V \nstandard Derivation: %f V", meanValues(ii), stdDeris(ii));
        text(ii + xMargin, meanValues(ii) - down, tmpStr, 'FontSize', 14);
    end
    tmpStr = {
        join(['mean value: '  num2str(meanValues(5))  voltageRange]),
        join(['standard deviation: ' num2str(stdDevis(5)) voltageRange]),
        join(['max. deviation: '  num2str(maxDevis(5))  voltageRange])};
    text(lastMargin, meanValues(5) + up, tmpStr, 'FontSize', 14);
    hold off
     
    tmp = strrep(plotTitle, ' ', '');
    tmp = strrep(tmp, '[2.5V]', '');
    tmp = strrep(tmp, '.', '');
    tmp = strrep(tmp, '-', '');
    saveas(fig, tmp + '.png')
end

