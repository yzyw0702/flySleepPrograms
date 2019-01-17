# Generated with SMOP  0.41
from libsmop import *
# main_SD_R.m

    #����ڣ�20140407-09ȫ���ر���
    
    #��Ҫ���²��ļ�����ͬĿ¼�洢��txt.speed, txt.location,
#txt.order�����ļ�:����txt.speed�Լ�txt.locationΪ��������Զ����ɣ�
#txt.orderΪλ��-Ʒϵ��Ϣ
    
    #��Ҫ��ѡ����ļ�������config_time.txt�ļ�: ��¼��ҹ������Ϣ��һ��ֻ������ͬһ��config_time.txtʱ������ļ���ʱ���᲻Ҫ����ʵ��¼������ʱ��
    
    #ʹ�õ���ֵΪ����5mins speed=0��¼Ϊsleep,�м������κ���Ŀ��<=2frames(2secs)������speed��Ϊ0��ȱ��
#���ȱ����������������������ʱ��������>=5mins֮��ſ���ȥ��������
#Ĭ�Ϸ����ӵ�һ���㿪ʼ��������Ŀ,�����Ҫ�޸ģ��봦���ʱ�������ʼ�����ʱ��
    
    #�����Ҫ����ĳһ���ļ��Ľ��������ʱ�����ļ��е�txt.speed����չ���޸�Ϊ��Ķ������������Ը��ļ��Լ�������.location�Լ�.order
    
    #Ϊ����ȷ�ļ������ʳ���λ�ã�¼����Ҫ����һ��������1,ʳ���ڰ��ӵ��м�; 2,���еĹ��Ӷ�Ϊƽ�л��ߴ�ֱ����; 3,ÿһ�����ӵ����Ҷ�����������һ������ʹ�õĹ���
    
    #����ļ���raw plot.jpeg; config_flys.txt����У�������Ĺ�Ӭ, report.txt��¼�������б���,
#'time'_main_SD_R_imported_speed.mat��¼�����.speed���ݺϼ�;
#'time'_main_SD_R_imported_location.mat��¼�����.location���ݺϼ�
#'time'_main_SD_R.mat��¼�����.order����,�Լ��м����ı�������������һ��cell��˵��
#���Ƶ�ʱ��ΪCT 1-720, �ڵƵ�ʱ��ΪCT 721-1440
    
    ## �����һ�μ��㻺��
    clear
    clc
    ##  ¼��������Ϣ, ��һ��������õ�������CT_time_list,import_data_Complex(import_data_Complex_speed,import_data_Complex_location,import_data_Complex_order),
    dirPath=uigetdir('','\xce\xc4\xbc\xfe\xbc\xd0\xc2\xb7\xbe\xb6')
# main_SD_R.m:27
    dirName=regexp(dirPath,'\\','split')
# main_SD_R.m:28
    outputDir=dirName[end()]
# main_SD_R.m:28
    mkdir(outputDir)
    clear('dirName')
    process_report=fopen(concat([outputDir,'\\report.txt']),'w')
# main_SD_R.m:29
    
    speedList=getAllFiles(dirPath,'*.speed',1)
# main_SD_R.m:30
    locationList=cell(size(speedList))
# main_SD_R.m:31
    orderList=cell(size(speedList))
# main_SD_R.m:32
    for i in arange(1,size(speedList,1)).reshape(-1):
        orderList[i]=concat([speedList[i](arange(1,end() - 9)),'txt.order'])
# main_SD_R.m:34
        locationList[i]=concat([speedList[i](arange(1,end() - 9)),'txt.location'])
# main_SD_R.m:35
    
    #¼��ʱ����Ϣ,����config_time_M��¼ʱ��˳��
    file_config_time=concat([dirPath,'\\config_time.txt'])
# main_SD_R.m:38
    fid_config_time=fopen(file_config_time)
# main_SD_R.m:38
    fprintf(process_report,'%s\\n','...\xb7\xa2\xcf\xd6\xcb\xf9\xd3\xd0\xb1\xd8\xd0\xe8\xce\xc4\xbc\xfe')
    fprintf('%s\\n','...\xb7\xa2\xcf\xd6\xcb\xf9\xd3\xd0\xb1\xd8\xd0\xe8\xce\xc4\xbc\xfe')
    config_time_C=textscan(fid_config_time,'%d%d%d')
# main_SD_R.m:40
    for i in arange(1,3).reshape(-1):
        config_time_M[arange(),i]=config_time_C[i]
# main_SD_R.m:42
    
    fclose(fid_config_time)
    clear('file_config_time','fid_config_time','config_time_C')
    fprintf(process_report,'%s\\n','...\xca\xb1\xbc\xe4\xce\xc4\xbc\xfe\xd5\xfd\xb3\xa3\xbc\xd3\xd4\xd8')
    fprintf('%s\\n','...\xca\xb1\xbc\xe4\xce\xc4\xbc\xfe\xd5\xfd\xb3\xa3\xbc\xd3\xd4\xd8')
    #¼�����е�.speed�Լ�.location��.order�ļ�
#import_data_Complex=cell(size(speedList,1),3);#for txt.speed/{*,1}, txt.location/{*,2}, txt.order/{*,3}
    import_data_Complex_speed=cell(size(speedList,1),1)
# main_SD_R.m:49
    import_data_Complex_location=cell(size(speedList,1),1)
# main_SD_R.m:50
    import_data_Complex_order=cell(size(speedList,1),1)
# main_SD_R.m:51
    #Ϊ��Լ�ռ䣬��Ϊ����
    for i in arange(1,size(speedList)).reshape(-1):
        import_data_Complex_speed[i,1]=importdata(speedList[i])
# main_SD_R.m:54
        import_data_Complex_order[i,1]=raw_input_order(orderList[i])
# main_SD_R.m:55
        fprintf('%s%d\\n','\xcd\xea\xb3\xc9\xbc\xd3\xd4\xd8\xce\xc4\xbc\xfe:',i)
    
    #���ʱ���ļ��Ƿ��д���,����CT_time_list�Լ�min_time_length
    if config_time_M(1,1) != 1:
        error('time_config should start from min 1')
    
    for i in arange(2,size(config_time_M,1)).reshape(-1):
        if config_time_M(i,2) - config_time_M(i,1) > 719:
            error(concat(['time ',num2str(i),' exceed max duration of 720mins,please check time_config again']))
        if config_time_M(i,1) - config_time_M(i - 1,2) != 1:
            error(concat(['time ',num2str(i),' not continue, please check time_config again']))
    
    temp_time_duration=zeros(size(speedList,1) + 1,1)
# main_SD_R.m:70
    temp_time_duration[end(),1]=config_time_M(end(),2)
# main_SD_R.m:70
    for i in arange(1,size(speedList)).reshape(-1):
        temp_time_duration[i,1]=floor(size(import_data_Complex_speed[i,1],1) / 60)
# main_SD_R.m:72
    
    min_time_length=min(temp_time_duration)
# main_SD_R.m:74
    fprintf(process_report,'%s\\t%d\\n','...\xca\xb1\xbc\xe4\xce\xc4\xbc\xfe\xbc\xec\xb2\xe9\xcd\xea\xb1\xcf,\xbf\xc9\xd3\xc3\xca\xb1\xbc\xe4\xb3\xa4\xb6\xc8\xce\xaa:',min_time_length)
    fprintf('%s\\n','...\xca\xb1\xbc\xe4\xce\xc4\xbc\xfe\xbc\xec\xb2\xe9\xcd\xea\xb1\xcf')
    #����CT_time list
#��ǰ��죬����
    CT_time_list_temp=zeros(min_time_length,2)
# main_SD_R.m:78
    
    for i in arange(1,size(config_time_M,1)).reshape(-1):
        CT_time_list_temp[arange(config_time_M(i,1),config_time_M(i,2)),1]=config_time_M(i,3)
# main_SD_R.m:80
    
    #���CT time /mins
#���Ƶ�ʱ��ΪCT 1-720, �ڵƵ�ʱ��ΪCT 721-1440
#Ĭ�����ھ�Ϊ720���ӣ���һ��Ƭ�����ս���ʱ����ǰ�ƣ�������Ƭ�ξ����տ�ʼʱ��������
    if config_time_M(1,3) == 0:
        CT_time_list_temp[arange(config_time_M(1,1),config_time_M(1,2)),2]=(arange((1440 - (config_time_M(1,2) - config_time_M(1,1))),1440))
# main_SD_R.m:86
    else:
        CT_time_list_temp[arange(config_time_M(1,1),config_time_M(1,2)),2]=(arange((720 - (config_time_M(1,2) - config_time_M(1,1))),720))
# main_SD_R.m:88
    
    for i in arange(2,size(config_time_M,1)).reshape(-1):
        if config_time_M(i,3) == 0:
            CT_time_list_temp[arange(config_time_M(i,1),config_time_M(i,2)),2]=(arange(721,(721 + (config_time_M(i,2) - config_time_M(i,1)))))
# main_SD_R.m:92
        else:
            CT_time_list_temp[arange(config_time_M(i,1),config_time_M(i,2)),2]=(arange(1,(1 + (config_time_M(i,2) - config_time_M(i,1)))))
# main_SD_R.m:94
    
    if min_time_length < size(CT_time_list_temp,1):
        CT_time_list=zeros(min_time_length,2)
# main_SD_R.m:98
        CT_time_list[arange(1,end()),arange()]=CT_time_list_temp(arange(1,size(CT_time_list,1)),arange())
# main_SD_R.m:99
    else:
        CT_time_list=copy(CT_time_list_temp)
# main_SD_R.m:101
    
    clear('CT_time_list_temp')
    fprintf('%s\\n','...CT\xce\xc4\xbc\xfe\xc9\xfa\xb3\xc9')
    clear('temp_time_duration')
    #���õ������У� CT_time_list ((*,1)Ϊ0,1���;(*,2)ΪCTʱ����); import_data_Complex, config_time_M, min_time_length,
#outputDir, dirPath, speedList, locationList, orderList, 
## ����.speed �ļ������ sleep_matrix, sleep_mins, sleep_30mins(sleep_30mins_SD & sleep_30mins_CT)
#��� sleep_matrix ���ݣ�ʹ�õ���ֵΪ5mins����speed=0; sleep_matrix�������ڼ���sleep_bout�������
    sleep_matrix=cell(size(speedList,1),1)
# main_SD_R.m:110
    for i in arange(1,size(speedList,1)).reshape(-1):
        temp_speed_matrix=import_data_Complex_speed[i,1]
# main_SD_R.m:112
        temp_speed_matrix_1=zeros(size(temp_speed_matrix))
# main_SD_R.m:113
        temp_speed_matrix_1[temp_speed_matrix <= 0]=1
# main_SD_R.m:114
        temp_speed_matrix_1=logical(temp_speed_matrix_1)
# main_SD_R.m:115
        time_mask_denoize=strel('line',1,90)
# main_SD_R.m:116
        time_mask=strel('line',dot(5,60),90)
# main_SD_R.m:117
        speed_data_logic_2=imopen(temp_speed_matrix_1,time_mask)
# main_SD_R.m:118
        sleep_matrix[i,1]=imclose(speed_data_logic_2,time_mask_denoize)
# main_SD_R.m:119
    
    fprintf(process_report,'%s\\n','...sleep_matrix\xbc\xc6\xcb\xe3\xcd\xea\xb1\xcf')
    fprintf('%s\\n','...sleep_matrix\xbc\xc6\xcb\xe3\xcd\xea\xb1\xcf')
    clear('temp_speed_matrix','temp_speed_matrix_1','time_mask_denoize','time_mask','speed_data_logic_2')
    #���ÿ����˯��ʱ��,sleep_mins, 60��������ݺϲ�;
    sleep_mins=cell(size(speedList,1),1)
# main_SD_R.m:124
    for i in arange(1,size(speedList,1)).reshape(-1):
        temp_sleep_matrix=sleep_matrix[i,1]
# main_SD_R.m:126
        temp_min_sleep_matrix=zeros(min_time_length,size(temp_sleep_matrix,2))
# main_SD_R.m:127
        for j in arange(1,min_time_length).reshape(-1):
            temp_min_sleep_matrix[j,arange()]=sum(temp_sleep_matrix(arange(dot(j,60) - 59,dot(j,60)),arange()),1)
# main_SD_R.m:129
        sleep_mins[i,1]=temp_min_sleep_matrix
# main_SD_R.m:131
    
    fprintf(process_report,'%s\\n','...sleep_mins \xbc\xc6\xcb\xe3\xcd\xea\xb1\xcf')
    fprintf('%s\\n','...sleep_mins \xbc\xc6\xcb\xe3\xcd\xea\xb1\xcf')
    clear('temp_sleep_matrix','temp_min_sleep_matrix')
    #����ÿ30mins��˯��ʱ�����ֱ���CTʱ�仮��30mins(normal sleep ����)�Լ�����¼��ʼÿ30mins����(SD sleep rebount)
#sleep_30mins_SD: max calculated length 24hours
#��ɸѡ��ʵ���У������ֵ�ǲ���ʹ�õģ���Ϊcontrol��Ӭ��SD��Ӭ������ͬʱ��ʼ¼��ģ���Ҫʹ��CT��У��
    sleep_30mins_SD=cell(size(speedList,1),1)
# main_SD_R.m:138
    sleep_30mins_SD_length=48
# main_SD_R.m:139
    if min_time_length < 1440:
        sleep_30mins_SD_length=floor(min_time_length / 30)
# main_SD_R.m:141
    
    for i in arange(1,size(speedList,1)).reshape(-1):
        sleep_30SD=sleep_mins[i,1]
# main_SD_R.m:144
        sleep_30SD_temp=zeros(sleep_30mins_SD_length,size(sleep_30SD,2))
# main_SD_R.m:145
        for j in arange(1,sleep_30mins_SD_length).reshape(-1):
            sleep_30SD_temp[j,arange()]=sum(sleep_30SD(arange(dot(j,30) - 29,dot(j,30)),arange()),1)
# main_SD_R.m:147
        sleep_30mins_SD[i,1]=sleep_30SD_temp
# main_SD_R.m:149
    
    fprintf(process_report,'%s\\n','...sleep_30mins_SD \xbc\xc6\xcb\xe3\xcd\xea\xb1\xcf')
    fprintf('%s\\n','...sleep_30mins_SD \xbc\xc6\xcb\xe3\xcd\xea\xb1\xcf')
    clear('sleep_30mins_SD_length','sleep_30SD','sleep_30SD_temp')
    #sleep_30mins_CT,����CT����,��һ��ʱ�����<30mins�����Զ�����
    sleep_30mins_CT=cell(size(speedList,1),1)
# main_SD_R.m:154
    sleep_30CT_days=1
# main_SD_R.m:155
    
    if config_time_M(1,3) == 0:
        sleep_30CT_days=sleep_30CT_days + ceil((size(config_time_M,1) - 1) / 2)
# main_SD_R.m:157
    else:
        sleep_30CT_days=sleep_30CT_days + ceil((size(config_time_M,1) - 2) / 2)
# main_SD_R.m:159
    
    for i in arange(1,size(speedList,1)).reshape(-1):
        sleep_30CT=sleep_mins[i,1]
# main_SD_R.m:162
        sleep_30CT_temp=zeros(dot(sleep_30CT_days,48),size(sleep_30CT,2))
# main_SD_R.m:163
        ravel[sleep_30CT_temp]=- 1
# main_SD_R.m:164
        sleep_30CT_point=ceil(CT_time_list(1,2) / 30)
# main_SD_R.m:165
        sleep_30CT_temp2=zeros(1,size(sleep_30CT,2))
# main_SD_R.m:166
        for j in arange(1,size(sleep_30CT,1)).reshape(-1):
            sleep_30CT_temp2=sleep_30CT_temp2 + sleep_30CT(j,arange())
# main_SD_R.m:168
            if mod(CT_time_list(j,2),30) == 0:
                sleep_30CT_temp[sleep_30CT_point,arange()]=sleep_30CT_temp2
# main_SD_R.m:170
                sleep_30CT_point=sleep_30CT_point + 1
# main_SD_R.m:171
                ravel[sleep_30CT_temp2]=0
# main_SD_R.m:172
        sleep_30CT_point=ceil(CT_time_list(1,2) / 30)
# main_SD_R.m:175
        if mod((CT_time_list(1,2) - 1),30) != 0:
            sleep_30CT_temp[sleep_30CT_point,arange()]=- 1
# main_SD_R.m:177
        sleep_30mins_CT[i,1]=sleep_30CT_temp
# main_SD_R.m:179
    
    fprintf(process_report,'%s\\n','...sleep_30mins_CT \xbc\xc6\xcb\xe3\xcd\xea\xb1\xcf')
    fprintf('%s\\n','...sleep_30mins_CT \xbc\xc6\xcb\xe3\xcd\xea\xb1\xcf')
    clear('sleep_30CT_days','sleep_30CT','sleep_30CT_temp2','sleep_30CT_temp','sleep_30CT_point')
    #���õ������� sleep_matrix(�ж�ÿһ���Ƿ���˯��); sleep_minsΪÿһ����˯�����ݣ�����������jpeg raw sleepͼ
#sleep_30mins_SD ����¼��ʼÿ30mins����(SD sleep rebount),  sleep_30mins_CT ����CTʱ�仮��30mins(normal sleep ����)
## ����.speed ���ݣ������˶��ٶ�,����ÿ���Ӻϲ����Լ�ÿ30mins�ϲ�
# ��speed ���ݾ������룬��Ϊtrace������ʱ������������һ���������ֵ��������ʱ��������speed>=10 �� point��
    speed_matrix=cell(size(sleep_matrix,1),1)
# main_SD_R.m:187
    
    for i in arange(1,size(speedList,1)).reshape(-1):
        speed_matrix_temp=import_data_Complex_speed[i,1]
# main_SD_R.m:189
        speed_matrix_temp[sleep_matrix[i,1] == 1]=- 1
# main_SD_R.m:190
        speed_matrix_temp[speed_matrix_temp >= 10]=- 2
# main_SD_R.m:191
        speed_matrix[i,1]=speed_matrix_temp
# main_SD_R.m:192
    
    fprintf(process_report,'%s\\n','...speed_matrix \xbc\xc6\xcb\xe3\xcd\xea\xb1\xcf')
    fprintf('%s\\n','...speed_matrix \xbc\xc6\xcb\xe3\xcd\xea\xb1\xcf')
    clear('speed_matrix_temp')
    #����CT time����30mins֮��speed��ƽ��ֵ
    speed_30mins_CT=cell(size(sleep_matrix,1),1)
# main_SD_R.m:197
    for i in arange(1,size(speedList,1)).reshape(-1):
        speed_30CT=speed_matrix[i,1]
# main_SD_R.m:199
        speed_30CT[speed_matrix[i,1] < 0]=0
# main_SD_R.m:199
        speed_time_30CT=zeros(size(speed_30CT))
# main_SD_R.m:200
        speed_time_30CT[speed_matrix[i,1] >= 0]=1
# main_SD_R.m:200
        speed_30CT_temp=zeros(size(sleep_30mins_CT[i,1]))
# main_SD_R.m:201
        ravel[speed_30CT_temp]=- 1
# main_SD_R.m:202
        speed_30CT_point=ceil(CT_time_list(1,2) / 30)
# main_SD_R.m:203
        speed_30CT_temp2=zeros(1,size(speed_30CT,2))
# main_SD_R.m:204
        speed_30CT_temp3=zeros(1,size(speed_30CT,2))
# main_SD_R.m:205
        for j in arange(1,dot(min_time_length,60)).reshape(-1):
            speed_30CT_temp2=speed_30CT_temp2 + speed_30CT(j,arange())
# main_SD_R.m:207
            speed_30CT_temp3=speed_30CT_temp3 + speed_time_30CT(j,arange())
# main_SD_R.m:208
            if mod(CT_time_list(ceil(j / 60),2),30) == 0 and mod(j,60) == 0:
                for k in arange(1,size(speed_30CT_temp2,2)).reshape(-1):
                    if speed_30CT_temp3(1,k) > 0:
                        speed_30CT_temp[speed_30CT_point,k]=speed_30CT_temp2(1,k) / speed_30CT_temp3(1,k)
# main_SD_R.m:212
                    else:
                        speed_30CT_temp[speed_30CT_point,k]=- 1
# main_SD_R.m:214
                speed_30CT_point=speed_30CT_point + 1
# main_SD_R.m:217
                ravel[speed_30CT_temp2]=0
# main_SD_R.m:218
                ravel[speed_30CT_temp3]=0
# main_SD_R.m:218
        speed_30CT_point=ceil(CT_time_list(1,2) / 30)
# main_SD_R.m:221
        if mod((CT_time_list(1,2) - 1),30) != 0:
            speed_30CT_temp[speed_30CT_point,arange()]=- 1
# main_SD_R.m:223
        speed_30mins_CT[i,1]=speed_30CT_temp
# main_SD_R.m:225
        fprintf('%s\\t%d\\n','...speed_30mins_CT \xbc\xc6\xcb\xe3\xcd\xea\xb1\xcf,\xb5\xda:',i)
    
    fprintf(process_report,'%s\\n','...speed_30mins_CT \xc8\xab\xb2\xbf\xbc\xc6\xcb\xe3\xcd\xea\xb1\xcf')
    fprintf('%s\\n','...speed_30mins_CT \xc8\xab\xb2\xbf\xbc\xc6\xcb\xe3\xcd\xea\xb1\xcf')
    #mat_file_path=[outputDir,'\',datestr(now,30),'_main_SD_R_imported_speed.mat'];
    mat_file_path=concat([outputDir,'\\main_SD_R_imported_speed.mat'])
# main_SD_R.m:231
    save(mat_file_path,'import_data_Complex_speed','-v7.3')
    
    clear('speed_30CT','speed_time_30CT','speed_30CT_temp','speed_30CT_point','speed_30CT_temp2','speed_30CT_temp3','import_data_Complex_speed','mat_file_path')
    #���õ�������: speed_matrix; speed_30mins_CT;
## ����.location ���ݣ�����λ�þ���ʳ��ľ���
#20140422�޸ģ���������ʳ��λ�ã������Ŀ¼����"mark.txt"�������ݼ�¼�����������򲻽���������Ĭ��ʳ�������룬��ֻ��һ�����
#Ѱ�ҵ�first movement��ʱ���.һ��ʼû��movement��ʱ��locationΪĬ��λ��(0,0)
    for i in arange(1,size(speedList)).reshape(-1):
        import_data_Complex_location[i,1]=importdata(locationList[i])
# main_SD_R.m:239
        fprintf('%s%d\\n','\xcd\xea\xb3\xc9\xbc\xd3\xd4\xd8\xce\xbb\xd6\xc3\xce\xc4\xbc\xfe:',i)
    
    # for i=1:size(speedList)
#     if size(import_data_Complex_speed{i,1},1)~=size(import_data_Complex_location{i,1},1)
#         error(['time ',num2str(i),' .speed & .location length not match, please check original file again']);
#     end
#     if 2*size(import_data_Complex_speed{i,1},2)~=size(import_data_Complex_location{i,1},2)
#         error(['time ',num2str(i),' .speed & .location number not match, please check original file again']);
#     end
# end
    
    location_24h_data=cell(size(speedList,1),1)
# main_SD_R.m:252
    
    if size(CT_time_list,1) < dot(24,60):
        location_data_duration=dot(size(CT_time_list,1),60)
# main_SD_R.m:254
    else:
        location_data_duration=dot(dot(24,60),60)
# main_SD_R.m:256
    
    location_data_C=cell(size(speedList,1),2)
# main_SD_R.m:258
    
    for i in arange(1,size(speedList,1)).reshape(-1):
        location_matrix_24hs=zeros(location_data_duration,size(import_data_Complex_location[i,1],2))
# main_SD_R.m:260
        location_matrix_full=import_data_Complex_location[i,1]
# main_SD_R.m:261
        for j in arange(1,(size(import_data_Complex_location[i,1],2) / 2)).reshape(-1):
            location_line_temp=import_data_Complex_location[i,1](arange(),dot(j,2))
# main_SD_R.m:263
            temp_Nzero=find(location_line_temp > 0)
# main_SD_R.m:264
            if size(temp_Nzero,1) <= 0:
                temp_Nzero[1]=1
# main_SD_R.m:266
            if temp_Nzero(1) + location_data_duration - 1 < size(import_data_Complex_location[i,1],1):
                location_matrix_24hs[arange(),arange(dot(j,2) - 1,dot(j,2))]=import_data_Complex_location[i,1](arange(temp_Nzero(1),temp_Nzero(1) + location_data_duration - 1),arange(dot(j,2) - 1,dot(j,2)))
# main_SD_R.m:269
            else:
                location_matrix_24hs[arange(end() - (size(import_data_Complex_location[i,1],1) - temp_Nzero(1)),end()),arange(dot(j,2) - 1,dot(j,2))]=import_data_Complex_location[i,1](arange(temp_Nzero(1),end()),arange(dot(j,2) - 1,dot(j,2)))
# main_SD_R.m:271
                location_matrix_24hs[arange(1,end() - (size(import_data_Complex_location[i,1],1) - temp_Nzero(1)) - 1),dot(j,2) - 1]=location_matrix_24hs(end() - (size(import_data_Complex_location[i,1],1) - temp_Nzero(1)),dot(j,2) - 1)
# main_SD_R.m:272
                location_matrix_24hs[arange(1,end() - (size(import_data_Complex_location[i,1],1) - temp_Nzero(1)) - 1),dot(j,2)]=location_matrix_24hs(end() - (size(import_data_Complex_location[i,1],1) - temp_Nzero(1)),dot(j,2))
# main_SD_R.m:273
            location_matrix_full[arange(1,temp_Nzero(1) - 1),dot(j,2) - 1]=import_data_Complex_location[i,1](temp_Nzero(1),dot(j,2) - 1)
# main_SD_R.m:275
            location_matrix_full[arange(1,temp_Nzero(1) - 1),dot(j,2)]=import_data_Complex_location[i,1](temp_Nzero(1),dot(j,2))
# main_SD_R.m:276
        location_24h_data[i,1]=location_matrix_24hs
# main_SD_R.m:278
        location_data_C[i,1]=location_matrix_full
# main_SD_R.m:279
    
    #Ѱ�ҵ�ÿһֻ��Ӭ�����˶��ķ�Χ,ʹ��24Сʱ�����ݵļ�ֵ��Ϊ�߿�,����ʳ���λ�ã����е�ʳ��Ĭ�ϵİڷ�λ�ö����м�
    food_distance=cell(size(speedList,1),1)
# main_SD_R.m:282
    
    for i in arange(1,size(speedList,1)).reshape(-1):
        markFile=concat([speedList[i,1](arange(1,end() - 9)),'mark.txt'])
# main_SD_R.m:284
        markFid=fopen(markFile,'r')
# main_SD_R.m:285
        if markFid == - 1:
            location_24h_max_temp=zeros(3,size(location_24h_data[i,1],2))
# main_SD_R.m:287
            location_24h_max_temp[1,arange()]=max(location_24h_data[i,1],[],1)
# main_SD_R.m:288
            location_24h_max_temp[2,arange()]=min(location_24h_data[i,1],[],1)
# main_SD_R.m:289
            location_24h_max_temp[3,arange()]=location_24h_max_temp(1,arange()) - location_24h_max_temp(2,arange())
# main_SD_R.m:290
            location_24h_refe=zeros(3,size(location_24h_max_temp,2) / 2)
# main_SD_R.m:291
            if sum(location_24h_max_temp(3,arange(1,end(),2))) - sum(location_24h_max_temp(3,arange(2,end(),2))) > 0:
                location_24h_refe[arange(1,2),arange()]=location_24h_max_temp(arange(1,2),arange(1,end(),2))
# main_SD_R.m:293
                location_data_C[i,2]=location_data_C[i,1](arange(),arange(1,end(),2))
# main_SD_R.m:294
            else:
                location_24h_refe[arange(1,2),arange()]=location_24h_max_temp(arange(1,2),arange(2,end(),2))
# main_SD_R.m:296
                location_data_C[i,2]=location_data_C[i,1](arange(),arange(2,end(),2))
# main_SD_R.m:297
            food_location=(max(location_24h_refe,[],2) + min(location_24h_refe,[],2)) / 2
# main_SD_R.m:299
            for j in arange(1,size(location_24h_refe,2)).reshape(-1):
                if abs(location_24h_refe(1,j) - food_location) > abs(location_24h_refe(2,j) - food_location):
                    location_24h_refe[3,j]=location_24h_refe(2,j)
# main_SD_R.m:302
                else:
                    location_24h_refe[3,j]=location_24h_refe(1,j)
# main_SD_R.m:304
            location_distance_temp=zeros(size(location_data_C[i,2]))
# main_SD_R.m:307
            for j in arange(1,size(location_24h_refe,2)).reshape(-1):
                location_distance_temp[arange(),j]=abs(location_data_C[i,2](arange(),j) - location_24h_refe(3,j))
# main_SD_R.m:309
            food_distance[i,1]=location_distance_temp
# main_SD_R.m:311
        else:
            FidTempLine=fgetl(markFid)
# main_SD_R.m:313
            if strcmpi(FidTempLine,'One'):
                TempMiddle=str2double(cell2mat(regexp(fgetl(markFid),'\\d','match')))
# main_SD_R.m:315
                FidTempLine=fgetl(markFid)
# main_SD_R.m:316
                LineRegTemp=regexp(FidTempLine,'\\t','split')
# main_SD_R.m:316
                TempLeft=LineRegTemp[1,2]
# main_SD_R.m:316
                FidTempLine=fgetl(markFid)
# main_SD_R.m:317
                LineRegTemp=regexp(FidTempLine,'\\t','split')
# main_SD_R.m:317
                TempRight=LineRegTemp[1,2]
# main_SD_R.m:317
                location_24h_max_temp=zeros(3,size(location_24h_data[i,1],2))
# main_SD_R.m:318
                location_24h_max_temp[1,arange()]=max(location_24h_data[i,1],[],1)
# main_SD_R.m:319
                location_24h_max_temp[2,arange()]=min(location_24h_data[i,1],[],1)
# main_SD_R.m:320
                location_24h_max_temp[3,arange()]=location_24h_max_temp(1,arange()) - location_24h_max_temp(2,arange())
# main_SD_R.m:321
                location_24h_refe=zeros(3,size(location_24h_max_temp,2) / 2)
# main_SD_R.m:322
                if sum(location_24h_max_temp(3,arange(1,end(),2))) - sum(location_24h_max_temp(3,arange(2,end(),2))) > 0:
                    location_24h_refe[arange(1,2),arange()]=location_24h_max_temp(arange(1,2),arange(1,end(),2))
# main_SD_R.m:324
                    location_data_C[i,2]=location_data_C[i,1](arange(),arange(1,end(),2))
# main_SD_R.m:325
                else:
                    location_24h_refe[arange(1,2),arange()]=location_24h_max_temp(arange(1,2),arange(2,end(),2))
# main_SD_R.m:327
                    location_data_C[i,2]=location_data_C[i,1](arange(),arange(2,end(),2))
# main_SD_R.m:328
                for j in arange(1,size(location_24h_refe,2)).reshape(-1):
                    location_24h_refe[3,j]=1000
# main_SD_R.m:331
                    if (location_24h_refe(1,j) + location_24h_refe(2,j)) / 2 > TempMiddle:
                        if strcmpi(TempLeft,'Small'):
                            location_24h_refe[3,j]=location_24h_refe(2,j)
# main_SD_R.m:334
                        else:
                            if strcmpi(TempLeft,'Large'):
                                location_24h_refe[3,j]=location_24h_refe(1,j)
# main_SD_R.m:336
                    else:
                        if strcmpi(TempRight,'Small'):
                            location_24h_refe[3,j]=location_24h_refe(2,j)
# main_SD_R.m:340
                        else:
                            if strcmpi(TempRight,'Large'):
                                location_24h_refe[3,j]=location_24h_refe(1,j)
# main_SD_R.m:342
                location_distance_temp=zeros(size(location_data_C[i,2]))
# main_SD_R.m:346
                for j in arange(1,size(location_24h_refe,2)).reshape(-1):
                    location_distance_temp[arange(),j]=abs(location_data_C[i,2](arange(),j) - location_24h_refe(3,j))
# main_SD_R.m:348
                food_distance[i,1]=location_distance_temp
# main_SD_R.m:350
                clear('TempMiddle','LineRegTemp','TempLeft','LineRegTemp')
            else:
                if strcmpi(FidTempLine,'Two'):
                    TempMiddle=str2double(cell2mat(regexp(fgetl(markFid),'\\d','match')))
# main_SD_R.m:354
                    location_24h_max_temp=zeros(3,size(location_24h_data[i,1],2))
# main_SD_R.m:355
                    location_24h_max_temp[1,arange()]=max(location_24h_data[i,1],[],1)
# main_SD_R.m:356
                    location_24h_max_temp[2,arange()]=min(location_24h_data[i,1],[],1)
# main_SD_R.m:357
                    location_24h_max_temp[3,arange()]=location_24h_max_temp(1,arange()) - location_24h_max_temp(2,arange())
# main_SD_R.m:358
                    location_24h_refe=zeros(3,size(location_24h_max_temp,2) / 2)
# main_SD_R.m:359
                    if sum(location_24h_max_temp(3,arange(1,end(),2))) - sum(location_24h_max_temp(3,arange(2,end(),2))) > 0:
                        location_24h_refe[arange(1,2),arange()]=location_24h_max_temp(arange(1,2),arange(1,end(),2))
# main_SD_R.m:361
                        location_data_C[i,2]=location_data_C[i,1](arange(),arange(1,end(),2))
# main_SD_R.m:362
                    else:
                        location_24h_refe[arange(1,2),arange()]=location_24h_max_temp(arange(1,2),arange(2,end(),2))
# main_SD_R.m:364
                        location_data_C[i,2]=location_data_C[i,1](arange(),arange(2,end(),2))
# main_SD_R.m:365
                    Temp_Left_number=0
# main_SD_R.m:367
                    Temp_Right_number=0
# main_SD_R.m:367
                    refe_left=zeros(size(location_24h_refe))
# main_SD_R.m:367
                    refe_right=zeros(size(location_24h_refe))
# main_SD_R.m:367
                    for j in arange(1,size(location_24h_refe,2)).reshape(-1):
                        if (location_24h_refe(1,j) + location_24h_refe(2,j)) / 2 > TempMiddle:
                            Temp_Right_number=Temp_Right_number + 1
# main_SD_R.m:370
                            refe_right[arange(),Temp_Right_number]=location_24h_refe(arange(),j)
# main_SD_R.m:371
                        else:
                            Temp_Left_number=Temp_Left_number + 1
# main_SD_R.m:373
                            refe_left[arange(),Temp_Left_number]=location_24h_refe(arange(),j)
# main_SD_R.m:374
                    food_left=(max(refe_left(arange(),arange(1,Temp_Left_number)),[],2) + min(refe_left(arange(),arange(1,Temp_Left_number)),[],2)) / 2
# main_SD_R.m:377
                    food_right=(max(refe_right(arange(),arange(1,Temp_Right_number)),[],2) + min(refe_right(arange(),arange(1,Temp_Right_number)),[],2)) / 2
# main_SD_R.m:378
                    for j in arange(1,size(location_24h_refe,2)).reshape(-1):
                        if (location_24h_refe(1,j) + location_24h_refe(2,j)) / 2 > TempMiddle:
                            if abs(location_24h_refe(1,j) - food_left) > abs(location_24h_refe(2,j) - food_left):
                                location_24h_refe[3,j]=location_24h_refe(2,j)
# main_SD_R.m:382
                            else:
                                location_24h_refe[3,j]=location_24h_refe(1,j)
# main_SD_R.m:384
                        else:
                            if abs(location_24h_refe(1,j) - food_right) > abs(location_24h_refe(2,j) - food_right):
                                location_24h_refe[3,j]=location_24h_refe(2,j)
# main_SD_R.m:388
                            else:
                                location_24h_refe[3,j]=location_24h_refe(1,j)
# main_SD_R.m:390
                    location_distance_temp=zeros(size(location_data_C[i,2]))
# main_SD_R.m:394
                    for j in arange(1,size(location_24h_refe,2)).reshape(-1):
                        location_distance_temp[arange(),j]=abs(location_data_C[i,2](arange(),j) - location_24h_refe(3,j))
# main_SD_R.m:396
                    food_distance[i,1]=location_distance_temp
# main_SD_R.m:398
                    clear('TempMiddle','Temp_Left_number','Temp_Right_number','refe_left','refe_right','food_left','food_right')
                else:
                    if strcmpi(FidTempLine,'Two-2'):
                        TempMiddle=str2double(cell2mat(regexp(fgetl(markFid),'\\d','match')))
# main_SD_R.m:402
                        FidTempLine=fgetl(markFid)
# main_SD_R.m:403
                        LineRegTemp=regexp(FidTempLine,'\\t','split')
# main_SD_R.m:403
                        location_24h_max_temp=zeros(3,size(location_24h_data[i,1],2))
# main_SD_R.m:404
                        location_24h_max_temp[1,arange()]=max(location_24h_data[i,1],[],1)
# main_SD_R.m:405
                        location_24h_max_temp[2,arange()]=min(location_24h_data[i,1],[],1)
# main_SD_R.m:406
                        location_24h_max_temp[3,arange()]=location_24h_max_temp(1,arange()) - location_24h_max_temp(2,arange())
# main_SD_R.m:407
                        location_24h_refe=zeros(3,size(location_24h_max_temp,2) / 2)
# main_SD_R.m:408
                        if sum(location_24h_max_temp(3,arange(1,end(),2))) - sum(location_24h_max_temp(3,arange(2,end(),2))) > 0:
                            location_24h_refe[arange(1,2),arange()]=location_24h_max_temp(arange(1,2),arange(1,end(),2))
# main_SD_R.m:410
                            location_data_C[i,2]=location_data_C[i,1](arange(),arange(1,end(),2))
# main_SD_R.m:411
                        else:
                            location_24h_refe[arange(1,2),arange()]=location_24h_max_temp(arange(1,2),arange(2,end(),2))
# main_SD_R.m:413
                            location_data_C[i,2]=location_data_C[i,1](arange(),arange(2,end(),2))
# main_SD_R.m:414
                        Temp_Left_number=0
# main_SD_R.m:416
                        Temp_Right_number=0
# main_SD_R.m:416
                        refe_left=zeros(size(location_24h_refe))
# main_SD_R.m:416
                        refe_right=zeros(size(location_24h_refe))
# main_SD_R.m:416
                        for j in arange(1,size(location_24h_refe,2)).reshape(-1):
                            if (location_24h_refe(1,j) + location_24h_refe(2,j)) / 2 > TempMiddle:
                                Temp_Right_number=Temp_Right_number + 1
# main_SD_R.m:419
                                refe_right[arange(),Temp_Right_number]=location_24h_refe(arange(),j)
# main_SD_R.m:420
                            else:
                                Temp_Left_number=Temp_Left_number + 1
# main_SD_R.m:422
                                refe_left[arange(),Temp_Left_number]=location_24h_refe(arange(),j)
# main_SD_R.m:423
                        food_left=(max(refe_left(arange(),arange(1,Temp_Left_number)),[],2) + min(refe_left(arange(),arange(1,Temp_Left_number)),[],2)) / 2
# main_SD_R.m:426
                        food_right=(max(refe_right(arange(),arange(1,Temp_Right_number)),[],2) + min(refe_right(arange(),arange(1,Temp_Right_number)),[],2)) / 2
# main_SD_R.m:427
                        if strcmpi(LineRegTemp[1,1],'L'):
                            if strcmpi(LineRegTemp[1,2],'Small'):
                                food_left=min(refe_left(arange(),arange(1,Temp_Left_number)),[],2)
# main_SD_R.m:430
                            else:
                                food_left=max(refe_left(arange(),arange(1,Temp_Left_number)),[],2)
# main_SD_R.m:432
                        else:
                            if strcmpi(LineRegTemp[1,2],'Small'):
                                food_right=min(refe_right(arange(),arange(1,Temp_Right_number)),[],2)
# main_SD_R.m:436
                            else:
                                food_right=max(refe_right(arange(),arange(1,Temp_Right_number)),[],2)
# main_SD_R.m:438
                        for j in arange(1,size(location_24h_refe,2)).reshape(-1):
                            if (location_24h_refe(1,j) + location_24h_refe(2,j)) / 2 > TempMiddle:
                                if abs(location_24h_refe(1,j) - food_left) > abs(location_24h_refe(2,j) - food_left):
                                    location_24h_refe[3,j]=location_24h_refe(2,j)
# main_SD_R.m:444
                                else:
                                    location_24h_refe[3,j]=location_24h_refe(1,j)
# main_SD_R.m:446
                            else:
                                if abs(location_24h_refe(1,j) - food_right) > abs(location_24h_refe(2,j) - food_right):
                                    location_24h_refe[3,j]=location_24h_refe(2,j)
# main_SD_R.m:450
                                else:
                                    location_24h_refe[3,j]=location_24h_refe(1,j)
# main_SD_R.m:452
                        location_distance_temp=zeros(size(location_data_C[i,2]))
# main_SD_R.m:456
                        for j in arange(1,size(location_24h_refe,2)).reshape(-1):
                            location_distance_temp[arange(),j]=abs(location_data_C[i,2](arange(),j) - location_24h_refe(3,j))
# main_SD_R.m:458
                        food_distance[i,1]=location_distance_temp
# main_SD_R.m:460
                        clear('TempMiddle','Temp_Left_number','Temp_Right_number','refe_left','refe_right','food_left','food_right','LineRegTemp')
            fclose(markFid)
            clear('FidTempLine')
        clear('markFile','markFid')
    
    fprintf(process_report,'%s\\n','\xbc\xc6\xcb\xe3\xd3\xeb\xca\xb3\xce\xef\xbe\xe0\xc0\xeb\xcd\xea\xb1\xcf')
    fprintf('%s\\n','...\xbc\xc6\xcb\xe3\xd3\xeb\xca\xb3\xce\xef\xbe\xe0\xc0\xeb\xcd\xea\xb1\xcf')
    #mat_file_path=[outputDir,'\',datestr(now,30),'_main_SD_R_imported_location.mat'];
    mat_file_path=concat([outputDir,'\\main_SD_R_imported_location.mat'])
# main_SD_R.m:471
    save(mat_file_path,'import_data_Complex_location','-v7.3')
    
    clear('location_24h_data','location_data_duration','location_matrix_24hs','location_line_temp','temp_Nzero','location_24h_max','location_24h_refe','location_24h_max_temp')
    clear('food_location','location_data_C','location_matrix_full','location_distance_temp','import_data_Complex_location')
    #����ʹ�õ����ݣ�food_distance
## ����.jpeg�ļ�������config_flys.txt;  ����&�ϲ� sleep_mins
#����Ʒϵ��Ŀ,line_number
    line_number=0
# main_SD_R.m:478
    i=1
# main_SD_R.m:479
    line_number=line_number + size(import_data_Complex_order[i,1],1)
# main_SD_R.m:480
    raw_draw_out=cell(size(import_data_Complex_order[i,1],1),2)
# main_SD_R.m:481
    for j in arange(1,size(import_data_Complex_order[i,1],1)).reshape(-1):
        out_matrix_temp=zeros(size(CT_time_list,1),(size(import_data_Complex_order[i,1][j,2],2) + 1))
# main_SD_R.m:483
        out_matrix_temp[arange(),1]=CT_time_list(arange(),1)
# main_SD_R.m:484
        raw_draw_out[j,1]=import_data_Complex_order[i,1][j,1]
# main_SD_R.m:485
        out_matrix_temp[arange(),arange(2,end())]=sleep_mins[i,1](arange(),str2double(import_data_Complex_order[i,1][j,2]) + 1)
# main_SD_R.m:486
        raw_draw_out[j,2]=out_matrix_temp
# main_SD_R.m:487
    
    for i in arange(2,size(speedList,1)).reshape(-1):
        line_number=line_number + size(import_data_Complex_order[i,1],1)
# main_SD_R.m:490
        raw_draw_out_temp=cell(size(import_data_Complex_order[i,1],1),2)
# main_SD_R.m:491
        for j in arange(1,size(import_data_Complex_order[i,1],1)).reshape(-1):
            out_matrix_temp=zeros(size(CT_time_list,1),(size(import_data_Complex_order[i,1][j,2],2) + 1))
# main_SD_R.m:493
            out_matrix_temp[arange(),1]=CT_time_list(arange(),1)
# main_SD_R.m:494
            raw_draw_out_temp[j,1]=import_data_Complex_order[i,1][j,1]
# main_SD_R.m:495
            out_matrix_temp[arange(),arange(2,end())]=sleep_mins[i,1](arange(),str2double(import_data_Complex_order[i,1][j,2]) + 1)
# main_SD_R.m:496
            raw_draw_out_temp[j,2]=out_matrix_temp
# main_SD_R.m:497
        raw_draw_out=concat([[raw_draw_out],[raw_draw_out_temp]])
# main_SD_R.m:499
    
    raw_drawn_func(raw_draw_out,outputDir)
    file_name_out_text=concat([outputDir,'\\','config_flys.txt'])
# main_SD_R.m:502
    
    file_fid_out_text=fopen(file_name_out_text,'w')
# main_SD_R.m:503
    fprintf(file_fid_out_text,'%s\\t%s\\t%s\\n','line','indi','frag')
    for i in arange(1,size(raw_draw_out,1)).reshape(-1):
        for j in arange(1,size(raw_draw_out[i,2],2) - 1).reshape(-1):
            fprintf(file_fid_out_text,'%d%s',i,'--')
            fprintf(file_fid_out_text,'%s\\t',raw_draw_out[i,1])
            fprintf(file_fid_out_text,'%d\\t',j)
            for k in arange(1,size(config_time_M,1) - 1).reshape(-1):
                fprintf(file_fid_out_text,'%d%c',k,',')
            fprintf(file_fid_out_text,'\\n')
    
    fclose(file_fid_out_text)
    fprintf(process_report,'%s\\n','\xc9\xfa\xb3\xc9jpeg\xcd\xea\xb1\xcf')
    fprintf('%s\\n','...\xc9\xfa\xb3\xc9jpeg\xcd\xea\xb1\xcf')
    clear('out_matrix_temp')
    #���õ������� line_number������Ʒϵ��Ŀ; raw_drawn_func{*,1}:line_name;{*,2}:sleep_mins//����������ͼƬ
## ����&�ϲ� sleep_matrix; sleep_30mins_SD; sleep_30mins_CT;sleep_mins;... line_name as id
    group_data_C=cell(line_number,8)
# main_SD_R.m:521
    
    temp_sequence=1
# main_SD_R.m:522
    for i in arange(1,size(speedList,1)).reshape(-1):
        for j in arange(1,size(import_data_Complex_order[i,1],1)).reshape(-1):
            out_speed_temp=speed_matrix[i,1](arange(),str2double(import_data_Complex_order[i,1][j,2]) + 1)
# main_SD_R.m:525
            out_speed_30CT_temp=speed_30mins_CT[i,1](arange(),str2double(import_data_Complex_order[i,1][j,2]) + 1)
# main_SD_R.m:526
            out_sleep_matrix_temp=sleep_matrix[i,1](arange(),str2double(import_data_Complex_order[i,1][j,2]) + 1)
# main_SD_R.m:527
            out_sleep_mins_temp=sleep_mins[i,1](arange(),str2double(import_data_Complex_order[i,1][j,2]) + 1)
# main_SD_R.m:528
            out_sleep_30mins_SD_temp=sleep_30mins_SD[i,1](arange(),str2double(import_data_Complex_order[i,1][j,2]) + 1)
# main_SD_R.m:529
            out_sleep_30mins_CT_temp=sleep_30mins_CT[i,1](arange(),str2double(import_data_Complex_order[i,1][j,2]) + 1)
# main_SD_R.m:530
            out_food_distance_temp=food_distance[i,1](arange(),str2double(import_data_Complex_order[i,1][j,2]) + 1)
# main_SD_R.m:531
            group_data_C[temp_sequence,1]=import_data_Complex_order[i,1][j,1]
# main_SD_R.m:532
            group_data_C[temp_sequence,2]=out_speed_temp
# main_SD_R.m:533
            group_data_C[temp_sequence,3]=out_speed_30CT_temp
# main_SD_R.m:534
            group_data_C[temp_sequence,4]=out_sleep_matrix_temp
# main_SD_R.m:535
            group_data_C[temp_sequence,5]=out_sleep_mins_temp
# main_SD_R.m:536
            group_data_C[temp_sequence,6]=out_sleep_30mins_SD_temp
# main_SD_R.m:537
            group_data_C[temp_sequence,7]=out_sleep_30mins_CT_temp
# main_SD_R.m:538
            group_data_C[temp_sequence,8]=out_food_distance_temp
# main_SD_R.m:539
            temp_sequence=temp_sequence + 1
# main_SD_R.m:540
    
    fprintf(process_report,'%s\\n','...\xca\xfd\xbe\xdd\xb7\xd6\xd7\xe9\xcd\xea\xb1\xcf')
    fprintf('%s\\n','...\xca\xfd\xbe\xdd\xb7\xd6\xd7\xe9\xcd\xea\xb1\xcf')
    clear('temp_sequence','out_speed_temp','out_speed_30CT_temp','out_sleep_matrix_temp','out_sleep_mins_temp','out_sleep_30mins_SD_temp','out_sleep_30mins_CT_temp','out_speed_30CT_temp')
    clear('out_food_distance_temp')
    #���õ������� group_data_C; 
## ���洦������ݣ�
#import_data_Complex, group_data_C,raw_draw_out,config_time_M, min_time_length,
#���������,���������,��ͼ����,ʱ����,ʱ��/mins
#outputDir, dirPath, speedList, locationList, orderList,line_number
#������ļ��У�������ļ��У�speed�ļ��б�location�ļ��б�order�ļ��б�
# sleep_matrix, sleep_mins, sleep_30mins(sleep_30mins_SD &
# sleep_30mins_CT), speed_matrix speed_30mins_CT food_distance
#��������:0/1״̬,ÿ����˯��,ÿ30����˯��,�ٶȼ�¼,�ٶȾ�ֵ,��ʳ�����
#mat_file_path=[outputDir,'\',datestr(now,30),'_main_SD_R.mat'];
    mat_file_path=concat([outputDir,'\\main_SD_R.mat'])
# main_SD_R.m:556
    save(mat_file_path,'import_data_Complex_order','group_data_C','raw_draw_out','config_time_M','min_time_length','outputDir','dirPath','speedList','locationList','orderList','sleep_matrix','sleep_mins','sleep_30mins_SD','sleep_30mins_CT','speed_matrix','speed_30mins_CT','food_distance','line_number','-v7.3')
    fprintf(process_report,'%s\\n','...\xca\xfd\xbe\xdd\xb1\xa3\xb4\xe6\xcd\xea\xb1\xcf')
    fprintf('%s\\n','...\xca\xfd\xbe\xdd\xb1\xa3\xb4\xe6\xcd\xea\xb1\xcf')
    fclose(process_report)
    
    fprintf('%s\\n','...\xb9\xd8\xb1\xd5')
    clear