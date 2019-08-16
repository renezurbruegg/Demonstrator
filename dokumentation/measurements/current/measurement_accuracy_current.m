files = [
    % file name                 % appliled voltage
    "meas_CM3_100.0_uA.csv",    100.0;
    "meas_CM3_199.996_uA.csv",  199.996;
    "meas_CM3_299.994_uA.csv",  299.994;
    "meas_CM3_399.997_uA.csv",  399.997;
    "meas_CM3_499.995_uA.csv",  499.995
    ];
files(:, :, 2) = [
    "meas_CM4_100.0_uA.csv",    100.0;
    "meas_CM4_199.998_uA.csv",  199.998;
    "meas_CM4_300.006_uA.csv",  300.006;
    "meas_CM4_399.998_uA.csv",  399.998;
    "meas_CM4_500_uA.csv",      500
    ];
files(:, :, 3) = [
    "meas_CM3_10.0_mA.csv",     10.0;
    "meas_CM3_19.9994_mA.csv",  19.9994;
    "meas_CM3_30.0003_mA.csv",  30.0003;
    "meas_CM3_40.0001_mA.csv",  40.0001;
    "meas_CM3_49.9999_mA.csv",  49.9999
    ];
files(:,:, 4) = [
    "meas_CM4_10.0_mA.csv",     10.0;
    "meas_CM4_20.0002_mA.csv",  20.0002;
    "meas_CM4_29.9999_mA.csv",  29.9999;
    "meas_CM4_39.9998_mA.csv",  39.9998;
    "meas_CM4_50.0001_mA.csv",  50.0001
    ];

plotTitles = [
    "current measurement 3 - 500uA range";
    "current measurement 4 - 500uA range";
    "current measurement 3 - 50mA range";
    "current measurement 4 - 50mA range";
    ];

for voltageIndex = 1:size(files, 3)
    % save the diffrent voltages
    measurements = [];
    meanValues = [];
    stdDevis = [];
    maxDevis = [];
    
    % uA or mA range??
    if voltageIndex > 2
        currentRange = "mA";
    else
        currentRange = "uA";
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
        meanValues = [meanValues, meanValue];
        stdDevis = [stdDevis, stdDevi];
        maxValue = abs(max(data) - appliedVoltage);
        minValue = abs(min(data) - appliedVoltage);
        if maxValue > minValue
            minMax = maxValue;
        else
            minMax = minValue;
        end
        maxDevis = [maxDevis, minMax];
        data = [appliedVoltage; data];
        % first save the applied voltage then 
        measurements = [measurements, data];
    end
    
    fig = figure('Position', get(0, 'Screensize'));
    hold on
    
    title({plotTitle, "1000 measurements per applied current"}, 'FontSize', 25);
    labelString = ['applied current [' currentRange ']'];
    xlabel(join(labelString), 'FontSize', 20);

    boxplot(measurements, measurements(1,:));
    labelString = ['measured current [' currentRange ']'];
    ylabel(join(labelString), 'FontSize', 20);
    for ii = 1:4
        tmpStr = {
            join(['mean value: '  num2str(meanValues(ii))  currentRange]),
            join(['standard deviation: ' num2str(stdDevis(ii)) currentRange]),
            join(['max. deviation: ' num2str(maxDevis(ii)) currentRange])};
        %sprintf("mean Value: %f V \nstandard Derivation: %f V", meanValues(ii), stdDeris(ii));
        text(ii + xMargin, meanValues(ii), tmpStr, 'FontSize', 14);
    end
    tmpStr = {
        join(['mean value: '  num2str(meanValues(5))  currentRange]),
        join(['standard deviation: ' num2str(stdDevis(5)) currentRange]),
        join(['max. deviation: ' num2str(maxDevis(5)) currentRange])};
    text(lastMargin, meanValues(5), tmpStr, 'FontSize', 14);
    hold off
    
    tmp = strrep(plotTitle, ' ', '');
    tmp = strrep(tmp, '[2.5V]', '');
    tmp = strrep(tmp, '.', '');
    tmp = strrep(tmp, '-', '');
    saveas(fig, tmp + '.png')
end

