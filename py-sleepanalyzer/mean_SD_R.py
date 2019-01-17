# Generated with SMOP  0.41
from myutils import *
# mean_SD_R.m
def mean_SD_R(dirPath):
    #指定的文件夹以及下级文件夹中需要包含有使用 main_SD_R 或者 batProcess处理之后的'time'_main_SD_R.mat，以及config_flys.txt, 将会合并所有的同名的文件
    
    #speed_30mins_CT计算的数值为每秒平均速度，1：除去被计算为睡眠的点，但是速度为0，但不满足睡眠条件的点没有排除；2：除去速度>10的点
# ！speed 数据经过降噪，因为trace可能暂时跟丢，将计算一个超大的数值，本处暂时忽略所有speed>=10 的 point！
#sleep_30mins_SD以及sleep_30mins_CT,计算的为30min之内睡眠的秒数总和,
#food_distance_30CT,计算的为与食物的平均距离
#sleep_center,计算的所有每一分钟睡眠时长按照当前CT值的加权平均，也就是睡眠发生时间的中值
    
    ## 0.loading数据,
#依照 30mins_CT 预处理food_distance{*,8}均值,以及CT_time_list重新计算;并且重新存储
#以及sleep_matrix的加权均值,分day以及night;之后只留下之后处理需要使用的数据:{*,1,3,6,7,8}为lineName;speed_30mins_CT;sleep_30mins_SD;sleep_30mins_CT;food_distance_30CT;sleep_center
	# input data file list
    lFInputMat=getAllFiles(dirPath,'main-py_SD_R')
    #计算line_number
    line_number=0
# mean_SD_R.m:17
    for i in arange(1,size(lFInputMat,1)).reshape(-1):
        load(lFInputMat[i,1],'raw_draw_out')
        line_number=line_number + size(raw_draw_out,1)
# mean_SD_R.m:20
        clear('raw_draw_out')
    
    grouped_data=cell(line_number,6)
# mean_SD_R.m:23
    
    ##
    for i in arange(1,size(lFInputMat,1)).reshape(-1):
        outputDir=lFInputMat[i,1](arange(1,end() - 14))
# mean_SD_R.m:26
        outputMat=concat([outputDir,'\\main_SD_R_Addition.mat'])
# mean_SD_R.m:26
        clear('outputDir')
        # 重新计算CT_time_list
        load(lFInputMat[i,1],'min_time_length','config_time_M')
        #标记白天，晚上
        CT_time_list_temp=zeros(min_time_length,2)
# mean_SD_R.m:30
        for j in arange(1,size(config_time_M,1)).reshape(-1):
            CT_time_list_temp[arange(config_time_M(j,1),config_time_M(j,2)),1]=config_time_M(j,3)
# mean_SD_R.m:32
        #标记CT time /mins
        if config_time_M(1,3) == 0:
            CT_time_list_temp[arange(config_time_M(1,1),config_time_M(1,2)),2]=(arange((1440 - (config_time_M(1,2) - config_time_M(1,1))),1440))
# mean_SD_R.m:36
        else:
            CT_time_list_temp[arange(config_time_M(1,1),config_time_M(1,2)),2]=(arange((720 - (config_time_M(1,2) - config_time_M(1,1))),720))
# mean_SD_R.m:38
        for j in arange(2,size(config_time_M,1)).reshape(-1):
            if config_time_M(j,3) == 0:
                CT_time_list_temp[arange(config_time_M(j,1),config_time_M(j,2)),2]=(arange(721,(721 + (config_time_M(j,2) - config_time_M(j,1)))))
# mean_SD_R.m:42
            else:
                CT_time_list_temp[arange(config_time_M(j,1),config_time_M(j,2)),2]=(arange(1,(1 + (config_time_M(j,2) - config_time_M(j,1)))))
# mean_SD_R.m:44
        if min_time_length < size(CT_time_list_temp,1):
            CT_time_list=zeros(min_time_length,2)
# mean_SD_R.m:48
            CT_time_list[arange(1,end()),arange()]=CT_time_list_temp(arange(1,size(CT_time_list,1)),arange())
# mean_SD_R.m:49
        else:
            CT_time_list=copy(CT_time_list_temp)
# mean_SD_R.m:51
        clear('CT_time_list_temp')
        #计算 sleep_center, 睡眠发生的代数中心,分night以及day
        load(lFInputMat[i,1],'sleep_mins')
        sleep_center=cell(size(sleep_mins,1),1)
# mean_SD_R.m:57
        for k in arange(1,size(sleep_mins,1)).reshape(-1):
            sleep_center_temp=zeros(size(config_time_M,1),size(sleep_mins[k,1],2))
# mean_SD_R.m:59
            CT_time_mask=zeros(size(sleep_mins[k,1]))
# mean_SD_R.m:60
            for j in arange(1,size(sleep_mins[k,1],2)).reshape(-1):
                CT_time_mask[arange(),j]=CT_time_list(arange(),2)
# mean_SD_R.m:62
            sleep_mins_sum=multiply(sleep_mins[k,1],CT_time_mask)
# mean_SD_R.m:64
            for j in arange(1,size(config_time_M,1) - 1).reshape(-1):
                sleep_center_temp[j,arange()]=sum(sleep_mins_sum(arange(config_time_M(j,1),config_time_M(j,2)),arange()),1) / double(dot(60,(config_time_M(j,2) - config_time_M(j,1) + 1)))
# mean_SD_R.m:66
            j=size(config_time_M,1)
# mean_SD_R.m:68
            sleep_center_temp[j,arange()]=sum(sleep_mins_sum(arange(config_time_M(j,1),end()),arange()),1) / double(dot(60,(size(sleep_mins[k,1],1) - config_time_M(j,1) + 1)))
# mean_SD_R.m:69
            sleep_center[k,1]=sleep_center_temp
# mean_SD_R.m:70
        clear('sleep_mins','CT_time_mask','sleep_mins_sum','sleep_center_temp')
        #计算food_distance_30CT
        load(lFInputMat[i,1],'food_distance','sleep_30mins_CT')
        food_distance_30CT=cell(size(food_distance,1),1)
# mean_SD_R.m:76
        for k in arange(1,size(food_distance,1)).reshape(-1):
            distance_30CT_raw=food_distance[k,1]
# mean_SD_R.m:78
            distance_30CT_temp=zeros(size(sleep_30mins_CT[1,1],1),size(distance_30CT_raw,2))
# mean_SD_R.m:79
            ravel[distance_30CT_temp]=- 1
# mean_SD_R.m:80
            distance_30CT_point=ceil(CT_time_list(1,2) / 30)
# mean_SD_R.m:81
            distance_30CT_temp2=zeros(1,size(distance_30CT_raw,2))
# mean_SD_R.m:82
            for j in arange(1,dot(min_time_length,60)).reshape(-1):
                distance_30CT_temp2=distance_30CT_temp2 + distance_30CT_raw(j,arange())
# mean_SD_R.m:84
                if mod(CT_time_list(ceil(j / 60),2),30) == 0 and mod(j,60) == 0:
                    distance_30CT_temp[distance_30CT_point,arange()]=distance_30CT_temp2 / 1800
# mean_SD_R.m:86
                    distance_30CT_point=distance_30CT_point + 1
# mean_SD_R.m:87
                    ravel[distance_30CT_temp2]=0
# mean_SD_R.m:88
            distance_30CT_point=ceil(CT_time_list(1,2) / 30)
# mean_SD_R.m:91
            if mod((CT_time_list(1,2) - 1),30) != 0:
                distance_30CT_temp[distance_30CT_point,arange()]=- 1
# mean_SD_R.m:93
            food_distance_30CT[k,1]=distance_30CT_temp
# mean_SD_R.m:95
        clear('sleep_30mins_CT','food_distance','distance_30CT_raw','distance_30CT_temp','distance_30CT_point','distance_30CT_temp2')
        save(outputMat,'CT_time_list','sleep_center','food_distance_30CT','-v7.3')
        clear('outputMat','min_time_length','config_time_M','outputMat','CT_time_list','sleep_center','food_distance_30CT','CT_time_list')
    
    # line_number 保存
## 0.2 pregroup 数据;把所有需要处理的数据在同一录像内按照品系分组
    for i in arange(1,size(lFInputMat,1)).reshape(-1):
        load(lFInputMat[i,1],'import_data_Complex_order','raw_draw_out','sleep_30mins_SD','sleep_30mins_CT','speed_30mins_CT')
        RelFInputMat=concat([lFInputMat[i,1](arange(1,end() - 14)),'\\main_SD_R_Addition.mat'])
# mean_SD_R.m:105
        load(RelFInputMat,'sleep_center','food_distance_30CT')
        preGroupMat=concat([lFInputMat[i,1](arange(1,end() - 14)),'\\preGroup.mat'])
# mean_SD_R.m:107
        grouped_output=cell(size(raw_draw_out,1),6)
# mean_SD_R.m:108
        line_number_Indi=1
# mean_SD_R.m:109
        for j in arange(1,size(import_data_Complex_order,1)).reshape(-1):
            for k in arange(1,size(import_data_Complex_order[j,1],1)).reshape(-1):
                grouped_output[line_number_Indi,1]=import_data_Complex_order[j,1][k,1]
# mean_SD_R.m:112
                grouped_output[line_number_Indi,2]=speed_30mins_CT[j,1](arange(),str2double(import_data_Complex_order[j,1][k,2]) + 1)
# mean_SD_R.m:113
                grouped_output[line_number_Indi,3]=sleep_30mins_SD[j,1](arange(),str2double(import_data_Complex_order[j,1][k,2]) + 1)
# mean_SD_R.m:114
                grouped_output[line_number_Indi,4]=sleep_30mins_CT[j,1](arange(),str2double(import_data_Complex_order[j,1][k,2]) + 1)
# mean_SD_R.m:115
                grouped_output[line_number_Indi,5]=food_distance_30CT[j,1](arange(),str2double(import_data_Complex_order[j,1][k,2]) + 1)
# mean_SD_R.m:116
                grouped_output[line_number_Indi,6]=sleep_center[j,1](arange(),str2double(import_data_Complex_order[j,1][k,2]) + 1)
# mean_SD_R.m:117
                line_number_Indi=line_number_Indi + 1
# mean_SD_R.m:118
        save(preGroupMat,'grouped_output','raw_draw_out','-v7.3')
        clear('import_data_Complex_order','raw_draw_out','sleep_30mins_SD','sleep_30mins_CT','sleep_center','food_distance_30CT','preGroupMat','grouped_output','speed_30mins_CT')
        clear('line_number_Indi')
    
    ## 1.依照config_flys.txt去除不能使用的时间片段
#选择的可以用的数据为<0的数，没有被选中的为-1,matrix大小与inport的数据大小相同。
#output的mean-sleep-30min-CT的数据为所有数据最前面的一部分数据。如果没有选中fragment 1,2,3,4,则会缺少数据
    grouped_data_temp=cell(size(lFInputMat,1),2)
# mean_SD_R.m:129
    for i in arange(1,size(lFInputMat,1)).reshape(-1):
        D_InClu_C=F_Include_Info(concat([lFInputMat[i,1](arange(1,end() - 14)),'\\config_flys.txt']))
# mean_SD_R.m:131
        preGroupMat=concat([lFInputMat[i,1](arange(1,end() - 14)),'\\preGroup.mat'])
# mean_SD_R.m:132
        load(preGroupMat,'grouped_output','raw_draw_out')
        load(lFInputMat[i,1],'config_time_M')
        CT_transList=zeros(24,size(config_time_M,1))
# mean_SD_R.m:135
        if config_time_M(1,3) == 1:
            for j in arange(1,size(config_time_M,1)).reshape(-1):
                CT_transList[arange(),j]=arange((dot(j,24) - 23),dot(j,24))
# mean_SD_R.m:138
        else:
            for j in arange(1,size(config_time_M,1)).reshape(-1):
                CT_transList[arange(),j]=(arange(dot(j,24) + 1,dot(j,24) + 24))
# mean_SD_R.m:142
        Sorted_inclu=zeros(size(D_InClu_C,1),4)
# mean_SD_R.m:146
        for j in arange(1,size(D_InClu_C,1)).reshape(-1):
            Sorted_inclu[j,1]=D_InClu_C[j,4]
# mean_SD_R.m:148
            Sorted_inclu[j,2]=D_InClu_C[j,2]
# mean_SD_R.m:149
            Sorted_inclu[j,3]=D_InClu_C[j,7]
# mean_SD_R.m:150
            Sorted_inclu[j,4]=j
# mean_SD_R.m:151
        Sorted_inclu=sortrows(Sorted_inclu,concat([1,3]))
# mean_SD_R.m:153
        grouped_data_sorted=cell(size(grouped_output,1),6)
# mean_SD_R.m:155
        raw_draw_out_sorted=cell(size(grouped_output,1),2)
# mean_SD_R.m:156
        for j in arange(1,size(grouped_output,1)).reshape(-1):
            grouped_data_sorted[j,1]=grouped_output[j,1]
# mean_SD_R.m:158
            for k in arange(2,6).reshape(-1):
                grouped_data_sorted[j,k]=zeros(size(grouped_output[j,k]))
# mean_SD_R.m:160
                ravel[grouped_data_sorted[j,k]]=- 1
# mean_SD_R.m:161
            raw_draw_out_sorted[j,1]=raw_draw_out[j,1]
# mean_SD_R.m:163
            raw_draw_out_sorted[j,2]=zeros(size(raw_draw_out[j,2]))
# mean_SD_R.m:164
            ravel[raw_draw_out_sorted[j,2]]=- 1
# mean_SD_R.m:165
            raw_draw_out_sorted[j,2][arange(),1]=raw_draw_out[j,2](arange(),1)
# mean_SD_R.m:166
        indi_seq_temp=1
# mean_SD_R.m:168
        for j in arange(1,size(Sorted_inclu,1)).reshape(-1):
            if Sorted_inclu(j,3) > 0:
                for k in arange(1,size(D_InClu_C[Sorted_inclu(j,4),3],2)).reshape(-1):
                    indi_line_temp=Sorted_inclu(j,1)
# mean_SD_R.m:172
                    indi_frag_temp=CT_transList(arange(),D_InClu_C[Sorted_inclu(j,4),3](1,k))
# mean_SD_R.m:172
                    indi_indi_temp=Sorted_inclu(j,2)
# mean_SD_R.m:172
                    grouped_data_sorted[indi_line_temp,2][indi_frag_temp,indi_seq_temp]=grouped_output[indi_line_temp,2](indi_frag_temp,indi_indi_temp)
# mean_SD_R.m:173
                    grouped_data_sorted[indi_line_temp,4][indi_frag_temp,indi_seq_temp]=grouped_output[indi_line_temp,4](indi_frag_temp,indi_indi_temp)
# mean_SD_R.m:174
                    grouped_data_sorted[indi_line_temp,5][indi_frag_temp,indi_seq_temp]=grouped_output[indi_line_temp,5](indi_frag_temp,indi_indi_temp)
# mean_SD_R.m:175
                    grouped_data_sorted[indi_line_temp,6][D_InClu_C[Sorted_inclu(j,4),3](1,k),indi_seq_temp]=grouped_output[indi_line_temp,6](D_InClu_C[Sorted_inclu(j,4),3](1,k),indi_indi_temp)
# mean_SD_R.m:176
                    indi_frag_jpeg=arange(config_time_M(D_InClu_C[Sorted_inclu(j,4),3](1,k),1),config_time_M(D_InClu_C[Sorted_inclu(j,4),3](1,k),2))
# mean_SD_R.m:178
                    raw_draw_out_sorted[indi_line_temp,2][indi_frag_jpeg,indi_seq_temp + 1]=raw_draw_out[indi_line_temp,2](indi_frag_jpeg,indi_indi_temp + 1)
# mean_SD_R.m:179
                    clear('indi_line_temp','indi_frag_temp','indi_indi_temp','indi_frag_jpeg')
            #只有在前三个片段都被选中的时候，前24小时的sleep数据才使用，否则废弃
            if Sorted_inclu(j,3) >= 3 and isempty(setdiff(D_InClu_C[Sorted_inclu(j,4),3](1,arange(1,3)),concat([1,2,3]))):
                indi_line_temp=Sorted_inclu(j,1)
# mean_SD_R.m:185
                indi_indi_temp=Sorted_inclu(j,2)
# mean_SD_R.m:185
                grouped_data_sorted[indi_line_temp,3][arange(),indi_seq_temp]=grouped_output[indi_line_temp,3](arange(),indi_indi_temp)
# mean_SD_R.m:186
                clear('indi_line_temp','indi_indi_temp')
            if j < size(Sorted_inclu,1):
                if Sorted_inclu(j,1) == Sorted_inclu(j + 1,1):
                    indi_seq_temp=indi_seq_temp + 1
# mean_SD_R.m:191
                else:
                    indi_seq_temp=1
# mean_SD_R.m:193
        grouped_data_temp[i,1]=grouped_data_sorted
# mean_SD_R.m:197
        grouped_data_temp[i,2]=raw_draw_out_sorted
# mean_SD_R.m:198
        clear('grouped_output','raw_draw_out','config_time_M','D_InClu_C','grouped_data_sorted','raw_draw_out_sorted','CT_transList','preGroupMat','Sorted_inclu','indi_seq_temp')
    
    save(concat([dirPath,'\\grouped_data.mat']),'grouped_data_temp','-v7.3')
    
    #最后可以使用的数据在grouped_data_temp
## 2.输出过滤之后的图片
    for i in arange(1,size(lFInputMat,1)).reshape(-1):
        outputJPEG=concat([lFInputMat[i,1](arange(1,end() - 14)),'\\selected'])
# mean_SD_R.m:205
        raw_drawn_out_temp=grouped_data_temp[i,2]
# mean_SD_R.m:206
        for j in arange(1,size(raw_drawn_out_temp,1)).reshape(-1):
            raw_drawn_out_temp[j,2][raw_drawn_out_temp[j,2] < 0]=0
# mean_SD_R.m:208
        mkdir(outputJPEG)
        raw_drawn_func(raw_drawn_out_temp,outputJPEG)
    
    clear('outputJPEG','raw_drawn_out_temp')
    ## 3.依照名称group果蝇
    line_indi=1
# mean_SD_R.m:215
    for i in arange(1,size(grouped_data_temp)).reshape(-1):
        for j in arange(1,size(grouped_data_temp[i,1],1)).reshape(-1):
            for k in arange(1,6).reshape(-1):
                grouped_data[line_indi,k]=grouped_data_temp[i,1][j,k]
# mean_SD_R.m:219
            line_indi=line_indi + 1
# mean_SD_R.m:221
    
    line_ID_number=zeros(line_number,3)
# mean_SD_R.m:224
    
    for i in arange(1,line_number).reshape(-1):
        temp_line_name=regexp(grouped_data[i,1],'-','split')
# mean_SD_R.m:226
        if size(temp_line_name,2) == 2:
            line_ID_number[i,1]=str2double(cell2mat(regexp(temp_line_name[1,1],'\\d','match')))
# mean_SD_R.m:228
            line_ID_number[i,2]=str2double(cell2mat(regexp(temp_line_name[1,2],'\\d','match')))
# mean_SD_R.m:229
            line_ID_number[i,3]=i
# mean_SD_R.m:230
        else:
            line_ID_number[i,1]=- 1
# mean_SD_R.m:232
            line_ID_number[i,2]=- 1
# mean_SD_R.m:232
            line_ID_number[i,3]=i
# mean_SD_R.m:232
    
    line_ID_number=sortrows(line_ID_number,concat([1,2]))
# mean_SD_R.m:235
    group_data_sorted=cell(line_number,6)
# mean_SD_R.m:236
    
    for i in arange(1,line_number).reshape(-1):
        for j in arange(1,6).reshape(-1):
            group_data_sorted[i,j]=grouped_data[line_ID_number(i,3),j]
# mean_SD_R.m:239
    
    clear('line_indi','grouped_data_temp','line_ID_number','grouped_data','temp_line_name')
    save(concat([dirPath,'\\grouped_data_sorted.mat']),'group_data_sorted','-v7.3')
    #grouped_data_sorted: {*,1}line name; {*,2}speed_30mins_CT,{*,3}sleep_30mins_SD, {*,4}sleep_30mins_CT, {*,5}food_distance_30CT, {*,6}sleep_center
## 4.输出所有果蝇，以30mins为间隔的各数据的txt文件,依品系名称分隔,以及该品系的平均值
#lineName;speed_30mins_CT;sleep_30mins_SD;sleep_30mins_CT;food_distance_30CT;sleep_center
    fid_speed_30mins_CT=fopen(concat([dirPath,'\\speed_30mins_CT.txt']),'w')
# mean_SD_R.m:247
    fid_sleep_30mins_SD=fopen(concat([dirPath,'\\sleep_30mins_SD.txt']),'w')
# mean_SD_R.m:248
    fid_sleep_30mins_CT=fopen(concat([dirPath,'\\sleep_30mins_CT.txt']),'w')
# mean_SD_R.m:249
    fid_food_distance_30CT=fopen(concat([dirPath,'\\food_distance_30CT.txt']),'w')
# mean_SD_R.m:250
    fid_sleep_center=fopen(concat([dirPath,'\\sleep_center.txt']),'w')
# mean_SD_R.m:251
    for i in arange(1,size(group_data_sorted,1)).reshape(-1):
        #speed_30mins_CT
        for a in arange(1,size(group_data_sorted[i,2],2)).reshape(-1):
            fprintf(fid_speed_30mins_CT,'%s\\t',group_data_sorted[i,1])
            for b in arange(1,size(group_data_sorted[i,2],1)).reshape(-1):
                if (group_data_sorted[i,2](b,a) >= 0):
                    fprintf(fid_speed_30mins_CT,'%f\\t',group_data_sorted[i,2](b,a))
                else:
                    fprintf(fid_speed_30mins_CT,'\\t')
            fprintf(fid_speed_30mins_CT,'\\n')
        #sleep_30mins_SD
        for a in arange(1,size(group_data_sorted[i,3],2)).reshape(-1):
            fprintf(fid_sleep_30mins_SD,'%s\\t',group_data_sorted[i,1])
            for b in arange(1,size(group_data_sorted[i,3],1)).reshape(-1):
                if group_data_sorted[i,3](b,a) >= 0:
                    fprintf(fid_sleep_30mins_SD,'%f\\t',group_data_sorted[i,3](b,a))
                else:
                    fprintf(fid_sleep_30mins_SD,'\\t')
            fprintf(fid_sleep_30mins_SD,'\\n')
        #sleep_30mins_CT
        for a in arange(1,size(group_data_sorted[i,4],2)).reshape(-1):
            fprintf(fid_sleep_30mins_CT,'%s\\t',group_data_sorted[i,1])
            for b in arange(1,size(group_data_sorted[i,4],1)).reshape(-1):
                if group_data_sorted[i,4](b,a) >= 0:
                    fprintf(fid_sleep_30mins_CT,'%f\\t',group_data_sorted[i,4](b,a))
                else:
                    fprintf(fid_sleep_30mins_CT,'\\t')
            fprintf(fid_sleep_30mins_CT,'\\n')
        #food_distance_30CT
        for a in arange(1,size(group_data_sorted[i,5],2)).reshape(-1):
            fprintf(fid_food_distance_30CT,'%s\\t',group_data_sorted[i,1])
            for b in arange(1,size(group_data_sorted[i,5],1)).reshape(-1):
                if group_data_sorted[i,5](b,a) >= 0:
                    fprintf(fid_food_distance_30CT,'%f\\t',group_data_sorted[i,5](b,a))
                else:
                    fprintf(fid_food_distance_30CT,'\\t')
            fprintf(fid_food_distance_30CT,'\\n')
        #sleep_center
        for a in arange(1,size(group_data_sorted[i,6],2)).reshape(-1):
            fprintf(fid_sleep_center,'%s\\t',group_data_sorted[i,1])
            for b in arange(1,size(group_data_sorted[i,6],1)).reshape(-1):
                if group_data_sorted[i,6](b,a) >= 0:
                    fprintf(fid_sleep_center,'%f\\t',group_data_sorted[i,6](b,a))
                else:
                    fprintf(fid_sleep_center,'\\t')
            fprintf(fid_sleep_center,'\\n')
    
    fclose(fid_speed_30mins_CT)
    fclose(fid_sleep_30mins_SD)
    fclose(fid_sleep_30mins_CT)
    fclose(fid_food_distance_30CT)
    fclose(fid_sleep_center)
    clear('fid_speed_30mins_CT','fid_sleep_30mins_SD','fid_sleep_30mins_CT','fid_food_distance_30CT','fid_sleep_center')
    #输出12小时整合之后的所有_CT参数
    group_data_sorted_add=cell(size(group_data_sorted,1),9)
# mean_SD_R.m:322
    #{1-3}将12小时的数据平均之后的数值，几天之间的差值//{4-6}将所有天平均之后一个CT时间下的均值，看一天之内的变化
#{7-9}白天黑夜的平均值，这里取的是平均值，开始的数据为30mins之内的速度均值，睡眠时长累加，距离均值，计算之后的结果也为30min的均值
    max_length=1
# mean_SD_R.m:325
    
    for i in arange(1,size(group_data_sorted,1)).reshape(-1):
        #按照12小时合并_CT数据，包括 speed_30mins_CT, sleep_30mins_CT, food_distance_30CT
        temp_speed=group_data_sorted[i,2]
# mean_SD_R.m:328
        temp_speed[temp_speed < 0]=0
# mean_SD_R.m:328
        temp_speed_30mins_CT=zeros(size(group_data_sorted[i,2],1) / 24,size(group_data_sorted[i,2],2))
# mean_SD_R.m:329
        temp_sleep_30mins_CT=zeros(size(temp_speed_30mins_CT))
# mean_SD_R.m:330
        temp_food_distance_30CT=zeros(size(temp_speed_30mins_CT))
# mean_SD_R.m:331
        for j in arange(1,size(temp_speed_30mins_CT,1)).reshape(-1):
            temp_speed_30mins_CT[j,arange()]=mean(temp_speed(arange(dot(j,24) - 23,dot(j,24)),arange()),1)
# mean_SD_R.m:333
            temp_sleep_30mins_CT[j,arange()]=mean(group_data_sorted[i,4](arange(dot(j,24) - 23,dot(j,24)),arange()),1)
# mean_SD_R.m:334
            temp_food_distance_30CT[j,arange()]=mean(group_data_sorted[i,5](arange(dot(j,24) - 23,dot(j,24)),arange()),1)
# mean_SD_R.m:335
        group_data_sorted_add[i,1]=temp_speed_30mins_CT
# mean_SD_R.m:337
        group_data_sorted_add[i,2]=temp_sleep_30mins_CT
# mean_SD_R.m:338
        group_data_sorted_add[i,3]=temp_food_distance_30CT
# mean_SD_R.m:339
        if size(group_data_sorted[i,2],1) > max_length:
            max_length=size(group_data_sorted[i,2],1)
# mean_SD_R.m:341
        clear('temp_speed')
    
    fid_speed_12h_CT=fopen(concat([dirPath,'\\speed_12h_CT.txt']),'w')
# mean_SD_R.m:345
    fid_sleep_12h_CT=fopen(concat([dirPath,'\\sleep_12h_CT.txt']),'w')
# mean_SD_R.m:346
    fid_distance_12h_CT=fopen(concat([dirPath,'\\distance_12h_CT.txt']),'w')
# mean_SD_R.m:347
    for i in arange(1,size(group_data_sorted,1)).reshape(-1):
        for a in arange(1,size(group_data_sorted_add[i,1],2)).reshape(-1):
            fprintf(fid_speed_12h_CT,'%s\\t',group_data_sorted[i,1])
            for b in arange(1,size(group_data_sorted_add[i,1],1)).reshape(-1):
                if group_data_sorted_add[i,1](b,a) >= 0:
                    fprintf(fid_speed_12h_CT,'%f\\t',group_data_sorted_add[i,1](b,a))
                else:
                    fprintf(fid_speed_12h_CT,'\\t')
            fprintf(fid_speed_12h_CT,'\\n')
        for a in arange(1,size(group_data_sorted_add[i,2],2)).reshape(-1):
            fprintf(fid_sleep_12h_CT,'%s\\t',group_data_sorted[i,1])
            for b in arange(1,size(group_data_sorted_add[i,2],1)).reshape(-1):
                if group_data_sorted_add[i,2](b,a) >= 0:
                    fprintf(fid_sleep_12h_CT,'%f\\t',group_data_sorted_add[i,2](b,a))
                else:
                    fprintf(fid_sleep_12h_CT,'\\t')
            fprintf(fid_sleep_12h_CT,'\\n')
        for a in arange(1,size(group_data_sorted_add[i,3],2)).reshape(-1):
            fprintf(fid_distance_12h_CT,'%s\\t',group_data_sorted[i,1])
            for b in arange(1,size(group_data_sorted_add[i,3],1)).reshape(-1):
                if group_data_sorted_add[i,3](b,a) >= 0:
                    fprintf(fid_distance_12h_CT,'%f\\t',group_data_sorted_add[i,3](b,a))
                else:
                    fprintf(fid_distance_12h_CT,'\\t')
            fprintf(fid_distance_12h_CT,'\\n')
    
    fclose(fid_speed_12h_CT)
    fclose(fid_sleep_12h_CT)
    fclose(fid_distance_12h_CT)
    clear('temp_speed_30mins_CT','temp_sleep_30mins_CT','temp_food_distance_30CT','fid_speed_12h_CT','fid_sleep_12h_CT','fid_distance_12h_CT')
    #计算一天之内的sleep,speed,distance的变化。将相同CT值的取平均值
    for i in arange(1,size(group_data_sorted,1)).reshape(-1):
        temp_speed_1day=zeros(48,size(group_data_sorted[i,2],2))
# mean_SD_R.m:387
        number_1day=zeros(2,size(group_data_sorted[i,2],2))
# mean_SD_R.m:387
        temp_sleep_1day=zeros(48,size(group_data_sorted[i,2],2))
# mean_SD_R.m:388
        temp_distance_1day=zeros(48,size(group_data_sorted[i,2],2))
# mean_SD_R.m:389
        temp_speed_temp=group_data_sorted[i,2]
# mean_SD_R.m:390
        temp_speed_temp[temp_speed_temp < 0]=0
# mean_SD_R.m:390
        for j in arange(1,(size(group_data_sorted[i,2],1) / 48)).reshape(-1):
            for k in arange(1,size(group_data_sorted[i,2],2)).reshape(-1):
                if group_data_sorted[i,4](dot(j,48) - 47,k) >= 0:
                    temp_speed_1day[arange(1,24),k]=temp_speed_1day(arange(1,24),k) + temp_speed_temp(arange(dot(j,48) - 47,dot(j,48) - 24),k)
# mean_SD_R.m:394
                    temp_sleep_1day[arange(1,24),k]=temp_sleep_1day(arange(1,24),k) + group_data_sorted[i,4](arange(dot(j,48) - 47,dot(j,48) - 24),k)
# mean_SD_R.m:395
                    temp_distance_1day[arange(1,24),k]=temp_distance_1day(arange(1,24),k) + group_data_sorted[i,5](arange(dot(j,48) - 47,dot(j,48) - 24),k)
# mean_SD_R.m:396
                    number_1day[1,k]=number_1day(1,k) + 1
# mean_SD_R.m:397
                if group_data_sorted[i,4](dot(j,48) - 23,k) >= 0:
                    temp_speed_1day[arange(25,48),k]=temp_speed_1day(arange(25,48),k) + temp_speed_temp(arange(dot(j,48) - 23,dot(j,48)),k)
# mean_SD_R.m:400
                    temp_sleep_1day[arange(25,48),k]=temp_sleep_1day(arange(25,48),k) + group_data_sorted[i,4](arange(dot(j,48) - 23,dot(j,48)),k)
# mean_SD_R.m:401
                    temp_distance_1day[arange(25,48),k]=temp_distance_1day(arange(25,48),k) + group_data_sorted[i,5](arange(dot(j,48) - 23,dot(j,48)),k)
# mean_SD_R.m:402
                    number_1day[2,k]=number_1day(2,k) + 1
# mean_SD_R.m:403
        for k in arange(1,size(group_data_sorted[i,2],2)).reshape(-1):
            if number_1day(1,k) > 0:
                temp_speed_1day[arange(1,24),k]=temp_speed_1day(arange(1,24),k) / number_1day(1,k)
# mean_SD_R.m:409
                temp_sleep_1day[arange(1,24),k]=temp_sleep_1day(arange(1,24),k) / number_1day(1,k)
# mean_SD_R.m:410
                temp_distance_1day[arange(1,24),k]=temp_distance_1day(arange(1,24),k) / number_1day(1,k)
# mean_SD_R.m:411
            else:
                temp_speed_1day[arange(1,24),k]=- 1
# mean_SD_R.m:413
                temp_sleep_1day[arange(1,24),k]=- 1
# mean_SD_R.m:413
                temp_distance_1day[arange(1,24),k]=- 1
# mean_SD_R.m:413
            if number_1day(2,k) > 0:
                temp_speed_1day[arange(25,48),k]=temp_speed_1day(arange(25,48),k) / number_1day(2,k)
# mean_SD_R.m:416
                temp_sleep_1day[arange(25,48),k]=temp_sleep_1day(arange(25,48),k) / number_1day(2,k)
# mean_SD_R.m:417
                temp_distance_1day[arange(25,48),k]=temp_distance_1day(arange(25,48),k) / number_1day(2,k)
# mean_SD_R.m:418
            else:
                temp_speed_1day[arange(25,48),k]=- 1
# mean_SD_R.m:420
                temp_sleep_1day[arange(25,48),k]=- 1
# mean_SD_R.m:420
                temp_distance_1day[arange(25,48),k]=- 1
# mean_SD_R.m:420
        group_data_sorted_add[i,4]=temp_speed_1day
# mean_SD_R.m:423
        group_data_sorted_add[i,5]=temp_sleep_1day
# mean_SD_R.m:424
        group_data_sorted_add[i,6]=temp_distance_1day
# mean_SD_R.m:425
    
    clear('temp_speed_1day','temp_sleep_1day','temp_distance_1day','number_1day','temp_speed_temp')
    fid_speed_1day_CT=fopen(concat([dirPath,'\\speed_1day_CT.txt']),'w')
# mean_SD_R.m:428
    fid_sleep_1day_CT=fopen(concat([dirPath,'\\sleep_1day_CT.txt']),'w')
# mean_SD_R.m:429
    fid_distance_1day_CT=fopen(concat([dirPath,'\\distance_1day_CT.txt']),'w')
# mean_SD_R.m:430
    for i in arange(1,size(group_data_sorted,1)).reshape(-1):
        for a in arange(1,size(group_data_sorted_add[i,4],2)).reshape(-1):
            fprintf(fid_speed_1day_CT,'%s\\t',group_data_sorted[i,1])
            fprintf(fid_sleep_1day_CT,'%s\\t',group_data_sorted[i,1])
            fprintf(fid_distance_1day_CT,'%s\\t',group_data_sorted[i,1])
            for b in arange(1,size(group_data_sorted_add[i,4],1)).reshape(-1):
                if group_data_sorted_add[i,4](b,a) >= 0:
                    fprintf(fid_speed_1day_CT,'%f\\t',group_data_sorted_add[i,4](b,a))
                else:
                    fprintf(fid_speed_1day_CT,'\\t')
                if group_data_sorted_add[i,5](b,a) >= 0:
                    fprintf(fid_sleep_1day_CT,'%f\\t',group_data_sorted_add[i,5](b,a))
                else:
                    fprintf(fid_sleep_1day_CT,'\\t')
                if group_data_sorted_add[i,6](b,a) >= 0:
                    fprintf(fid_distance_1day_CT,'%f\\t',group_data_sorted_add[i,6](b,a))
                else:
                    fprintf(fid_distance_1day_CT,'\\t')
            fprintf(fid_speed_1day_CT,'\\n')
            fprintf(fid_sleep_1day_CT,'\\n')
            fprintf(fid_distance_1day_CT,'\\n')
    
    fclose(fid_speed_1day_CT)
    fclose(fid_sleep_1day_CT)
    fclose(fid_distance_1day_CT)
    clear('fid_speed_1day_CT','fid_sleep_1day_CT','fid_distance_1day_CT')
    #将12小时的数据平均之后，计算白天和黑夜的sleep,speed,distance数值
    for i in arange(1,size(group_data_sorted_add,1)).reshape(-1):
        temp_speed_halfD=zeros(2,size(group_data_sorted_add[i,4],2))
# mean_SD_R.m:460
        temp_sleep_halfD=zeros(2,size(group_data_sorted_add[i,4],2))
# mean_SD_R.m:461
        temp_distance_halfD=zeros(2,size(group_data_sorted_add[i,4],2))
# mean_SD_R.m:462
        for j in arange(1,size(group_data_sorted_add[i,4],2)).reshape(-1):
            if group_data_sorted_add[i,4](1,j) >= 0:
                temp_speed_halfD[1,j]=mean(group_data_sorted_add[i,4](arange(1,24),j),1)
# mean_SD_R.m:465
                temp_sleep_halfD[1,j]=mean(group_data_sorted_add[i,5](arange(1,24),j),1)
# mean_SD_R.m:466
                temp_distance_halfD[1,j]=mean(group_data_sorted_add[i,6](arange(1,24),j),1)
# mean_SD_R.m:467
            else:
                temp_speed_halfD[1,j]=- 1
# mean_SD_R.m:469
                temp_sleep_halfD[1,j]=- 1
# mean_SD_R.m:469
                temp_distance_halfD[1,j]=- 1
# mean_SD_R.m:469
            if group_data_sorted_add[i,4](25,j) >= 0:
                temp_speed_halfD[2,j]=mean(group_data_sorted_add[i,4](arange(25,48),j),1)
# mean_SD_R.m:472
                temp_sleep_halfD[2,j]=mean(group_data_sorted_add[i,5](arange(25,48),j),1)
# mean_SD_R.m:473
                temp_distance_halfD[2,j]=mean(group_data_sorted_add[i,6](arange(25,48),j),1)
# mean_SD_R.m:474
            else:
                temp_speed_halfD[2,j]=- 1
# mean_SD_R.m:476
                temp_sleep_halfD[2,j]=- 1
# mean_SD_R.m:476
                temp_distance_halfD[2,j]=- 1
# mean_SD_R.m:476
        group_data_sorted_add[i,7]=temp_speed_halfD
# mean_SD_R.m:479
        group_data_sorted_add[i,8]=temp_sleep_halfD
# mean_SD_R.m:480
        group_data_sorted_add[i,9]=temp_distance_halfD
# mean_SD_R.m:481
    
    clear('temp_speed_halfD','temp_sleep_halfD','temp_distance_halfD')
    fid_speed_halfD=fopen(concat([dirPath,'\\speed_halfD.txt']),'w')
# mean_SD_R.m:484
    fid_sleep_halfD=fopen(concat([dirPath,'\\sleep_halfD.txt']),'w')
# mean_SD_R.m:485
    fid_distance_halfD=fopen(concat([dirPath,'\\distance_halfD.txt']),'w')
# mean_SD_R.m:486
    for i in arange(1,size(group_data_sorted_add,1)).reshape(-1):
        for a in arange(1,size(group_data_sorted_add[i,7],2)).reshape(-1):
            fprintf(fid_speed_halfD,'%s\\t',group_data_sorted[i,1])
            fprintf(fid_sleep_halfD,'%s\\t',group_data_sorted[i,1])
            fprintf(fid_distance_halfD,'%s\\t',group_data_sorted[i,1])
            for b in arange(1,size(group_data_sorted_add[i,7],1)).reshape(-1):
                if group_data_sorted_add[i,7](b,a) >= 0:
                    fprintf(fid_speed_halfD,'%f\\t',group_data_sorted_add[i,7](b,a))
                    fprintf(fid_sleep_halfD,'%f\\t',group_data_sorted_add[i,8](b,a))
                    fprintf(fid_distance_halfD,'%f\\t',group_data_sorted_add[i,9](b,a))
                else:
                    fprintf(fid_speed_halfD,'\\t')
                    fprintf(fid_sleep_halfD,'\\t')
                    fprintf(fid_distance_halfD,'\\t')
                fprintf(fid_speed_halfD,'\\n')
                fprintf(fid_sleep_halfD,'\\n')
                fprintf(fid_distance_halfD,'\\n')
    
    fclose(fid_speed_halfD)
    fclose(fid_sleep_halfD)
    fclose(fid_distance_halfD)
    clear('fid_speed_halfD','fid_sleep_halfD','fid_distance_halfD')
    ## 5.输出品系的平均值，数量以及方差
# 需要输出的有: lineName; sleep_30mins_SD(total 24hs,30mins sum); sleep_center(12hs mean)
# sleep_30mins_CT, speed_30mins_CT, distance_30mins_CT (first day with data)
# sleep_12hs_CT, speed_12hs_CT, distance_12hs_CT
# sleep_1day_CT, speed_1day_CT, distance_1day_CT
# sleep_day_night, speed_day_night, distance_day_night
    
    #for SD, use:
# sleep_30mins_SD(total 24hs,30mins sum);  
# sleep_30mins_CT, speed_30mins_CT, distance_30mins_CT (first day with data)
    
    mean_SD_N=cell(size(group_data_sorted,6))
# mean_SD_R.m:517
    #{*,1}输出有数据的前24小时点的sleep_30mins_CT, speed_30mins_CT, distance_30mins_CT
#！错误，这样不同开始时间的点会被放到一起比较，直接输出所有前48小时的点
#{*,2}计算，sleep_30mins_SD(total 24hs,30mins sum)
#{*,3}计算 sleep_center(12hs mean)
#{*,4}计算 sleep_12hs_CT, speed_12hs_CT, distance_12hs_CT
#{*,5}计算 sleep_1day_CT, speed_1day_CT, distance_1day_CT
#{*,6}计算 sleep_day_night, speed_day_night, distance_day_night
    for i in arange(1,size(group_data_sorted)).reshape(-1):
        #     temp_start=1000;#寻找开始有数据记录的点
#     for j=1:size(group_data_sorted{i,4},2)
#      p=find(group_data_sorted{i,4}(:,j)>=0);
#      if ~isempty(p) 
#      if(p(1)<temp_start)
#        temp_start=p(1);
#      end
#      end
#     end
#   if temp_start<1000
#     temp_end=temp_start+47;#是否可用的数据>24小时，否则使用可用的数据
#     if temp_end>size(group_data_sorted{i,4},1)
#         temp_end=size(group_data_sorted{i,4},1);
#     end
#     temp_mean_SD_N=zeros(temp_end-temp_start+1,9);#speed(mean,SD,N);sleep(mean,SD,N);distance(mean,SD,N);
#     temp_speed_temp2=group_data_sorted{i,2}; temp_speed_temp2(temp_speed_temp2<0)=0;
#     for j=temp_start:temp_end
#        temp_mask=group_data_sorted{i,4}(j,:);
#        temp_line=temp_speed_temp2(j,:); temp_line_exc=temp_line(temp_mask>=0);
#        temp_mean_SD_N(j-temp_start+1,3)=size(temp_line_exc,2);temp_mean_SD_N(j-temp_start+1,1)=mean(temp_line_exc,2);temp_mean_SD_N(j-temp_start+1,2)=std(temp_line_exc,0,2);
#        temp_line=group_data_sorted{i,4}(j,:); temp_line_exc=temp_line(temp_mask>=0);
#        temp_mean_SD_N(j-temp_start+1,6)=size(temp_line_exc,2);temp_mean_SD_N(j-temp_start+1,4)=mean(temp_line_exc,2);temp_mean_SD_N(j-temp_start+1,5)=std(temp_line_exc,0,2);
#        temp_line=group_data_sorted{i,5}(j,:); temp_line_exc=temp_line(temp_mask>=0);
#        temp_mean_SD_N(j-temp_start+1,9)=size(temp_line_exc,2);temp_mean_SD_N(j-temp_start+1,7)=mean(temp_line_exc,2);temp_mean_SD_N(j-temp_start+1,8)=std(temp_line_exc,0,2);
#     end
#     mean_SD_N{i,1}=temp_mean_SD_N;
#     clear p temp_start temp_end temp_mean_SD_N temp_mask temp_line temp_line_exc temp_speed_temp2
#   else
#     mean_SD_N{i,1}=-1;
#   end
        if size(group_data_sorted[i,4],1) < 96:
            temp_end=size(group_data_sorted[i,4],1)
# mean_SD_R.m:557
        else:
            temp_end=96
# mean_SD_R.m:559
        temp_mean_SD_N=zeros(temp_end,9)
# mean_SD_R.m:561
        temp_speed_temp2=group_data_sorted[i,2]
# mean_SD_R.m:562
        temp_speed_temp2[temp_speed_temp2 < 0]=0
# mean_SD_R.m:562
        for j in arange(1,temp_end).reshape(-1):
            p=find(group_data_sorted[i,4](j,arange()) >= 0)
# mean_SD_R.m:564
            if isempty(p):
                ravel[temp_mean_SD_N]=- 1
# mean_SD_R.m:566
            else:
                temp_line=temp_speed_temp2(j,arange())
# mean_SD_R.m:568
                temp_line_exc=temp_line(p)
# mean_SD_R.m:568
                temp_mean_SD_N[j,1]=mean(temp_line_exc,2)
# mean_SD_R.m:569
                temp_mean_SD_N[j,2]=std(temp_line_exc,0,2)
# mean_SD_R.m:569
                temp_mean_SD_N[j,3]=size(temp_line_exc,2)
# mean_SD_R.m:569
                temp_line=group_data_sorted[i,4](j,arange())
# mean_SD_R.m:570
                temp_line_exc=temp_line(p)
# mean_SD_R.m:570
                temp_mean_SD_N[j,4]=mean(temp_line_exc,2)
# mean_SD_R.m:571
                temp_mean_SD_N[j,5]=std(temp_line_exc,0,2)
# mean_SD_R.m:571
                temp_mean_SD_N[j,6]=size(temp_line_exc,2)
# mean_SD_R.m:571
                temp_line=group_data_sorted[i,5](j,arange())
# mean_SD_R.m:572
                temp_line_exc=temp_line(p)
# mean_SD_R.m:572
                temp_mean_SD_N[j,7]=mean(temp_line_exc,2)
# mean_SD_R.m:573
                temp_mean_SD_N[j,8]=std(temp_line_exc,0,2)
# mean_SD_R.m:573
                temp_mean_SD_N[j,9]=size(temp_line_exc,2)
# mean_SD_R.m:573
        mean_SD_N[i,1]=temp_mean_SD_N
# mean_SD_R.m:576
        clear('p','temp_mean_SD_N','temp_line','temp_line_exc','temp_speed_temp2')
        #计算，sleep_30mins_SD(total 24hs,30mins sum)，line 180注释的，只会整个果蝇都选中，或者都不要
        p=find(group_data_sorted[i,3](1,arange()) >= 0)
# mean_SD_R.m:580
        if logical_not(isempty(p)):
            temp_matrix=group_data_sorted[i,3](arange(),p)
# mean_SD_R.m:582
            temp_mean_SD_N=zeros(48,3)
# mean_SD_R.m:583
            temp_mean_SD_N[arange(),1]=mean(temp_matrix,2)
# mean_SD_R.m:584
            temp_mean_SD_N[arange(),2]=std(temp_matrix,0,2)
# mean_SD_R.m:584
            temp_mean_SD_N[arange(),3]=size(temp_matrix,2)
# mean_SD_R.m:584
            mean_SD_N[i,2]=temp_mean_SD_N
# mean_SD_R.m:585
            clear('p','temp_matrix','temp_mean_SD_N')
        else:
            mean_SD_N[i,2]=- 1
# mean_SD_R.m:588
        #计算 sleep_center(12hs mean)
        temp_mean_SD_N=zeros(size(group_data_sorted[i,6],1),3)
# mean_SD_R.m:591
        ravel[temp_mean_SD_N]=- 1
# mean_SD_R.m:592
        for j in arange(1,size(group_data_sorted[i,6],1)).reshape(-1):
            temp_line=group_data_sorted[i,6](j,arange())
# mean_SD_R.m:594
            temp_line_exc=temp_line(group_data_sorted[i,6](j,arange()) >= 0)
# mean_SD_R.m:594
            if isempty(temp_line_exc):
                temp_mean_SD_N[j,arange()]=- 1
# mean_SD_R.m:596
            else:
                temp_mean_SD_N[j,1]=mean(temp_line_exc,2)
# mean_SD_R.m:598
                temp_mean_SD_N[j,2]=std(temp_line_exc,0,2)
# mean_SD_R.m:598
                temp_mean_SD_N[j,3]=size(temp_line_exc,2)
# mean_SD_R.m:598
        mean_SD_N[i,3]=temp_mean_SD_N
# mean_SD_R.m:601
        clear('temp_mean_SD_N','temp_line','temp_line_exc')
        #计算 sleep_12hs_CT, speed_12hs_CT, distance_12hs_CT
        temp_mean_SD_N=zeros(size(group_data_sorted_add[i,1],1),9)
# mean_SD_R.m:604
        for j in arange(1,size(group_data_sorted_add[i,1],1)).reshape(-1):
            temp_mask=group_data_sorted_add[i,2](j,arange())
# mean_SD_R.m:606
            p=find(temp_mask >= 0)
# mean_SD_R.m:607
            if isempty(p):
                temp_mean_SD_N[j,arange()]=- 1
# mean_SD_R.m:609
            else:
                temp_line=group_data_sorted_add[i,1](j,arange())
# mean_SD_R.m:611
                temp_line_exc=temp_line(p)
# mean_SD_R.m:611
                temp_mean_SD_N[j,1]=mean(temp_line_exc,2)
# mean_SD_R.m:612
                temp_mean_SD_N[j,2]=std(temp_line_exc,0,2)
# mean_SD_R.m:612
                temp_mean_SD_N[j,3]=size(temp_line_exc,2)
# mean_SD_R.m:612
                temp_line=group_data_sorted_add[i,2](j,arange())
# mean_SD_R.m:613
                temp_line_exc=temp_line(p)
# mean_SD_R.m:613
                temp_mean_SD_N[j,4]=mean(temp_line_exc,2)
# mean_SD_R.m:614
                temp_mean_SD_N[j,5]=std(temp_line_exc,0,2)
# mean_SD_R.m:614
                temp_mean_SD_N[j,6]=size(temp_line_exc,2)
# mean_SD_R.m:614
                temp_line=group_data_sorted_add[i,3](j,arange())
# mean_SD_R.m:615
                temp_line_exc=temp_line(p)
# mean_SD_R.m:615
                temp_mean_SD_N[j,7]=mean(temp_line_exc,2)
# mean_SD_R.m:616
                temp_mean_SD_N[j,8]=std(temp_line_exc,0,2)
# mean_SD_R.m:616
                temp_mean_SD_N[j,9]=size(temp_line_exc,2)
# mean_SD_R.m:616
        mean_SD_N[i,4]=temp_mean_SD_N
# mean_SD_R.m:619
        clear('temp_mask','p','temp_mean_SD_N','temp_line','temp_line_exc')
        #计算 sleep_1day_CT, speed_1day_CT, distance_1day_CT
        temp_mean_SD_N=zeros(size(group_data_sorted_add[i,4],1),9)
# mean_SD_R.m:622
        for j in arange(1,size(group_data_sorted_add[i,4],1)).reshape(-1):
            temp_mask=group_data_sorted_add[i,5](j,arange())
# mean_SD_R.m:624
            p=find(temp_mask >= 0)
# mean_SD_R.m:625
            if isempty(p):
                temp_mean_SD_N[j,arange()]=- 1
# mean_SD_R.m:627
            else:
                temp_line=group_data_sorted_add[i,4](j,arange())
# mean_SD_R.m:629
                temp_line_exc=temp_line(p)
# mean_SD_R.m:629
                temp_mean_SD_N[j,1]=mean(temp_line_exc,2)
# mean_SD_R.m:630
                temp_mean_SD_N[j,2]=std(temp_line_exc,0,2)
# mean_SD_R.m:630
                temp_mean_SD_N[j,3]=size(temp_line_exc,2)
# mean_SD_R.m:630
                temp_line=group_data_sorted_add[i,5](j,arange())
# mean_SD_R.m:631
                temp_line_exc=temp_line(p)
# mean_SD_R.m:631
                temp_mean_SD_N[j,4]=mean(temp_line_exc,2)
# mean_SD_R.m:632
                temp_mean_SD_N[j,5]=std(temp_line_exc,0,2)
# mean_SD_R.m:632
                temp_mean_SD_N[j,6]=size(temp_line_exc,2)
# mean_SD_R.m:632
                temp_line=group_data_sorted_add[i,6](j,arange())
# mean_SD_R.m:633
                temp_line_exc=temp_line(p)
# mean_SD_R.m:633
                temp_mean_SD_N[j,7]=mean(temp_line_exc,2)
# mean_SD_R.m:634
                temp_mean_SD_N[j,8]=std(temp_line_exc,0,2)
# mean_SD_R.m:634
                temp_mean_SD_N[j,9]=size(temp_line_exc,2)
# mean_SD_R.m:634
        mean_SD_N[i,5]=temp_mean_SD_N
# mean_SD_R.m:637
        clear('temp_mask','p','temp_mean_SD_N','temp_line','temp_line_exc')
        #{*,6}计算 sleep_day_night, speed_day_night, distance_day_night
        temp_mean_SD_N=zeros(size(group_data_sorted_add[i,4],1),9)
# mean_SD_R.m:640
        for j in arange(1,size(group_data_sorted_add[i,7],1)).reshape(-1):
            temp_mask=group_data_sorted_add[i,8](j,arange())
# mean_SD_R.m:642
            p=find(temp_mask >= 0)
# mean_SD_R.m:643
            if isempty(p):
                temp_mean_SD_N[j,arange()]=- 1
# mean_SD_R.m:645
            else:
                temp_line=group_data_sorted_add[i,7](j,arange())
# mean_SD_R.m:647
                temp_line_exc=temp_line(p)
# mean_SD_R.m:647
                temp_mean_SD_N[j,1]=mean(temp_line_exc,2)
# mean_SD_R.m:648
                temp_mean_SD_N[j,2]=std(temp_line_exc,0,2)
# mean_SD_R.m:648
                temp_mean_SD_N[j,3]=size(temp_line_exc,2)
# mean_SD_R.m:648
                temp_line=group_data_sorted_add[i,8](j,arange())
# mean_SD_R.m:649
                temp_line_exc=temp_line(p)
# mean_SD_R.m:649
                temp_mean_SD_N[j,4]=mean(temp_line_exc,2)
# mean_SD_R.m:650
                temp_mean_SD_N[j,5]=std(temp_line_exc,0,2)
# mean_SD_R.m:650
                temp_mean_SD_N[j,6]=size(temp_line_exc,2)
# mean_SD_R.m:650
                temp_line=group_data_sorted_add[i,9](j,arange())
# mean_SD_R.m:651
                temp_line_exc=temp_line(p)
# mean_SD_R.m:651
                temp_mean_SD_N[j,7]=mean(temp_line_exc,2)
# mean_SD_R.m:652
                temp_mean_SD_N[j,8]=std(temp_line_exc,0,2)
# mean_SD_R.m:652
                temp_mean_SD_N[j,9]=size(temp_line_exc,2)
# mean_SD_R.m:652
        mean_SD_N[i,6]=temp_mean_SD_N
# mean_SD_R.m:655
        clear('temp_mask','p','temp_mean_SD_N','temp_line','temp_line_exc')
    
    #{*,1}输出有数据的前24小时点的sleep_30mins_CT, speed_30mins_CT, distance_30mins_CT
#！错误，这样不同开始时间的点会被放到一起比较，直接输出所有前48小时的点
#{*,2}计算，sleep_30mins_SD(total 24hs,30mins sum)
#{*,3}计算 sleep_center(12hs mean)
#{*,4}计算 sleep_12hs_CT, speed_12hs_CT, distance_12hs_CT
#{*,5}计算 sleep_1day_CT, speed_1day_CT, distance_1day_CT
#{*,6}计算 sleep_day_night, speed_day_night, distance_day_night
    tempMatrix1=zeros(48,9)
# mean_SD_R.m:666
    tempMatrix2=zeros(48,3)
# mean_SD_R.m:666
    ravel[tempMatrix1]=- 1
# mean_SD_R.m:667
    ravel[tempMatrix2]=- 1
# mean_SD_R.m:667
    for i in arange(1,size(mean_SD_N,1)).reshape(-1):
        if (size(mean_SD_N[i,1],1) == 1):
            mean_SD_N[i,1]=tempMatrix1
# mean_SD_R.m:670
        if (size(mean_SD_N[i,2],1) == 1):
            mean_SD_N[i,2]=tempMatrix2
# mean_SD_R.m:673
    
    clear('tempMatrix1','tempMatrix2')
    dirPathMean=concat([dirPath,'\\Mean_data'])
# mean_SD_R.m:677
    mkdir(dirPathMean)
    mean_sleep_30mins_CT=fopen(concat([dirPathMean,'\\mean_sleep_30mins_CT.txt']),'w')
# mean_SD_R.m:679
    mean_speed_30mins_CT=fopen(concat([dirPathMean,'\\mean_speed_30mins_CT.txt']),'w')
# mean_SD_R.m:680
    mean_distance_30mins_CT=fopen(concat([dirPathMean,'\\mean_distance_30mins_CT.txt']),'w')
# mean_SD_R.m:681
    mean_sleep_30mins_SD=fopen(concat([dirPathMean,'\\mean_sleep_30mins_SD.txt']),'w')
# mean_SD_R.m:682
    mean_sleep_center=fopen(concat([dirPathMean,'\\mean_sleep_center.txt']),'w')
# mean_SD_R.m:683
    mean_sleep_12hs_CT=fopen(concat([dirPathMean,'\\mean_sleep_12hs_CT.txt']),'w')
# mean_SD_R.m:684
    mean_speed_12hs_CT=fopen(concat([dirPathMean,'\\mean_speed_12hs_CT.txt']),'w')
# mean_SD_R.m:685
    mean_distance_12hs_CT=fopen(concat([dirPathMean,'\\mean_distance_12hs_CT.txt']),'w')
# mean_SD_R.m:686
    mean_sleep_1day_CT=fopen(concat([dirPathMean,'\\mean_sleep_1day_CT.txt']),'w')
# mean_SD_R.m:687
    mean_speed_1day_CT=fopen(concat([dirPathMean,'\\mean_speed_1day_CT.txt']),'w')
# mean_SD_R.m:688
    mean_distance_1day_CT=fopen(concat([dirPathMean,'\\mean_distance_1day_CT.txt']),'w')
# mean_SD_R.m:689
    mean_sleep_day_night=fopen(concat([dirPathMean,'\\mean_sleep_day_night.txt']),'w')
# mean_SD_R.m:690
    mean_speed_day_night=fopen(concat([dirPathMean,'\\mean_speed_day_night.txt']),'w')
# mean_SD_R.m:691
    mean_distance_day_night=fopen(concat([dirPathMean,'\\mean_distance_day_night.txt']),'w')
# mean_SD_R.m:692
    for i in arange(1,size(mean_SD_N,1)).reshape(-1):
        fprintf(mean_sleep_30mins_CT,'%s\\t',group_data_sorted[i,1])
        fprintf(mean_speed_30mins_CT,'%s\\t',group_data_sorted[i,1])
        fprintf(mean_distance_30mins_CT,'%s\\t',group_data_sorted[i,1])
        fprintf(mean_sleep_30mins_SD,'%s\\t',group_data_sorted[i,1])
        fprintf(mean_sleep_1day_CT,'%s\\t',group_data_sorted[i,1])
        fprintf(mean_speed_1day_CT,'%s\\t',group_data_sorted[i,1])
        fprintf(mean_distance_1day_CT,'%s\\t',group_data_sorted[i,1])
        fprintf(mean_sleep_day_night,'%s\\t',group_data_sorted[i,1])
        fprintf(mean_speed_day_night,'%s\\t',group_data_sorted[i,1])
        fprintf(mean_distance_day_night,'%s\\t',group_data_sorted[i,1])
        for a in arange(1,3).reshape(-1):
            for b in arange(1,size(mean_SD_N[i,1],1)).reshape(-1):
                fprintf(mean_sleep_30mins_CT,'%f\\t',mean_SD_N[i,1](b,a + 3))
                fprintf(mean_speed_30mins_CT,'%f\\t',mean_SD_N[i,1](b,a))
                fprintf(mean_distance_30mins_CT,'%f\\t',mean_SD_N[i,1](b,a + 6))
            for b in arange(1,48).reshape(-1):
                fprintf(mean_sleep_30mins_SD,'%f\\t',mean_SD_N[i,2](b,a))
                fprintf(mean_sleep_1day_CT,'%f\\t',mean_SD_N[i,5](b,a + 3))
                fprintf(mean_speed_1day_CT,'%f\\t',mean_SD_N[i,5](b,a))
                fprintf(mean_distance_1day_CT,'%f\\t',mean_SD_N[i,5](b,a + 6))
                fprintf(mean_sleep_day_night,'%f\\t',mean_SD_N[i,6](b,a + 3))
                fprintf(mean_speed_day_night,'%f\\t',mean_SD_N[i,6](b,a))
                fprintf(mean_distance_day_night,'%f\\t',mean_SD_N[i,6](b,a + 6))
        fprintf(mean_sleep_30mins_CT,'\\n')
        fprintf(mean_speed_30mins_CT,'\\n')
        fprintf(mean_distance_30mins_CT,'\\n')
        fprintf(mean_sleep_30mins_SD,'\\n')
        fprintf(mean_sleep_1day_CT,'\\n')
        fprintf(mean_speed_1day_CT,'\\n')
        fprintf(mean_distance_1day_CT,'\\n')
        fprintf(mean_sleep_day_night,'\\n')
        fprintf(mean_speed_day_night,'\\n')
        fprintf(mean_distance_day_night,'\\n')
        fprintf(mean_sleep_center,'%s\\t',group_data_sorted[i,1])
        for a in arange(1,3).reshape(-1):
            for b in arange(1,size(mean_SD_N[i,3],1)).reshape(-1):
                fprintf(mean_sleep_center,'%f\\t',mean_SD_N[i,3](b,a))
        fprintf(mean_sleep_center,'\\n')
        fprintf(mean_sleep_12hs_CT,'%s\\t',group_data_sorted[i,1])
        fprintf(mean_speed_12hs_CT,'%s\\t',group_data_sorted[i,1])
        fprintf(mean_distance_12hs_CT,'%s\\t',group_data_sorted[i,1])
        for a in arange(1,3).reshape(-1):
            for b in arange(1,size(mean_SD_N[i,4],1)).reshape(-1):
                fprintf(mean_sleep_12hs_CT,'%f\\t',mean_SD_N[i,4](b,a + 3))
                fprintf(mean_speed_12hs_CT,'%f\\t',mean_SD_N[i,4](b,a))
                fprintf(mean_distance_12hs_CT,'%f\\t',mean_SD_N[i,4](b,a + 6))
        fprintf(mean_sleep_12hs_CT,'\\n')
        fprintf(mean_speed_12hs_CT,'\\n')
        fprintf(mean_distance_12hs_CT,'\\n')
    
    fclose(mean_sleep_30mins_CT)
    fclose(mean_speed_30mins_CT)
    fclose(mean_distance_30mins_CT)
    fclose(mean_sleep_30mins_SD)
    fclose(mean_sleep_center)
    fclose(mean_sleep_12hs_CT)
    fclose(mean_speed_12hs_CT)
    fclose(mean_distance_12hs_CT)
    fclose(mean_sleep_1day_CT)
    fclose(mean_speed_1day_CT)
    fclose(mean_distance_1day_CT)
    fclose(mean_sleep_day_night)
    fclose(mean_speed_day_night)
    fclose(mean_distance_day_night)