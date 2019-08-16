%Body Bias pos and neg
%First column represents the current the second one the voltage
%plots Voltage vs Current
%mA V


BodyBias_0V5 = [
    
    0, 0.49;
    1.6, 0.49;
    2.5, 0.49;
    4.5, 0.49;
    12, 0.48
    12.8, 0.48;
    13.6, 0.37;
    14.3, 0.22;
    14.9, 0.11;
]

BodyBias_1V5 = [
   0, 1.495;
   1.2, 1.490;
   2.4, 1.489;
   4.2, 1.486;
   8.1, 1.310;
   9.7, 1.049;
   14.9, 0.121;
   
   
]

BodyBias_2V5 = [

]
BodyBiasNeg_0V5 = [
    0, 0.523;
    0.28, 0.522;
    0.36, 0.521;
    0.60, 0.520;
    0.87, 0.519;
    1.10,0.518;
    1.63,0.515;
    2.05,0.513;
    2.59,0.510;
    4.12,0.502;
    5.88,0.495;
    8.57,0.495;
    12.8,0.489;
    17.03,0.49;
    17.55,0.429;
    17.83,0.300;

]

BodyBiasNeg_1V5 = [
    0.0,1.516;
    0.82,1.513;
    01.07,1.511;
    1.34,1.510;
    1.55,1.509;
    1.98,1.507;
    2.16,1.506;
    2.52,1.504;
    2.92,1.502;
    3.25,1.5;
    3.85,1.496;
    4.65,1.491;
    5.32,1.484;
    6.21,1.482;
    7.21,1.481;
    9.06,1.485;
    11.29,1.484;
    12.7,1.481;
    13.11,1.481;
    14.25,1.488;
    15.17,1.324;
    15.83,1.103;
    17.04,0.650;
    17.84,0.296;
]

BodyBiasNeg_2V5 = [
    0.0,2.50;
    1.36,2.49;
    1.55,2.48;
    1.76,2.47;
    2.01,2.45;
    2.44,2.43;
    2.98,2.40;
    3.78,2.36;
    4.41,2.33;
    6.02,2.24;
    6.92,2.20;
    7.89,2.15;
    8.43,2.12;
    9.1,2.09;
    10.08,2.04;
    11.09,1.98;
    12.44,1.89;
    13.19,1.82;
    14.14,1.62;
    15.10,1.33;
    16.34,0.91;
    17.11,0.61;
    17.84,0.30;
]

figure
    subplot(2,1,1);
    hold on
    plot(BodyBias_0V5(:,1),BodyBias_0V5(:,2),"-o")
    legend({'Body Bias'},'Location','southwest');
    title({'0.5V'})
    xlabel('Supply Current [mA]');
    ylabel('Supply Voltage [V]');
    grid on
    
    subplot(2,1,2);
    hold on
    title ('1.5V')
    plot(BodyBias_1V5(:,1),BodyBias_1V5(:,2),"-o")
    legend({'Body Bias'},'Location','southwest');
    xlabel('Supply Current [mA]');
    ylabel('Supply Voltage [V]');
    grid on
    
    figure
    subplot(3,1,1);
    hold on
    title('-0.5V')
    plot(BodyBiasNeg_0V5(:,1),BodyBiasNeg_0V5(:,2),"-o")
    legend({'Body Bias Neg'},'Location','southwest');
    xlabel('Supply Current [-mA]');
    ylabel('Supply Voltage [-V]');
    grid on
    
    subplot(3,1,2);
    hold on
    title('-1.5V')
    plot(BodyBiasNeg_1V5(:,1),BodyBiasNeg_1V5(:,2),"-o")
    legend({'Body Bias Neg'},'Location','southwest');
    xlabel('Supply Current [-mA]');
    ylabel('Supply Voltage [-V]');
    grid on
    
    subplot(3,1,3);
    hold on
    title('-2.5V')
    plot(BodyBiasNeg_2V5(:,1),BodyBiasNeg_2V5(:,2),"-o")
    legend({'Body Bias Neg'},'Location','southwest');
    xlabel('Supply Current [-mA]');
    ylabel('Supply Voltage [-V]');
    grid on