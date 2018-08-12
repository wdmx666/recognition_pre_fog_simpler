import joblib
import shelve
import path
import pandas as pd

# p1=path.Path(r'E:\my_proj\fog_recognition\ExtendFoGData\fixed_data\Tuned4Model\extract_feature_para_opt')
# p1=path.Path(r'E:\my_proj\fog_recognition\ExtendFoGData\fixed_data\Tuned4Model\SelectFeature\FeatureSelect')
# p1=path.Path(r'E:\my_proj\fog_recognition\ExtendFoGData\fixed_data\Tuned4Model\SelectModel\result')
# fs=p1.files()
# res=[]
# for i in fs:
#     if i.find(".dat")>0:
#         res.append(i.splitext()[0])
# print(res[0])
# all_res_df=pd.DataFrame()
# for test in res:
#     with shelve.open(test) as db:
#         print(len(list(db.keys())), list(db.keys()))
#         res_li = {}
#         for k in db.keys():
#             print(db[k])
#             res_li[k]=db[k]
#         all_res_df = all_res_df.append(pd.DataFrame.from_dict(res_li,orient="index"))
#
# print(all_res_df.head())
# all_res_df.to_csv("modelpara1.csv")


# df = pd.read_clipboard()
# data = []
# for i in df.sample_id.unique():
#     #raw_f1_score
#     data.append(list(df[df['sample_id']==i]['raw_kappa']))
#
# df_f1=pd.DataFrame(data=data).T
# df_f1.columns=df.sample_id.unique()
# df_f1.to_csv("modelpara1b_kappa.csv")
#
# fs=p1.files()
# all_res_df=pd.DataFrame()
# for test in fs:
#     db = joblib.load(test)
#     res_li = {}
#     for k in db.keys():
#         db[k].pop("predict_result")
#         res_li[k] = db[k]
#     all_res_df = all_res_df.append(pd.DataFrame.from_dict(res_li,orient="index"))
#
# print(all_res_df.head())
# all_res_df.to_csv("modelpara1b.csv")


p1 = path.Path(r'E:\my_proj\fog_recognition\ExtendFoGData\fixed_data\Tuned4Model\ExtractParaSelector')
fs = p1.files()
res = []

all_res_df = pd.DataFrame()
for test in fs:
    data = joblib.load(test)
    print(test)
    print(len(list(data.keys())), list(data.keys()))
    res_li = {}
    for k in data.keys():
        data[k].pop("predict_result")
        res_li[k] = data[k]
    all_res_df = all_res_df.append(pd.DataFrame.from_dict(res_li, orient="index"))

print(all_res_df.head())
all_res_df.to_csv("extract_para_onebyone.csv")