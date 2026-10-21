#!/usr/bin/env python3
"""Non-identifying aggregate audit of four publicly exported CODEC workbooks.
Usage: python src/audit_codec_b08.py /path/to/restricted/xlsx
Raw records stay local; only aggregate counts are printed.
"""
import collections, csv, json, re, sys, unicodedata
from pathlib import Path
from openpyxl import load_workbook

FILES={2022:"17_06_26.xlsx",2023:"17_06_26 (1).xlsx",2024:"17_06_26 (2).xlsx",2025:"17_06_26 (3).xlsx"}
def norm(v):
    s=unicodedata.normalize("NFKD",str(v or "")).encode("ascii","ignore").decode()
    return " ".join(s.upper().split())
def select(a,b,sex):
    a,b,sex=norm(a),norm(b),norm(sex)
    if a=="FEMINICIDIO" or (a=="HOMICIDIO" and "FEMINICIDIO" in b): return "Feminicide"
    if sex!="F": return None
    if a=="LESAO CORPORAL" and b=="VIOLENCIA DOMESTICA": return "Domestic violence bodily injury"
    if a=="ESTUPRO": return "Rape"
    if a=="ESTUPRO DE VULNERAVEL": return "Rape of vulnerable person"
    return None
def main(folder):
    rows=[]
    for year,fn in FILES.items():
        wb=load_workbook(folder/fn,read_only=True,data_only=True)
        ws=wb.worksheets[0]; it=ws.iter_rows(values_only=True)
        headers=next(it)
        expected=("CONSOLIDADO(S)","ESPECIFICAÇÃO CRIME","MUNICÍPIO(S)","ANO DO FATO","DATA DO FATO","SEXO VÍTIMA")
        index={norm(v):i for i,v in enumerate(headers)}
        for name in expected:
            assert norm(name) in index,(fn,name)
        def get(row,name):
            j=index[norm(name)]
            return row[j] if j<len(row) else None
        count=collections.Counter(); exact_all=collections.Counter(); exact_selected=collections.Counter(); categories=collections.Counter()
        for row in it:
            if not any(v is not None for v in row):continue
            count["rows"]+=1
            if get(row,"DATA DO FATO") is not None:count["date_present"]+=1
            if str(get(row,"ANO DO FATO")).strip() not in (str(year),str(float(year))):count["year_mismatch"]+=1
            key=tuple(str(v) if v is not None else "" for v in row[:len(headers)])
            exact_all[key]+=1
            cat=select(get(row,"CONSOLIDADO(S)"),get(row,"ESPECIFICAÇÃO CRIME"),get(row,"SEXO VÍTIMA"))
            if cat:
                categories[cat]+=1
                count["selected"]+=1
                exact_selected[key]+=1
                if get(row,"ESPECIFICAÇÃO CRIME") in (None,""):count["selected_specification_blank"]+=1
                if get(row,"MUNICÍPIO(S)") in (None,""):count["selected_municipality_blank"]+=1
                if get(row,"SEXO VÍTIMA") in (None,""):count["selected_victim_sex_blank"]+=1
        count["identical_full_extra"]=sum(n-1 for n in exact_all.values() if n>1)
        count["identical_selected_extra"]=sum(n-1 for n in exact_selected.values() if n>1)
        rows.append({"year":year,**dict(count),"categories":dict(categories)})
        wb.close()
    print(json.dumps(rows,ensure_ascii=False,indent=2))
if __name__=="__main__":main(Path(sys.argv[1] if len(sys.argv)>1 else "."))
