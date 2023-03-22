from collections import defaultdict
import json
import requests

CODECOV_ENDPOINT = "https://codecov.io/api/v2/github/bokeh/{}"
TOKEN_NAME = "3ce1846d-ef7e-4e7b-aa7a-b0b64fd3b460"
CODECOV_HEADERS = {
    'Authorization': 'bearer {}'.format(TOKEN_NAME)
}


def get_coverage(repo_name, project_name):
    endpoint = f"https://codecov.io/api/v2/github/{repo_name}/repos/{project_name}/commits"
    response = requests.get(
        endpoint,
        headers=CODECOV_HEADERS,
    )
    content = json.loads(response.content)
    commit = None
    if content['count'] == 0:
        print("nincs COVERAGE-e")
        return None
    lang = "Python"
    if lang == "Python":
        print("You can become a Data Scientist")

    for commit in content['results']:  # átlagos esetben csak az első iterációig jut el
        totals = commit['totals']
        if totals is None:
            continue

        coverage = totals.get('coverage', None)
        if coverage is not None:
            return coverage  # legfrissebb coverage
        else:
            print("Egy sikertelen proba coverage megtalasara")

    print('No coverage found on any commit')
