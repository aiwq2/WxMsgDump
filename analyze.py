
import pandas as pd
import os

def analyze(file_name,start_time,end_time):
    with open(file_name,'r',encoding='utf-8-sig') as f:
        lines=f.readlines()
        first_line=lines[0]
        if first_line[0]=='昵':
            with open(file_name,'w',encoding='utf-8-sig') as out:
                out.writelines(lines[2:])
            

    df=pd.read_csv(file_name,on_bad_lines='skip')

    # 获取指定时间范围内的数据
    start_time=start_time
    end_time=end_time
    df['时间'] = pd.to_datetime(df['时间'])
    start_date = pd.to_datetime(start_time)
    end_date = pd.to_datetime(end_time)
    df_time_select=df[(df['时间']>=start_date) & (df['时间']<=end_date)]

    msg_num_all=len(df_time_select)
    msg_me=len(df_time_select[df_time_select['你的回复']!=' '])
    msg_you=len(df_time_select[df_time_select['对方']!=' '])
    # print('总条数:',msg_num_all)
    # print('微信主:',msg_me)
    # print('对方:',msg_you)

    # 常用词分析
    from tqdm import tqdm
    frquent_words=['猪猪','晚安','宝','啵啵','早安','爱你','哈哈哈','睡觉','嗯嗯','好滴','是嗷','可爱','呜呜呜','起床']
    words_count=[0]*len(frquent_words)
    for index,row in tqdm(df_time_select.iterrows()):
        for role in ['你的回复','对方']:
            for location,word in enumerate(frquent_words):
                if word in row[role]:
                    words_count[location]+=1
    words_count_dict={}
    for index,word in enumerate(frquent_words):
        words_count_dict[word]=words_count[index]
    print(words_count_dict)
    
        # 每天发消息高频时间段分析，以及查询哪一天发的消息最多
    import matplotlib.pyplot as plt
    from tqdm import tqdm

    max_msg_day=-1
    max_msg_month=-1
    max_msg_year=-1
    day_acc=0
    yesterday=-1
    max_msg_day_num=-1

    # 分析从0时到23时
    time_list=[i for i in range(24)]
    time_count=[0]*24

    for index,row in tqdm(df_time_select.iterrows()):
        time_count[row['时间'].hour]+=1
        day=row['时间'].day
        if index==0:
            day_acc+=1
        if day==yesterday:
            day_acc+=1
        else:
            max_msg_day_num=max(max_msg_day_num,day_acc)
            if max_msg_day_num==day_acc:
                max_msg_day=day
                max_msg_month=row['时间'].month
                max_msg_year=row['时间'].year
            day_acc=1
        yesterday=day

    print(time_count)
    print('发消息最多的一天是:{}年{}月{}日,一共{}条'.format(max_msg_year,max_msg_month,max_msg_day,max_msg_day_num))


    # 保存微信记录相关消息的地址
    file_save_info='info.txt'
    user_name='lzh'
    opposite_name='hwq'

    with open(file_save_info,'w',encoding='utf-8') as out:
        out.write('微信主名字:{},对方名字:{}\n'.format(user_name,opposite_name))
        out.write('消息总条数:{},微信主消息数:{},对方消息数:{}\n'.format(msg_num_all,msg_me,msg_you))
        # out.write('统计词为:{},所对应的频数为:{}\n'.format(frquent_words,words_count))
        out.write('统计词对应的频数{}\n'.format(words_count_dict))
        out.write('每天发消息0-24小时时间统计:{}\n'.format(time_count))
        out.write('发消息最多的一天是:{}年{}月{}日,一共{}条\n'.format(max_msg_year,max_msg_month,max_msg_day,max_msg_day_num))
    print('结果写入{}成功'.format(file_save_info))
if __name__=='__main__':
    analyze(file_name='微信聊天导出\hwqh h15709438996(wxid_x5gmcr15xi3b22).csv',
            start_time='2022-10-29',
            end_time='2023-10-29',
            )
# 昵称,hwqh
# 微信号,h15709438996

