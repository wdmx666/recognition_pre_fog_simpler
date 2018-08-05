import shelve
import path
import pandas as pd

p1=path.Path(r'E:\my_proj\fog_recognition\ExtendFoGData\fixed_data\Tuned4Model\extract_feature_para_opt')
fs=p1.files()
res=[]
for i in fs:
    if i.find("res.dat")>0:
        res.append(i.splitext()[0])
print(res[0])
all_res_df=pd.DataFrame()
for test in res:
    with shelve.open(test) as db:
        print(len(list(db.keys())),list(db.keys()))
        res_li = {}
        for k in db.keys():
            print(db[k])
            res_li[k]=db[k]
        all_res_df = all_res_df.append(pd.DataFrame.from_dict(res_li,orient="index"))

print(all_res_df.head())
all_res_df.to_csv("all_f1_kappa.csv")