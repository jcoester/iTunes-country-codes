#!/usr/bin/env python
# coding: utf-8

import json
import os
import pandas as pd

# Specify the base directory
base_path = "./"
full = ""

# List all files in the directory
file_list = [
    f
    for f in os.listdir(base_path)
    if f.startswith("c") and f.endswith(".json")
]

# Combine chunk data
for file in file_list:
    with open(os.path.join(base_path, file), "r") as f:
        data = f.read()
        # valid codes found in chunk
        if data.rstrip() != "":
            full += data.rstrip() + ","

# Split combined data and filter out empty strings
itunes_codes = full.split(",")
itunes_codes = list(filter(None, itunes_codes))

# 2. Load list of alpha-2 country names
df_countries = pd.read_csv(
    "script/alpha2_countries.csv", encoding="utf8", keep_default_na=False
).set_index("alpha2")
dict_countries = df_countries["country"].to_dict()

# 3. Match supported iTunes codes with alpha-2 country names
itunes_countries = {}
for alpha2 in itunes_codes:
    try:
        itunes_countries[alpha2] = dict_countries[alpha2]
    except KeyError as e:
        print("•", e, "is an unknown Country code. Update the CSV table.")
        itunes_countries[alpha2] = "-"
new = dict(sorted(itunes_countries.items(), key=lambda item: item[1]))

# 4. Compared to latest version
try:
    old = json.load(open("itunes_country_codes.json"))
except FileNotFoundError:
    old = {}

diffAdd = sorted(new.keys() - old)
diffRm = sorted(old.keys() - new)
diffNames = sorted([key for key in old.keys() & new if old[key] != new[key]])

# 5. Output changes
writeFile = False
if len(diffAdd) > 0:
    writeFile = True
    print("**Added**")
    for add in diffAdd:
        print("•", add + ":", new[add])
    print("")

if len(diffRm) > 0:
    writeFile = True
    print("**Removed**")
    for rm in diffRm:
        print("•", rm + ":", old[rm])
    print("")

if len(diffNames) > 0:
    writeFile = True
    print("**Updated**")
    for name in diffNames:
        print("•", name + ":", new[name])

if writeFile:
    with open("itunes_country_codes.json", "w", encoding="utf-8") as f:
        json.dump(new, f, ensure_ascii=False, indent=4)
else:
    print("identical")
