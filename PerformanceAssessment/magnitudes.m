%% Calculate failure magnitudes
% this script will calculate the magnitude of the worst failure for each
% year and each realization (i.e. Max_Alafia_magnitudes) and the maximum 30
% day moving average of failures for each year (Mov30_Alafia_magnitudes).

% it then calculates the percentiles for each year across realizations and
% prints them to csv files.

% calculate annual failures (could update to use sim calendar variable)

current_scenario = slacks_142;
scenario_number = 142;

Max_Alafia_magnitudes = zeros(1000,20);
Max_TBC_magnitudes = zeros(1000,20);
Max_Reservoir_magnitudes= zeros(1000,20);
Max_SCH3_magnitudes= zeros(1000,20);
Max_SCH_magnitudes= zeros(1000,20);
Max_BUD_magnitudes= zeros(1000,20);
Max_CWUP_magnitudes= zeros(1000,20);
% 
Mov30_Alafia_magnitudes = zeros(1000,20);
Mov30_TBC_magnitudes = zeros(1000,20);
Mov30_Reservoir_magnitudes= zeros(1000,20);
Mov30_SCH3_magnitudes= zeros(1000,20);
Mov30_SCH_magnitudes= zeros(1000,20);
Mov30_BUD_magnitudes= zeros(1000,20);
Mov30_CWUP_magnitudes= zeros(1000,20);




for i=1:1000
    cur_rel = current_scenario{i};
    j = 1;
    for day = 1:365:6936
        % Alafia
        Max_Alafia_magnitudes(i,j) = max(cur_rel.Alafia(day:day+364));
        if Max_Alafia_magnitudes(i,j) < 0
            Max_Alafia_magnitudes(i,j) =0;
        end
        for k=0:364
            if day + k + 30 < 7305
                temp_30 = mean(cur_rel.Alafia(day+k:day+k+30));
                if temp_30 < 0
                    temp_30=0;
                end
                if temp_30 > Mov30_Alafia_magnitudes(i,j)
                    Mov30_Alafia_magnitudes(i,j) = temp_30;
                end
            end 
        end
        
        % TBC
        Max_TBC_magnitudes(i,j) = max(cur_rel.TBC(day:day+364));
        if Max_TBC_magnitudes(i,j) < 0
            Max_TBC_magnitudes(i,j) =0;
        end
        for k=0:364
            if day + k + 30 < 7305
                temp_30 = mean(cur_rel.TBC(day+k:day+k+30));
                if temp_30 <0
                    temp_30=0;
                end
                if temp_30 > Mov30_TBC_magnitudes(i,j)
                    Mov30_TBC_magnitudes(i,j) = temp_30;
                end
            end
        end        
        
        
        % note, not sure if we should include res
        Max_Reservoir_magnitudes(i,j) = max(cur_rel.Reservoir(day:day+364));
        if Max_Reservoir_magnitudes(i,j) < 0
            Max_Reservoir_magnitudes(i,j) =0;
        end
        for k=0:364
            if day + k + 30 < 7305
                temp_30 = mean(cur_rel.Reservoir(day+k:day+k+30));
                if temp_30 <0
                    temp_30=0;
                end
                if temp_30 > Mov30_Reservoir_magnitudes(i,j)
                    Mov30_Reservoir_magnitudes(i,j) = temp_30;
                end
            end
        end
        
        
        % SCH3
        Max_SCH3_magnitudes(i,j) = max(cur_rel.SCH3(day:day+364));
        if Max_SCH3_magnitudes(i,j) < 0
            Max_SCH3_magnitudes(i,j) =0;
        end
        for k=0:364
            if day + k + 30 < 7305
                temp_30 = mean(cur_rel.SCH3(day+k:day+k+30));
                if temp_30 <0
                    temp_30=0;
                end
                if temp_30 > Mov30_SCH3_magnitudes(i,j)
                    Mov30_SCH3_magnitudes(i,j) = temp_30;
                end
            end 
        end        
        
        % SCH
        Max_SCH_magnitudes(i,j) = max(cur_rel.SCH(day:day+364) );
        if Max_SCH_magnitudes(i,j) < 0
            Max_SCH_magnitudes(i,j) =0;
        end
        for k=0:364
            if day + k + 30 < 7305
                temp_30 = mean(cur_rel.SCH(day+k:day+k+30));
                if temp_30 <0
                    temp_30=0;
                end
                if temp_30 > Mov30_SCH_magnitudes(i,j)
                    Mov30_SCH_magnitudes(i,j) = temp_30;
                end
            end
        end        
        
        
        % BUD
        Max_BUD_magnitudes(i,j) = max(cur_rel.BUD(day:day+364));
        if Max_BUD_magnitudes(i,j) < 0
            Max_BUD_magnitudes(i,j) =0;
        end
        for k=0:364
            if day + k + 30 < 7305
                temp_30 = mean(cur_rel.BUD(day+k:day+k+30));
                if temp_30 <0
                    temp_30=0;
                end
                if temp_30 > Mov30_BUD_magnitudes(i,j)
                    Mov30_BUD_magnitudes(i,j) = temp_30;
                end
            end
        end        
        
        % CWUP
        Max_CWUP_magnitudes(i,j) = max(cur_rel.CWUP(day:day+364));
        if Max_CWUP_magnitudes(i,j) < 0
            Max_CWUP_magnitudes(i,j) =0;
        end
        for k=0:364
            if day + k + 30 < 7305
                temp_30 = mean(cur_rel.CWUP(day+k:day+k+30));
                if temp_30 <0
                    temp_30=0;
                end
                if temp_30 > Mov30_CWUP_magnitudes(i,j)
                    Mov30_CWUP_magnitudes(i,j) = temp_30;
                end
            end
        end        
        
        
        j = j+1;
               
    end
    
end

%total_magnitudes_noSCH = Mov30_Alafia_magnitudes + Mov30_TBC_magnitudes + ...
 %   Mov30_Reservoir_magnitudes + Mov30_BUD_magnitudes + Mov30_CWUP_magnitudes;

%total_magnitudes_SCH = Mov30_SCH3_magnitudes + Mov30_SCH_magnitudes;


% calculate percentiles
Alafia_Max_percentiles = zeros(20,100);
TBC_Max_percentiles = zeros(20,100);
Reservoir_Max_percentiles = zeros(20,100);
SCH3_Max_percentiles = zeros(20,100);
SCH_Max_percentiles = zeros(20,100);
BUD_Max_percentiles = zeros(20,100);
CWUP_Max_percentiles = zeros(20,100);

for j =1:20
    Alafia_Max_percentiles(j,:) = prctile(Max_Alafia_magnitudes(:,j),(1:100));
    TBC_Max_percentiles(j,:) = prctile(Max_TBC_magnitudes(:,j),(1:100));
    Reservoir_Max_percentiles(j,:) = prctile(Max_Reservoir_magnitudes(:,j),(1:100));
    SCH3_Max_percentiles(j,:) = prctile(Max_SCH3_magnitudes(:,j),(1:100));
    SCH_Max_percentiles(j,:) = prctile(Max_SCH_magnitudes(:,j),(1:100));
    BUD_Max_percentiles(j,:) = prctile(Max_BUD_magnitudes(:,j),(1:100));
    CWUP_Max_percentiles(j,:) = prctile(Max_CWUP_magnitudes(:,j),(1:100));
end

Alafia_Mov30_percentiles = zeros(20,100);
TBC_Mov30_percentiles = zeros(20,100);
Reservoir_Mov30_percentiles = zeros(20,100);
SCH3_Mov30_percentiles = zeros(20,100);
SCH_Mov30_percentiles = zeros(20,100);
BUD_Mov30_percentiles = zeros(20,100);
CWUP_Mov30_percentiles = zeros(20,100);

for j =1:20
    Alafia_Mov30_percentiles(j,:) = prctile(Mov30_Alafia_magnitudes(:,j),(1:100));
    TBC_Mov30_percentiles(j,:) = prctile(Mov30_TBC_magnitudes(:,j),(1:100));
    Reservoir_Mov30_percentiles(j,:) = prctile(Mov30_Reservoir_magnitudes(:,j),(1:100));
    SCH3_Mov30_percentiles(j,:) = prctile(Mov30_SCH3_magnitudes(:,j),(1:100));
    SCH_Mov30_percentiles(j,:) = prctile(Mov30_SCH_magnitudes(:,j),(1:100));
    BUD_Mov30_percentiles(j,:) = prctile(Mov30_BUD_magnitudes(:,j),(1:100));
    CWUP_Mov30_percentiles(j,:) = prctile(Mov30_CWUP_magnitudes(:,j),(1:100));
end

% write to csv

alafia_out_file = strcat('Magnitude/Alafia_mov30_', num2str(scenario_number), '.csv');
csvwrite(alafia_out_file, Alafia_Mov30_percentiles)

TBC_out_file = strcat('Magnitude/TBC_mov30_', num2str(scenario_number), '.csv');
csvwrite(TBC_out_file, TBC_Mov30_percentiles)

reservoir_out_file = strcat('Magnitude/Reservoir_mov30_', num2str(scenario_number), '.csv');
csvwrite(reservoir_out_file, Reservoir_Mov30_percentiles)

SCH3_out_file = strcat('Magnitude/SCH3_mov30_', num2str(scenario_number), '.csv');
csvwrite(SCH3_out_file, SCH3_Mov30_percentiles)

SCH_out_file = strcat('Magnitude/SCH_mov30_', num2str(scenario_number), '.csv');
csvwrite(SCH_out_file, SCH_Mov30_percentiles)

BUD_out_file = strcat('Magnitude/BUD_mov30_', num2str(scenario_number), '.csv');
csvwrite('Magnitude/BUD_mov30.csv', BUD_Mov30_percentiles)

CWUP_out_file = strcat('Magnitude/CWUP_mov30_', num2str(scenario_number), '.csv');
csvwrite(CWUP_out_file, CWUP_Mov30_percentiles)

