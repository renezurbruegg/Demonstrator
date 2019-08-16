files = [
    % file name                                 % plot name
    "precision1_2.5V_0.5mA_40mA.csv",        "Precision Supply 1 [2.5V] rising edge: 0.5mA/40mA";
    "precision1_2.5V_0.5mA_40mA_falling.csv","Precision Supply 1 [2.5V] falling edge: 0.5mA/40mA";
    "precision1_2.5V_10mA_40mA.csv",         "Precision Supply 1 [2.5V] rising edge: 10mA/40mA";
    "precision2_2.5V_0.5mA_40mA.csv",        "Precision Supply 2 [2.5V] rising edge: 0.5mA/40mA";
    "precision2_2.5V_0.5mA_40mA_falling.csv","Precision Supply 2 [2.5V] falling edge: 0.5mA/40mA";
    "precision2_2.5V_10mA_40mA.csv",         "Precision Supply 2 [2.5V] rising edge: 10mA/40mA";
    "var1_2.5V_0.5mA_100mA.csv",            "Variable Supply 1 [2.5V] rising edge: 0.5mA/100mA";
    "var1_2.5V_0.5mA_100mA_falling.csv",    "Variable Supply 1 [2.5V] falling edge: 0.5mA/100mA";
    "var1_2.5V_10mA_70mA.csv",              "Variable Supply 1 [2.5V] rising edge: 10mA/70mA";
    "var1_2.5V_10mA_70mA_falling.csv",      "Variable Supply 1 [2.5V] falling edge: 10mA/70mA";
    "var2_2.5V_0.5mA_100mA.csv",            "Variable Supply 2 [2.5V] rising edge: 0.5mA/100mA";
    "var2_2.5V_0.5mA_100mA_falling.csv",    "Variable Supply 2 [2.5V] falling edge: 0.5mA/100mA";
    "var2_2.5V_10mA_70mA.csv",              "Variable Supply 2 [2.5V] rising edge: 10mA/70mA";
    "var2_2.5V_10mA_70mA_falling.csv",      "Variable Supply 2 [2.5V] falling edge: 10mA/70mA";
    "var3_2.5V_0.5mA_100mA.csv",            "Variable Supply 3 [2.5V] rising edge: 0.5mA/100mA";
    "var3_2.5V_0.5mA_100mA_falling.csv",    "Variable Supply 3 [2.5V] falling edge: 0.5mA/100mA";
    "var3_2.5V_10mA_70mA.csv",              "Variable Supply 3 [2.5V] rising edge: 10mA/70mA";
    "var3_2.5V_10mA_70mA_falling.csv",      "Variable Supply 3 [2.5V] falling edge: 10mA/70mA"
    ];

[fileCount,n] = size(files);

for index = 1:fileCount
    fileName            = files(index, 1);
    plotTitle           = files(index, 2);
    data                = csvread(fileName, 2, 0);
    myTime              = data(:,1) * 1000000;
    functionGenerator   = data(:,2);
    response            = data(:,3) * 1000;
    
    % search for max/min in response and label it
    [maxVal, maxIndex] = max(response);
    [minVal, minIndex] = min(response);
      
    fig = figure('Position', get(0, 'Screensize'));
    hold on
    
    title(plotTitle, 'FontSize', 24);
    xlabel('time [\mus]', 'FontSize', 20);

    yyaxis left
    plot(myTime, functionGenerator, "-", 'LineWidth', 4);
    ylabel('voltage [V]', 'FontSize', 20);

    yyaxis right
    plot(myTime, response, "-", 'LineWidth', 3);
    set(gca,'FontSize', 20);
    
    text(myTime(maxIndex), maxVal, ['\leftarrow ' num2str(maxVal) 'mV'], 'FontSize', 20);
    text(myTime(minIndex), minVal, ['\leftarrow ' num2str(minVal) 'mV'], 'FontSize', 20);
    ylabel('voltage [mV]', 'FontSize', 20);

    legend('function generator (DC coupling)', 'supply output (AC coupling)', 'Location', 'NorthWest');
    grid on
    
    hold off
    
    %%%%%%%%%% UNCOMMENT TO SAVE
%     tmp = strrep(plotTitle, '/', '_');
%     tmp = strrep(tmp, ':', '');
%     tmp = strrep(tmp, ' ', '');
%     tmp = strrep(tmp, '[2.5V]', '');
%     tmp = strrep(tmp, '.', '');
%     tmp = strrep(tmp, '-', '');    
%     saveas(fig, tmp + '.png')
end