#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import requests as req
from seffaflik.elektrik.piyasalar import gop
from seffaflik.elektrik import tuketim
from seffaflik.elektrik import yekdem
from openpyxl import load_workbook
import datetime

def get_arz_talep_data(date):
    arz_talep = gop.arz_talep_egrisi(tarih=date)
    if arz_talep is None:
        print("Yarının arz talep verileri daha yüklenmedi.")
    return arz_talep

def merge_arz_talep_data(arz_talep):
    grouped = arz_talep.groupby(arz_talep.Saat)
    df_list = []
    for hour, group in grouped:
        group = group.drop(columns=['Saat'])
        group = group.reset_index(drop=True)
        df_list.append(group)
    arz_talep_merged = pd.concat(df_list, axis=1)
    arz_talep_merged["Arz"] = arz_talep_merged["Arz"] * -1
    return arz_talep_merged

def create_excel_file(arz_talep_merged, blok_tek, gt, ptf,path):
    writer = pd.ExcelWriter(path, engine='xlsxwriter')
    arz_talep_merged.to_excel(writer, sheet_name="Arz_Talep")
    blok_tek.to_excel(writer, sheet_name="BLOK ALIS SATIS")
    gt.to_excel(writer, sheet_name="GECMIS TUKETIM")
    dfptf = pd.DataFrame(ptf, columns=[lastweekd])
    dfptf.to_excel(writer, sheet_name="PTF")
    writer.save()

# İstenilen Tarih Değişkenleri
x = datetime.datetime.now()
today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)
tomorrow = str(tomorrow)
lastweekd = today - datetime.timedelta(days=5)
lastweekd = str(lastweekd)

# Arz Talep Verileri
arz_talep_data = get_arz_talep_data(tomorrow)
arz_talep_merged = merge_arz_talep_data(arz_talep_data)

# Diğer Veriler
blok_tek = gop.blok_miktari(baslangic_tarihi=lastweekd, bitis_tarihi=tomorrow)
sutunkaldir= ["Talep Blok Teklif Miktarı","Arz Blok Teklif Miktarı"]
for k in sutunkaldir: 
    blok_tek.pop(k)
gt = tuketim.gerceklesen(baslangic_tarihi=lastweekd, bitis_tarihi=str(today))
params = {'date': lastweekd}
url = "https://seffaflik.epias.com.tr/transparency/service/market/day-ahead-interim-mcp?"
headers = {
    'Cookie': 'seffaflik=1666017770.144.55027.263853'
}
response = req.request("GET", url, headers=headers, params=params)
p = response.json().get("body")
pt = p["interimMCPList"]
ptf = [i["marketTradePrice"] for i in pt]


# Excel Dosyası Oluşturma
path = "Arz_Talep.xlsx"
writer = pd.ExcelWriter(path, engine='xlsxwriter')
create_excel_file(arz_talep_merged, blok_tek, gt, ptf, path)

