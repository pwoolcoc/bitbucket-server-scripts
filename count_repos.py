# coding: utf-8

import requests
from requests.auth import HTTPBasicAuth

"""
CHANGE THESE!
"""
URL = "https://fqdn.of.bitbucket.server"
(USER, PASS) = ("username", "password")
"""
/END
"""

PROJECTS_URL = "{url}/rest/api/1.0/projects".format(url=URL)
REPOS_URL = lambda key: "{url}/rest/api/1.0/projects/{key}/repos".format(url=URL, key=key)
LIMIT = 25

def projects():
    start = 0
    while True:
        r = requests.get(PROJECTS_URL, params={"start": start, "limit": LIMIT}, auth=HTTPBasicAuth(USER, PASS))
        if r.status_code == 200:
            j = r.json()
            for project in j['values']:
                yield project
            if j['isLastPage']:
                break
            else:
                start = j['start'] + j['size']
        else:
            print("exiting, got non-200 response: {0} {1}".format(r, r.text))
            break

def repos(project_key):
    start = 0
    while True:
        url = REPOS_URL(project_key)
        r = requests.get(REPOS_URL(project_key), params={"start": start, "limit": LIMIT}, auth=HTTPBasicAuth(USER, PASS))
        if r.status_code == 200:
            j = r.json()
            for repo in j['values']:
                if repo is not None:
                    yield repo
            if j['isLastPage']:
                break
            else:
                start = j['start'] + j['size']
        else:
            print("exiting, got non-200 reponse: {0} {1}".format(r, r.text))
            break

def sizes(repo):
    project = repo.get('project').get('key')
    slug = repo.get('slug')
    baseurl = "{url}/projects/{project}".format(url=URL, project=project)
    url = "{url}/repos/{slug}/sizes".format(url=baseurl, slug=slug)
    r = requests.get(url, auth=HTTPBasicAuth(USER, PASS))
    if r.status_code == 200:
        j = r.json()
        return j
    else:
        # uncomment if you're having issues
        # print("Couldn't get size for {project}/{slug}: status was {status}".format(project=project, slug=slug, status=r.status_code))
        return None

def count(sizes):
    repository_total = 0
    attachments_total = 0
    for result in results:
        r = result.get('repository', 0)
        a = result.get('attachments', 0)
        repository_total += r
        attachments_total += a
    return (repository_total, attachments_total)


if __name__ == '__main__':
    print("getting list of projects...", end='', flush=True)
    keys = set(p.get('key') for p in projects())
    print("Done", flush=True)

    print("getting list of repositories...", end='', flush=True)
    allrepos = [r for key in keys for r in repos(key)]
    print("Done", flush=True)

    total = len(allrepos)
    print("Counted {0} total repositories in {1} projects".format(total, len(keys)))

    results = []
    for i, repo in enumerate(allrepos):
        print("querying for the size of each repository. (this could take a while)", end='', flush=True)
        s = sizes(repo)
        print(" {}/{}...".format(i + 1, total), end='\r', flush=True)
        if s is not None:
            results.append(s)

    repository_total, attachments_total = count(results)
    print("Done")

    print("got sizes from {} repositories".format(len(results)))
    print("total repository size: {}\ntotal attachments size: {}".format(repository_total, attachments_total))
