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

PROJECTS_PATH = Path(__file__).parent.resolve() / "projects"
TEST_MEASURES_PATH = Path(__file__).parent.resolve() / "test_measures_v3.json"
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
    # "keras": ("https://github.com/keras-team/keras", _pytest),
    # "discord.py": ("https://github.com/Rapptz/discord.py", _pytest),
    # "InstaPy": ("https://github.com/InstaPy/InstaPy", _pytest),
    # "django": ("https://github.com/django/django", _django_test),
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
    "certbot": ("https://github.com/certbot/certbot", _pytest),
    "httpie": ("https://github.com/httpie/httpie", _pytest),
    "scarpy": ("https://github.com/scrapy/scrapy", _pytest),
    # "face_recognition": ("https://github.com/ageitgey/face_recognition", _pytest),
    # # "nerd-fonts": ("https://github.com/ryanoasis/nerd-fonts", _pytest), furán nagy helyet foglalhat
    # "rich": ("https://github.com/Textualize/rich", _pytest),
    # "scikit-learn": ("https://github.com/scikit-learn/scikit-learn", _pytest),
    # "ansible": ("https://github.com/ansible/ansible", _pytest),
}
config = {
    "test": True,
    "test_iterations": 3,
    "radon": True,
    "codecov": True,

    "debug": True,
}

def get_unittest_data(project_name, test_func, iter):
    def measure_time_and_mem(_project_name):
        data = []
        for i in range(iter):
            start = timer()
            test_func(_project_name)
            end = timer()
            data.append({"time": (end - start), "memory": get_mprof_highest()})
            if config["debug"]:
                print(data[-1])

        avg_time = sum(d["time"] for d in data) / len(data)
        avg_mem = sum(d["memory"] for d in data) / len(data)

        return avg_time, avg_mem

    o_time, o_mem = measure_time_and_mem(project_name)
    t_time, t_mem = measure_time_and_mem("transformed-" + project_name)

    return {"time": {"original": o_time, "transformed": t_time,
                     "diff": t_time-o_time, "diff%": round(1- t_time/o_time, 7)*100},
            "mem": {"original": o_mem, "transformed": t_mem,
                    "diff": t_mem-o_mem, "diff%": round(1 - t_mem/o_mem, 7)*100}}


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


def save_data_json(data, project_name):
    with open(TEST_MEASURES_PATH, 'r+') as f:
        file_data = json.load(f)
        # print("file_data", file_data)
        if project_name not in file_data:
            file_data[project_name] = {}

        file_data[project_name].update(data)

    with open(TEST_MEASURES_PATH, 'r+') as f:
        json.dump(file_data, f, indent=4)


def get_radon(project_name):
    cc, mi, raw, hal = get_radon_metrics(project_name, PROJECTS_PATH, config["debug"])
    tcc, tmi, traw, thal = get_radon_metrics("transformed-" + project_name, PROJECTS_PATH, config["debug"])

    return {"cc": {"original": cc, "transformed": tcc, "diff": tcc-cc, "diff%": round(1 - tcc/cc, 7)*100},
            "mi": {"original": mi, "transformed": tmi, "diff": tmi-mi, "diff%": round(1 - tmi/mi, 7)*100},
            "raw": {"original": raw, "transformed": traw},
            "hal": {"original": hal, "transformed": thal}}

def transform_project(project_name):
    if not (PROJECTS_PATH / project_name).exists():
        raise FileNotFoundError(f"Cannot find project: {project_name} in directory: {PROJECTS_PATH}")

    t_project_name = f"transformed-{project_name}"
    if not (PROJECTS_PATH / t_project_name).exists():
        os.chdir(PROJECTS_PATH.parent)
        subprocess.call([sys.executable, '/home/molnar/transpy-teszt/run_tests/transpy', f'{Path(PROJECTS_PATH / project_name)}', '-o'])
        print("✓", t_project_name, "has created.")
    else:
        print("✓", t_project_name, "already exists.")

def should_get_metrics(project_name):
    if not TEST_MEASURES_PATH.exists():
        with open(TEST_MEASURES_PATH, "w") as f:
            json.dump(dict(), f, indent=4)
            return True
    run = False

    with open(TEST_MEASURES_PATH, 'r+') as f:
        file_data = json.load(f)
        if project_name not in file_data:
            file_data[project_name] = {}
        project_data = file_data[project_name]
        if config["test"] and "time" not in project_data:
            run = True
            print("Unit test measures are not exists")
        if config["radon"] and "cc" not in project_data:
            run = True
            print("Radon metrics are not exists")
        if config["codecov"] and "test coverage" not in project_data:
            run = True
            print("Code coverage value is not exists")
    if not run:
        print("✓ All the queried measures are already exist.")
    return run

def main():
    try:
        clone_oroginal_transpy()
        mkdir_projectspath()
        for project_name, (url, test_func) in PROJECTS.items():
            print("----------------------------\nStart:", project_name)
            os.chdir(PROJECTS_PATH)
            subprocess.call(['git', 'clone', url])
            try:
                project_measures = {}
                transform_project(project_name)
                if should_get_metrics(project_name):
                    if config["test"]:
                        project_measures.update(get_unittest_data(project_name, test_func, config["test_iterations"]))
                    if config["radon"]:
                        project_measures.update(get_radon(project_name))
                    if config["codecov"]:
                        project_measures["test coverage"] = \
                            get_coverage(repo_name=url.split("/")[-2], project_name=url.split("/")[-1])

                    save_data_json(project_measures, project_name)
            except FileNotFoundError:
                print("Filenotfound error ---> cant_find_projects.txt")
                filename = "../cant_find_projects.txt"
                mode = "a" if os.path.exists(filename) else "w"
                with open(filename, mode) as f:
                    f.write(str(project_name) + "\n")

    except KeyboardInterrupt:
        print("*" * 50, "\n           Művelet megszakítva\n", "*" * 50)
        os.chdir(DEFAULT_PATH)
    # except Exception as e:
    #     print("*" * 50, "\nHIBA\n", "*" * 50)
    #     os.chdir(DEFAULT_PATH)
    #     raise e


def mkdir_projectspath():
    if not PROJECTS_PATH.exists():
        os.mkdir(PROJECTS_PATH)


def clone_oroginal_transpy():
    os.chdir(Path(__file__).parent.resolve())
    subprocess.call(['git', 'clone', "https://github.com/Tirasz/transpy.git"])


if __name__ == "__main__":
    main()
