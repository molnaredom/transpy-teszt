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
    if 'count' not in content or content['count'] == 0:
        print("nincs COVERAGE-e")
        return None
    for commit in content['results']:  # átlagos esetben csak az első iterációig jut el
        totals = commit['totals']
        if totals is None:
            continue

        coverage = totals.get('coverage', None)
        if coverage is not None:
            return coverage  # legfrissebb coverage
        else:
            print("X Egy sikertelen proba coverage megtalasara")

    print('X No coverage found on any commit')
