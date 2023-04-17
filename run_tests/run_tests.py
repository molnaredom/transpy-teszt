from dis import dis
import json
from pathlib import Path
import subprocess
import os
from timeit import default_timer as timer
import sys
from statistics import mean
from adam.codecov_api import get_coverage
from adam.radon_machine import get_radon_metrics, radons_diff
PROJECTS_PATH = Path(__file__).parent.resolve() / "new"
TEST_MEASURES_PATH = Path(__file__).parent.resolve() / "test_measures.json"
DEFAULT_PATH = Path(__file__).parent.resolve()

def _pytest(project):
    """Runs pytest in the projects folder."""
    os.chdir(PROJECTS_PATH / project)
    # print("test",project)
    # print(" ".join([sys.executable, '-m', 'mprof', 'run', '--include-children', sys.executable, "-m", "pytest"]))
    subprocess.run([sys.executable, '-m', 'mprof', 'run', '--include-children', sys.executable, "-m", "pytest"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _django_test(project):
    os.chdir(PROJECTS_PATH / project / "tests")
    subprocess.run(
        [sys.executable, '-m', 'mprof', 'run', '--include-children', sys.executable, "runtests.py", "-v", "0"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

PROJECTS = {
    # "asztro": ("https://github.com/molnaredom/asztro", _pytest),
    "keras": ("https://github.com/keras-team/keras", _pytest),
    # "discord.py": ("https://github.com/Rapptz/discord.py", _pytest),
    # "InstaPy": ("https://github.com/InstaPy/InstaPy", _pytest),
    "django": ("https://github.com/django/django", _django_test),
    # "pylint": ("https://github.com/PyCQA/pylint", _pytest),
    # "flask": ("https://github.com/pallets/flask", _pytest),
    # "loguru": ("https://github.com/Delgan/loguru", _pytest),
    # "autojump": ("https://github.com/wting/autojump", _pytest),
    # "spleeter": ("https://github.com/deezer/spleeter", _pytest),
    # "freqtrade": ("https://github.com/freqtrade/freqtrade", _pytest),
    # "bokeh": ("https://github.com/bokeh/bokeh", _pytest),
    # "Gooey": ("https://github.com/chriskiehl/Gooey", _pytest),
    # "PythonRobotics": ("https://github.com/AtsushiSakai/PythonRobotics", _pytest),
    # "textual": ("https://github.com/Textualize/textual", _pytest),
    # "fairseq": ("https://github.com/facebookresearch/fairseq", _pytest),
    # "jax": ("https://github.com/google/jax", _pytest),
    # "poetry": ("https://github.com/python-poetry/poetry", _pytest),
    # "tqdm": ("https://github.com/tqdm/tqdm", _pytest),
    # "django-rest-framework": ("https://github.com/encode/django-rest-framework", _pytest),
    # "python-telegram-bot": ("https://github.com/python-telegram-bot/python-telegram-bot", _pytest),
    # "lightning": ("https://github.com/Lightning-AI/lightning", _pytest),
    # "apache_airflow": ("https://github.com/apache/airflow", _pytest),
    # "certbot": ("https://github.com/certbot/certbot", _pytest),
    # "httpie": ("https://github.com/httpie/httpie", _pytest),
    # "scarpy": ("https://github.com/scrapy/scrapy", _pytest),
    # "face_recognition": ("https://github.com/ageitgey/face_recognition", _pytest),
    # # "nerd-fonts": ("https://github.com/ryanoasis/nerd-fonts", _pytest), furán nagy helyet foglalhat
    # "rich": ("https://github.com/Textualize/rich", _pytest),
    # "scikit-learn": ("https://github.com/scikit-learn/scikit-learn", _pytest),
    # "ansible": ("https://github.com/ansible/ansible", _pytest),
}
config = {
    "test": True,
    "radon": False,
    "codecov": False
}

def get_unittest_data(project, func, iter, transformed=False):
    """Runs unittest iter times, returns an array of dicts of the form: {name, transformed, time, memory, result}."""
    _project = f"transformed-{project}" if transformed else project
    data = []
    if not (PROJECTS_PATH / _project).exists():
        if transformed:
            # print(f"{project} is not transformed yet!")
            os.chdir(PROJECTS_PATH.parent)#
            subprocess.call([sys.executable, '/home/molnar/transpy_eredeti', f'{Path(PROJECTS_PATH / project)}', '-o'])
        else:
            raise FileNotFoundError(f"Cannot find project: {_project} in directory: {PROJECTS_PATH}")
    if config["test"]:
        for i in range(iter):
            # print(f"Running unit test # {i + 1}. for project: {_project}.")
            start = timer()
            func(_project)
            end = timer()
            data.append(
                {"name": project, "transformed": transformed,
                 "time": (end - start), "memory": get_mprof_highest()})  #
    return data


def latest_file(path: Path, pattern: str = "*"):
    files = path.glob(pattern)
    return max(files, key=lambda x: x.stat().st_ctime)


def get_mprof_highest():
    last_mprofile = latest_file(Path(os.getcwd()), 'mprofile_*.dat')

    with open(last_mprofile, 'r') as f:
        data = f.readlines()
        peak_mem = -1
        for line in data:
            if line.startswith('MEM'):
                mem = float(line.split(' ')[1])
                if mem > peak_mem:
                    peak_mem = mem
    os.remove(last_mprofile)
    return peak_mem


def save_data_json(data, url, project):
    if not TEST_MEASURES_PATH.exists():
        with open(TEST_MEASURES_PATH, "w") as f:
            json.dump(dict(), f, indent=4)

    with open(TEST_MEASURES_PATH, 'r+') as f:
        file_data = json.load(f)
        project_name = data[0]["name"]
        if project_name not in file_data:
            current_cwd = os.getcwd()
            os.chdir(PROJECTS_PATH)

            file_data[project_name] = {"difference": {}}
            if config["codecov"]:
                file_data[project_name].extend({
                    "codecov": get_coverage(repo_name=url.split("/")[-2], project_name=url.split("/")[-1])
                })
            if config["radon"]:
                file_data[project_name].extend({
                    "original": {"radon_metrics": get_radon_metrics(project),
                                 "time": [], "memory": []},
                    "transformed": {"radon_metrics": get_radon_metrics("transformed-" + project),
                                    "time": [], "memory": []},                })
            os.chdir(current_cwd)

        for record in data:
            measured_time = record["time"]
            measured_memory = record["memory"]
            if record["transformed"]:
                transormed = file_data[record["name"]]["transformed"]
                transormed["time"].append(measured_time)
                transormed["memory"].append(measured_memory)
                transormed["time_avg"] = mean(file_data[record["name"]]["transformed"]["time"])
                transormed["memory_avg"] = mean(file_data[record["name"]]["transformed"]["memory"])
            else:
                original = file_data[record["name"]]["original"]
                original["time"].append(measured_time)
                original["memory"].append(measured_memory)
                original["time_avg"] = mean(file_data[record["name"]]["original"]["time"])
                original["memory_avg"] = mean(file_data[record["name"]]["original"]["memory"])
        if config["radon"]:
            diff = file_data[record["name"]]["difference"]
            original = file_data[record["name"]]["original"]
            transformed = file_data[record["name"]]["transformed"]
            diff["radon-metrics"] = radons_diff(transformed["radon_metrics"], original["radon_metrics"])
        if config["test"]:
            diff["time_avg"] = [str(
                original["time_avg"] - transformed[
                    "time_avg"]) + " sec",
                                str((original["time_avg"] /
                                     transformed["time_avg"] - 1) * 100) + "%"]
            diff["memory_avg"] = [str(
                original["memory_avg"] - transformed[
                    "memory_avg"]),
                                  str((original["memory_avg"] /
                                       transformed["memory_avg"] - 1) * 100) + "%"]

        f.seek(0)
        json.dump(file_data, f, indent=4)


def main():
    try:
        os.chdir(Path(__file__).parent.resolve())
        subprocess.call(['git', 'clone', "https://github.com/Tirasz/transpy.git"])
        test_iteration = 1
        if not PROJECTS_PATH.exists():
            os.mkdir(PROJECTS_PATH)

        for project, (url, func) in PROJECTS.items():
            print("----------------------------\nStart:", project)
            os.chdir(PROJECTS_PATH)
            subprocess.call(['git', 'clone', url])
            try:
                for _ in range(test_iteration):
                    data = get_unittest_data(project, func, 1)
                    data.extend(get_unittest_data(project, func, 1, transformed=True))
                    save_data_json(data, url, project)
            except FileNotFoundError:
                print("Filenotfound error ---> cant_find_projects.txt")
                filename = "../cant_find_projects.txt"
                mode = "a" if os.path.exists(filename) else "w"
                with open(filename, mode) as f:
                    f.write(str(project) + "\n")

    except KeyboardInterrupt:
        print("*"*50, "\n           Művelet megszakítva\n", "*"*50)
        os.chdir(DEFAULT_PATH)
    except Exception as e:
        print("*" * 50, "\nHIBA\n", "*" * 50)
        os.chdir(DEFAULT_PATH)
        raise e

if __name__ == "__main__":
    main()
