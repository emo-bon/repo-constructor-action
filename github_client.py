from github import Github, GithubException
import base64
import os
import pandas as pd

def create_or_update_file(repo_handle, path, content):
    try:
        repo_handle.create_file(
            path=path,
            content=content,
            message=f"add {path}"
        )
        print(f"successfully created {path}")
    except GithubException as e:
        cf = repo_handle.get_contents(path)
        sha = cf.sha
        content_remote = (
            base64.b64decode(bytes(cf.content, "utf-8")).decode("utf-8")
        )
        if content == content_remote:
            print(f"no change detected in {path}; {e}")
        else:
            repo_handle.update_file(
                path=path,
                content=content,
                sha=sha,
                message=f"update {path}"
            )
            print(f"successfully updated {path}")

if __name__ == "__main__":
    GITHUB_WORKSPACE = "/github/workspace"
    GITHUB = Github(os.environ["PAT"])
    FILE_PATH = os.environ["FILE_PATH"]
    ORG = os.environ["ORG"]
    CHILD_ACTION = os.environ["CHILD_ACTION"]

    df = pd.read_csv(os.path.join(GITHUB_WORKSPACE, FILE_PATH))
    repos = [f"observatory-{obs}-data" for obs in df["EMOBON_observatory_id"]]
    water_urls = [url for url in df["Water Column"]]
    sediment_urls = [url for url in df["Soft sediment"]]

    for repo, water_url, sediment_url in zip(repos, water_urls, sediment_urls):
        print(f">>> {repo}")
        
        # create repo
        try:
            GITHUB.get_organization(ORG).create_repo(repo)
            print(f"successfully created {repo}")
        except GithubException as e:
            print(f"failed to create {repo}; {e}")
        
        # acquire reference to repo
        repo_handle = GITHUB.get_organization(ORG).get_repo(repo)

        # populate repo with google-docs.yml
        path = "./config/google-docs.yml"
        content = (
            f"water: {water_url}\n"
            f"sediment: {sediment_url}\n"
        )
        create_or_update_file(repo_handle, path, content)

        # populate repo with emobon_dm_gdrive_downloader.yml
        path = "./.github/workflows/emobon_dm_gdrive_downloader.yml"
        content = (
            "on:\n"
            "  push:\n"
            "  schedule:\n"
            "    - cron: '0 0 * * *'\n"
            "jobs:\n"
            "  emobon_job:\n"
            "    runs-on: ubuntu-latest\n"
            "    name: emobon dm gdrive downloader job\n"
            "    steps:\n"
            "      - name: checkout\n"
            "        uses: actions/checkout@v3\n"
            "      - name: download\n"
           f"        uses: {CHILD_ACTION}\n"
            "      - name: commit\n"
            "        uses: stefanzweifel/git-auto-commit-action@v4\n"
        )
        create_or_update_file(repo_handle, path, content)

        print()
