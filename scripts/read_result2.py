import path

s = ['20161223_1_1.csv',
     '20161223_1_2.csv',
     '20161223_6_1.csv',
     '20161223_6_3.csv',
     '20161226_1_1.csv',
     '20161226_4_1.csv',
     '20161226_4_2.csv',
     '20161227_2_1.csv',
     '20161227_2_3.csv',
     '20161227_5_1.csv',
     '20180320_1_3.csv',
     '20180320_2_1.csv',
     '20180320_2_2.csv',
     'sample1_8_4.csv']
T =["T01","T02","T03","T04","T05","T06","T07","T08","T09","T10","T11","T12","T13","T14","T15","T16",]

for f in T:
    for i in path.Path(r'E:\my_proj\fog_recognition\ExtendFoGData\fixed_data\Tuned4Model\DOE2').joinpath(f).files():
        if i.basename() not in s:
            i.remove()

