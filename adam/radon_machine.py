
import os
import subprocess
import json
# modules = os.listdir("../projects/")
# modules = [
#             " molnaredom", "InstaPy-transpy",
#            #  "InstaPy", "transformed-InstaPy",
#            # "tqdm", "transformed-tqdm"
#            ]
# os.chdir("../projects/")

def find_number(content:str, point_allowed=False):
    str_number= ""
    for char in content:
        if char.isdigit() or (point_allowed and char=="."):
            str_number += char
    return int(str_number) if not point_allowed else float(str_number)


def compelxity(module_name):
    proc = subprocess.Popen(f"radon cc {module_name} --total-average",
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    c = proc.stdout.read()
    print("---", module_name)
    print("---", os.getcwd())
    print("---", c)
    avg_complexity = c.decode('utf-8').strip().split("\n")[-2][20:]
    return find_number(avg_complexity, point_allowed=True)


def maintainability(module_name):
    proc = subprocess.Popen(f"radon mi {module_name} -j",
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, encoding="utf-8")

    mi_json = json.loads(proc.stdout.readlines()[0])

    mi_values = [v["mi"] for k, v in mi_json.items() if "mi" in v]
    agv = sum(mi_values) / len(mi_values)
    return agv


def raw(module_name):
    raw_data = dict()
    proc = subprocess.Popen(f"radon raw {module_name} -s",
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


def get_radon_metrics(module_file_name):
    metrics = dict()
    metrics["Complexity avg"] = compelxity(module_file_name)
    metrics["Maintainability avg"] = maintainability(module_file_name)
    metrics["Raw"] = raw(module_file_name)
    print(metrics)
    return metrics


def radons_diff(d1:dict, d2:dict):
    """ d1-d2 """
    metrics = dict()
    metrics["Complexity avg"] = d1["Complexity avg"] - d2["Complexity avg"]
    metrics["Maintainability avg"] = d1["Maintainability avg"] - d2["Maintainability avg"]
    metrics["Raw"] = {key: d1["Raw"][key] - d2["Raw"][key] for key in d1["Raw"]}
    print(metrics)

    return metrics


# for module_name in modules:
#     print("module_name: ", module_name)
#     metrics = dict()
#     metrics["Complexity avg"] = compelxity(module_name)
#     metrics["Maintainability avg"] = maintainability(module_name)
#     metrics["Raw"] = raw(module_name)
#     print(metrics)





