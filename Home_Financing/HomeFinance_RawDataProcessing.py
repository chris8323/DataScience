
# coding: utf-8

# In[ ]:

import pandas as pd
import os
import numpy as np


# ---
# Raw Data Download
# - 우리은행 Debit
#     - 과거거래내역조회 > 엑셀저장 > 텍스트 저장
# - 우리카드 Credit
#     - 

# ---
# Raw Data import
# - 우리은행 Debit
#     - 생활비계좌
#     - 급여계좌
#     - 용돈계좌
# - 우리카드 Credit
#     - 신용카드

# In[ ]:

# file download 경로 정의
fPath = input('raw_data 파일들 경로입력: ')


# ---
# Debit Data

# In[ ]:

fPath_debit = '{}\\debit'.format(fPath)
fList_debit = os.listdir('{}'.format(fPath_debit))
fList_debit


# In[ ]:

print('filename | 금액카테고리 | table_size')
df_debit = pd.DataFrame()

#for i in range(0, len(fList_debit)):
for i in {1,2}:

    ##### filne name / category명 설정
    # (중요) 순서쌍이 맞아야한다!!
    
    fName_debit = ['급여.txt', #0
                   '용돈.txt', #1
                   '생활비.txt', #2
                   '마이너스.txt' #3            
                  ][i]

    debit_group = ['급여통장(우리/688431)', #0
                   '용돈통장(우리/399402)', #1
                   '생활비통장(우리/875309)', #2
                   '마이너스통장(우리/508867)'#3
                  ][i]



    #file imoprt
    temp = pd.read_csv('{}\\{}'.format(fPath_debit, fName_debit), engine='python', sep='|')

    temp2 = temp.drop(['No.','적요','거래후 잔액', '취급점', '메모'], axis=1)
    temp2.rename_axis({'기재내용':'메모',
                          '거래일시':'날짜'}, axis=1, inplace=True)

    # 날짜 data 처리
    temp2['날짜'] = temp2['날짜'].apply(lambda x:pd.to_datetime(x))

    # 금액 data 처리
    temp2['맡기신금액'] = temp2['맡기신금액'].apply(lambda x:int(str(x).replace(',','')))
    temp2['찾으신금액'] = temp2['찾으신금액'].apply(lambda x:int(str(x).replace(',','')))

    temp2['금액'] = temp2['맡기신금액'] + temp2['찾으신금액']

    # 대변/차변에 카테고리명 추가
    temp2.loc[(temp2['맡기신금액']!=0), '왼쪽'] = debit_group
    temp2.loc[(temp2['찾으신금액']!=0), '오른쪽'] = debit_group

    # columns 정리
    temp2.drop(['찾으신금액', '맡기신금액'], axis=1, inplace=True)
    temp2['아이템(괄호)'] = np.nan


    df_debit = df_debit.append(temp2, ignore_index=True)
    print(fName_debit, ' | ', debit_group, ' | ', temp2.shape)


# ---
# Credit Data

# In[ ]:

fPath_credit = '{}\\credit'.format(fPath)
fList_credit = os.listdir('{}'.format(fPath_credit))
fList_credit


# In[ ]:

# file import
df_credit = pd.read_excel('{}\\{}'.format(fPath_credit, fList_credit[0]), header=1)

df_credit = df_credit.loc[(df_credit['일자'].notnull()) & (df_credit['일자']!='일자')][['일자',
                                                                    #'승인번호',
                                                                    'Unnamed: 6',
                                                                    '이용가맹점(은행)명',
                                                                    '매출구분',
                                                                    '할부\n개월',
                                                                    '승인금액',
                                                                    '취소금액',                                                 
                                                                    ]].rename_axis({'일자':'날짜',
                                                                                    '이용가맹점(은행)명':'메모',
                                                                                    'Unnamed: 6':'이용카드',
                                                                                   '할부\n개월':'할부개월'}, axis=1)

# 날짜 data 처리
df_credit['날짜'] = df_credit['날짜'].apply(lambda x:pd.to_datetime('2018.'+x))

# 금액 data 처리
df_credit['승인금액'] = df_credit['승인금액'].apply(lambda x:int(str(x).replace(',','')))
df_credit['취소금액'] = df_credit['취소금액'].apply(lambda x:float(str(x).replace(',','')))

df_credit['금액'] = df_credit['승인금액'] + df_credit['취소금액']


# 할부내용 표기
df_credit.loc[(df_credit['매출구분']=='할부'),'메모'] = '[할부] ' + df_credit.loc[(df_credit['매출구분']=='할부'),'메모'] + ' // '+ df_credit.loc[(df_credit['매출구분']=='할부'),'할부개월']


# columns 정리
df_credit.drop(['이용카드', '매출구분', '할부개월', '승인금액', '취소금액'], axis=1, inplace=True)
df_credit['왼쪽'] = np.nan
df_credit['오른쪽'] = '신용카드(508867)'
df_credit['아이템(괄호)'] = np.nan

print('filename | 금액카테고리 | table_size')
print(fList_credit[0], ' | ', '신용카드(508867) | ', df_credit.shape)


# ---
# Merge & 처리

# In[ ]:

df = df_debit.append(df_credit, ignore_index=False).sort_values('날짜')[['날짜', '아이템(괄호)', '금액', '왼쪽', '오른쪽', '메모']]


# In[ ]:

df[df['금액']==0]


# In[ ]:

df = df[df['금액']!=0]


# In[ ]:

# 수입 처리
df.loc[(df['오른쪽'].isnull()) & (df['메모'].str.contains('급여')), ['오른쪽','아이템(괄호)']] = ['월급','급여']
df.loc[(df['오른쪽'].isnull()) & (df['메모'].str.contains('나은')), ['오른쪽','아이템(괄호)']] = ['from나은','나은']
df.loc[(df['오른쪽'].isnull()) & (df['메모'].str.contains('예금결산이자')), ['오른쪽','아이템(괄호)']] = ['이자수익','예금결산이자']


# In[ ]:

df.loc[(df['오른쪽'].isnull())] 


# In[ ]:

# 비용 처리
df.loc[(df['왼쪽'].isnull()) & (df['메모'].str.contains('카페')), ['왼쪽','아이템(괄호)']] = ['식비','커피']
df.loc[(df['왼쪽'].isnull()) & (df['메모'].str.contains('까페')), ['왼쪽','아이템(괄호)']] = ['식비','커피']
df.loc[(df['왼쪽'].isnull()) & (df['메모'].str.contains('커피')), ['왼쪽','아이템(괄호)']] = ['식비','커피']
df.loc[(df['왼쪽'].isnull()) & (df['메모'].str.contains('스타벅스')), ['왼쪽','아이템(괄호)']] = ['식비','커피']
df.loc[(df['왼쪽'].isnull()) & (df['메모'].str.contains('이디야')), ['왼쪽','아이템(괄호)']] = ['식비','커피']

df.loc[(df['왼쪽'].isnull()) & (df['메모'].str.contains('베이커리')), ['왼쪽','아이템(괄호)']] = ['식비','간식(빵)']

df.loc[(df['왼쪽'].isnull()) & (df['메모'].str.contains('우아한형제들')), ['왼쪽','아이템(괄호)']] = ['식비','배달의민족']

df.loc[(df['왼쪽'].isnull()) & (df['메모'].str.contains('신동아마트')), ['왼쪽','아이템(괄호)']] = ['식비','마트']



df.loc[(df['왼쪽'].isnull()) & (df['메모'].str.contains('ＰＣ')), ['왼쪽','아이템(괄호)']] = ['여가','PC방']


df.loc[(df['왼쪽'].isnull()) & (df['메모'].str.contains('택시')), ['왼쪽','아이템(괄호)']] = ['교통비','택시']
df.loc[(df['왼쪽'].isnull()) & (df['메모'].str.contains('고속버스')), ['왼쪽','아이템(괄호)']] = ['교통비','고속버스']


df.loc[(df['왼쪽'].isnull()) & (df['메모'].str.contains('약국')), ['왼쪽','아이템(괄호)']] = ['의료,건강','약국']
df.loc[(df['왼쪽'].isnull()) & (df['메모'].str.contains('병원')), ['왼쪽','아이템(괄호)']] = ['의료,건강','병원']
df.loc[(df['왼쪽'].isnull()) & (df['메모'].str.contains('한의원')), ['왼쪽','아이템(괄호)']] = ['의료,건강','한의원']


df.loc[(df['왼쪽'].isnull()) & (df['메모'].str.contains('ＫＴ유선상품')), ['왼쪽','아이템(괄호)']] = ['통신비','핸드폰']
df.loc[(df['왼쪽'].isnull()) & (df['메모'].str.contains('ＫＴ통신요금')), ['왼쪽','아이템(괄호)']] = ['통신비','KT인터넷+TV']


df.loc[(df['왼쪽'].isnull()) & (df['메모'].str.contains('우리카드결제')), ['왼쪽','아이템(괄호)']] = ['신용카드(508867)','신용카드']


# In[ ]:

df.loc[(df['왼쪽'].isnull())] 


# In[ ]:




# In[ ]:

df.to_excel('{}\\merge.xlsx'.format(fPath), index=False)


# In[ ]:

print('merge 완료')


# In[ ]:



