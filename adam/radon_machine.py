import os
import subprocess
import json
import sys


def find_number(content:str, point_allowed=False):
    str_number= ""
    for char in content:
        if char.isdigit() or (point_allowed and char=="."):
            str_number += char
    return int(str_number) if not point_allowed else float(str_number)


def compelxity(module_name):
    proc = subprocess.Popen(f"python3.11 /home/molnar/radon_eredeti/radon/__main__.py cc {module_name} --total-average",
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    c = proc.stdout.read()
    # print("---", module_name)
    # print("---", os.getcwd())
    # print("---", c)
    avg_complexity = c.decode('utf-8').strip().split("\n")[-2][20:]
    return find_number(avg_complexity, point_allowed=True)


def maintainability(module_name):
    proc = subprocess.Popen(f"python3.11 /home/molnar/radon_eredeti/radon/__main__.py mi {module_name} -j",
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, encoding="utf-8")

    mi_json = json.loads(proc.stdout.readlines()[0])

    mi_values = [v["mi"] for k, v in mi_json.items() if "mi" in v]
    agv = sum(mi_values) / len(mi_values)
    return agv


def raw(module_name):
    raw_data = dict()
    proc = subprocess.Popen(f"python3.11 /home/molnar/radon_eredeti/radon/__main__.py raw {module_name} -s",
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, encoding="utf-8")
    lines = proc.stdout.readlines()
    raw_data["LOC"] = find_number(lines[-12])
    raw_data["LLOC"] = find_number(lines[-11])
    raw_data["SLOC"] = find_number(lines[-10])
    raw_data["Comments"] = find_number(lines[-9])
    raw_data["Single comments"] = find_number(lines[-8])
    raw_data["Multi"] = find_number(lines[-7])
    raw_data["blank"] = find_number(lines[-6])
    raw_data["C % L (in percentage)"] = find_number(lines[-4])
    raw_data["C % S (in percentage)"] = (find_number(lines[-3]))
    raw_data["C + M % L (in percentage)"] = find_number(lines[-2])

    return raw_data


def halstead(module_name):
    proc = subprocess.Popen(f"python3.11 /home/molnar/radon_eredeti/radon/__main__.py hal {module_name} -j",
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, encoding="utf-8")
    lines = proc.stdout.readlines()
    hal_json = json.loads(lines[0])
    halstead_metric_names = ["h1", "h2", "N1", "N2", "vocabulary", "length",
                             "calculated_length", "volume",
                             "difficulty", "effort", "time", "bugs"]
    szotar = {}
    for k,v in hal_json.items():
        if "total" in v:
            if len(v["total"]) != len(halstead_metric_names):
                print("Big prob", len(v["total"]) , len(halstead_metric_names))
            for i in range(len(v["total"])):
                if halstead_metric_names[i] in szotar:
                    szotar[halstead_metric_names[i]].append(v["total"][i])
                else:
                    szotar[halstead_metric_names[i]] = [v["total"][i]]  # create list
        else:
            print("problem", k, v)
    # print(szotar)
    eredmeny = {} # TOTAL halstead metrics
    for k, v in szotar.items():
        eredmeny[k] = sum(v)    # {"sum": ,"avg":}sum(v)/len(v)
    # print(eredmeny)
    return eredmeny


def get_radon_metrics(module_file_name, projects_path, debug):
    current_cwd = os.getcwd()
    os.chdir(projects_path)

    cc = compelxity(module_file_name)
    print(f"{cc}") if debug else None

    mi = maintainability(module_file_name)
    print(f"{mi}") if debug else None

    mraw = raw(module_file_name)
    print(f"{mraw}") if debug else None

    hal = halstead(module_file_name)
    print(f"{hal=}") if debug else None

    os.chdir(current_cwd)
    return cc, mi, mraw, hal


def radons_diff(d1:dict, d2:dict):
    """ d1-d2 """
    def add_measures(metrics_name, nested=False):
        if not nested:
            metrics[metrics_name] = {
                "value": d1[metrics_name] - d2[metrics_name],
                "percentage": 100 * (1 -d1[metrics_name] / d2[metrics_name])}
        else:
            metrics[metrics_name] = {
                "value": {key: d1[metrics_name][key] - d2[metrics_name][key] for key in d1[metrics_name]},
                "percentage": {key: (1 - d1[metrics_name][key] / d2[metrics_name][key]) * 100 for key in d1[metrics_name]}}

    metrics = dict()
    add_measures("Complexity avg")
    add_measures("Maintainability avg")
    add_measures("Raw", nested=True)
    add_measures("Halstead", nested=True)

    # with open("../../radon_eredmenyek.csv", "a") as f:
    #     print(f"Complexity avg;{metrics['Complexity avg']['value']};{metrics['Complexity avg']['percentage']}%", file=f)
    #     print(f"Maintainability avg;{metrics['Maintainability avg']['value']};{metrics['Maintainability avg']['percentage']}%", file=f)
    #     print(f"LOC;{metrics['Raw']['value']['LOC']};{metrics['Raw']['percentage']['LOC']}%", file=f)
    #     print(f"LLOC;{metrics['Raw']['value']['LLOC']};{metrics['Raw']['percentage']['LLOC']}%", file=f)
    #     print("-;-;-", file=f)
    return metrics






