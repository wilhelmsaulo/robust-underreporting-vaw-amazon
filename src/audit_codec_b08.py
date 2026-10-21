#!/usr/bin/env python3
"""Aggregate-only audit of four CODEC annual exports. Requires lxml.
Run: python src/audit_codec_b08.py /local/folder/with/xlsx
Prints aggregate statistics only; no individual records are persisted.
"""
import collections
import functools
import json
import sys
import unicodedata
import zipfile
from pathlib import Path
from lxml import etree as ET

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
COLS = {chr(65 + i): i for i in range(26)}
COLS.update({"AA":26, "AB":27, "AC":28, "AD":29})
FILES = {2022:"17_06_26.xlsx", 2023:"17_06_26 (1).xlsx",
         2024:"17_06_26 (2).xlsx", 2025:"17_06_26 (3).xlsx"}

@functools.lru_cache(maxsize=200000)
def norm(v):
    return " ".join(unicodedata.normalize("NFKD", str(v or "")).encode(
        "ascii","ignore").decode().upper().split())

def category(a, b, sex):
    a,b,sex = norm(a),norm(b),norm(sex)
    if a == "FEMINICIDIO" or (a == "HOMICIDIO" and "FEMINICIDIO" in b):
        return "Feminicidio"
    if sex != "F":
        return None
    if a == "LESAO CORPORAL" and b == "VIOLENCIA DOMESTICA":
        return "Domestic violence bodily injury"
    if a == "ESTUPRO":
        return "Rape"
    if a == "ESTUPRO DE VULNERAVEL":
        return "Rape of vulnerable persons"
    return None

def inspect(year, path):
    with zipfile.ZipFile(path) as archive:
        strings=[]
        if "xl/sharedStrings.xml" in archive.namelist():
            for _, e in ET.iterparse(archive.open("xl/sharedStrings.xml"), events=("end",), tag=NS+"si"):
                strings.append("".join(t.text or "" for t in e.iter(NS+"t")))
                e.clear()
        headers=None
        full=collections.Counter()
        selected=collections.Counter()
        counts=collections.Counter()
        categories=collections.Counter()
        with archive.open("xl/worksheets/sheet1.xml") as sheet:
            for _,row in ET.iterparse(sheet,events=("end",),tag=NS+"row",huge_tree=True):
                vals=[""]*30
                for cell in row.iterchildren(NS+"c"):
                    v=cell.find(NS+"v")
                    val="" if v is None else (v.text or "")
                    if cell.get("t")=="s" and val: val=strings[int(val)]
                    elif cell.get("t")=="inlineStr":
                        val="".join(t.text or "" for t in cell.iter(NS+"t"))
                    i=COLS.get(cell.get("r","").rstrip("0123456789"))
                    if i is not None: vals[i]=val
                if headers is None:
                    headers={norm(v):i for i,v in enumerate(vals)}
                    wanted=["DATA DO FATO","ANO DO FATO","CONSOLIDADO(S)",
                            "ESPECIFICAÇÃO CRIME","SEXO VÍTIMA","MUNICÍPIO(S)"]
                    indices={k:headers[norm(k)] for k in wanted}
                else:
                    def get(name): return vals[indices[name]]
                    counts["rows"]+=1
                    if get("DATA DO FATO"): counts["date_present"]+=1
                    if get("ANO DO FATO") not in (str(year), str(float(year))):
                        counts["year_mismatch"]+=1
                    # Hashes live only in memory; exact rows are never written to output.
                    key=hash(tuple(vals))
                    full[key]+=1
                    cat=category(get("CONSOLIDADO(S)"),
                                 get("ESPECIFICAÇÃO CRIME"),get("SEXO VÍTIMA"))
                    if cat is not None:
                        counts["selected"]+=1
                        categories[cat]+=1
                        selected[key]+=1
                        if not get("ESPECIFICAÇÃO CRIME"):counts["selected_specification_blank"]+=1
                        if not get("MUNICÍPIO(S)"):counts["selected_municipality_blank"]+=1
                        if not get("SEXO VÍTIMA"):counts["selected_victim_sex_blank"]+=1
                row.clear()
                while row.getprevious() is not None:
                    del row.getparent()[0]
        counts["identical_full_extra"]=sum(v-1 for v in full.values() if v>1)
        counts["identical_selected_extra"]=sum(v-1 for v in selected.values() if v>1)
        return {"year":year,**dict(counts),"categories":dict(categories)}

if __name__ == "__main__":
    folder=Path(sys.argv[1] if len(sys.argv)>1 else ".")
    print(json.dumps([inspect(year,folder/name) for year,name in FILES.items()],
                     ensure_ascii=False,indent=2))
