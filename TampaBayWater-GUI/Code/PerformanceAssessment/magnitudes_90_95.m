%% Calculate failure magnitudes
% this script will calculate the magnitude of the worst failure for each
% year and each realization (i.e. Max_Alafia_magnitudes) and the maximum 30
% day moving average of failures for each year (Mov30_Alafia_magnitudes).

% it then calculates the percentiles for each year across realizations and
% prints them to csv files.

% calculate annual failures (could update to use sim calendar variable)

current_scenario = slacks_141;
scenario_number = 144;

realization_list = [494 396 723 701 110 142 545 94 51 368 192 554 488 449 57 ...
    80 317 21 357 154 443 77 52 218 22 42 217 671 679 479 409 64 570 273 ...
    393 997 33 874 471 243 139 523 956 608 527 375 964 646 633 536];

rolling_mean = zeros(7305-30,50);

for i=1:1000
    cur_rel = current_scenario{realization_list(i)};
    j = 1;
    
    all_slack = cur_rel.Alafia + cur_rel.TBC + cur_rel.CWUP + ...
    cur_rel.Reservoir + cur_rel.BUD + cur_rel.SCH + cur_rel.SCH3;

    
    for day = 1:365:6936
        for k=0:364
            if day + k + 30 < 7305
                rolling_mean(day+k,i) = mean(all_slack(day+k:day+k+30));
            end
        end
    end
end
%
max_rolling = zeros(7275,1);
for i=1:7275
    max_rolling(i) = max(rolling_mean(i,:));
end
%%

hold on
plot(1:7275, max_rolling)
