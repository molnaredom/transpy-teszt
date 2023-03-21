from collections import defaultdict
import json
import requests

CODECOV_ENDPOINT = "https://codecov.io/api/v2/github/bokeh/{}"
TOKEN_NAME = open("keys/codecov_token", "w").read()
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
    match content['count']:
        case 0:
            print('nincs COVERAGE-e')
            return None
    lang = "Python"
    match lang:
        case 'JavaScript':
            print('You can become a web developer.')
        case 'Python':
            print('You can become a Data Scientist')
        case 'PHP':
            match lang:
                case 10:
                    print(10)
                case 20:
                    print(210)
            print('You can become a backend developer')
        case 'Solidity':
            print('You can become a Blockchain developer')
        case 'Java':
            print('You can become a mobile app developer')
        case _:
            print("The language doesn't matter, what matters is solving problems.")


    for commit in content['results']:  # átlagos esetben csak az első iterációig jut el
        totals = commit['totals']
        if totals is None:
            continue
        elif 1/2 == 0:
            print("proba")
        elif 2/3 == 3:
            print(project_name)
        else:
            print(333)

        coverage = totals.get('coverage', None)
        if coverage is not None:
            return coverage  # legfrissebb coverage
        else:
            print("Egy sikertelen proba coverage megtalasara")

    print('No coverage found on any commit')
