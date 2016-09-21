import requests
import semver

def matrix_join(matrix, separator):
    return separator.join([str(x) for x in matrix if x is not None])

def majorize(version):
    version_info = semver.parse(version)
    return "%d" % (version_info["major"])

def minorize(version):
    version_info = semver.parse(version)
    return "%d.%d" % (version_info["major"], version_info["minor"])

def patchize(version):
    version_info = semver.parse(version)
    return "%d.%d.%d" % (version_info["major"], version_info["minor"], version_info["patch"])

def get_tags(image):
    logstash_version = semver.parse(image)
    logstash_versions = []

    if logstash_version["major"] == 1:
        if logstash_version["minor"] == 5:
            logstash_versions.append("1")
    elif logstash_version["major"] == 2:
        if logstash_version["minor"] == 4:
            logstash_versions.append("2")
            logstash_versions.append("latest")

    logstash_versions.extend([patchize(image), minorize(image), image])

    return logstash_versions

def delete_builds(repo, token):
    headers = {'Authorization': token}
    builds = [];

    response = requests.get("https://hub.docker.com/v2/repositories/%s/autobuild/tags/" % (repo), headers=headers)

    if response.status_code == 200:
        body = response.json()
        builds.extend(body["results"])

        while not (body["next"] is None):
            response = requests.get(body["next"], headers=headers)

            if response.status_code == 200:
                body = response.json()
                builds.extend(body["results"])
            else:
                raise Exception("Invalid response")
    else:
        raise Exception("Invalid response")

    for build in builds:
        requests.delete("https://hub.docker.com/v2/repositories/%s/autobuild/tags/%s/" % (repo, build["id"]), headers=headers)

def add_builds (repo, token, paths, tags):
    headers = {'Authorization': token}

    for i in range(0, len(paths)):
        for tag in tags[i]:
            build = {"name": tag, "dockerfile_location": paths[i], "source_name": "master", "source_type": "Branch", "isNew": True}
            requests.post("https://hub.docker.com/v2/repositories/%s/autobuild/tags/" % (repo), headers=headers, data=build)
