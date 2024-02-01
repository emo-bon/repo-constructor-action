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

    df = pd.read_csv(os.path.join(GITHUB_WORKSPACE, FILE_PATH))
    df = df[df["autogenerate"] == 1]
    repos = [f"observatory-{obs.lower()}-crate" for obs in df["EMOBON_observatory_id"]]
    water_urls = [url for url in df["Water Column"]]
    sediment_urls = [url for url in df["Soft sediment"]]
    data_quality_control_threshold_dates = [date for date in df["data_quality_control_threshold_date"]]
    rocrate_profile_uris = [uri for uri in df["rocrate_profile_uri"]]

    for repo, water_url, sediment_url, data_quality_control_threshold_date, rocrate_profile_uri in zip(repos, water_urls, sediment_urls, data_quality_control_threshold_dates, rocrate_profile_uris):
        print(f">>> {repo}")
        
        # create repo
        try:
            GITHUB.get_organization(ORG).create_repo(repo)
            print(f"successfully created {repo}")
        except GithubException as e:
            print(f"failed to create {repo}; {e}")
        
        # acquire reference to repo
        repo_handle = GITHUB.get_organization(ORG).get_repo(repo)

        # populate repo with README.md
        path = "./README.md"
        content = (
            f"# {repo}\n"
            "This repository is an RO-Crate containing the harvested EMO BON logsheets for this observatory, along with their representation as linked data.\n"
        )
        create_or_update_file(repo_handle, path, content)

        # populate repo with workflow.yml
        path = "./.github/workflows/workflow.yml"
        content = (
            "on:\n"
            "  workflow_dispatch:\n"
            "  schedule:\n"
            "    - cron: '0 0 1 */6 *'\n"
            "jobs:\n"
            "  job:\n"
            "    runs-on: ubuntu-latest\n"
            "    env:\n"
           f"      ROCRATE_PROFILE_URI: {rocrate_profile_uri}\n"
            "    steps:\n"
            "      - name: checkout\n"
            "        uses: actions/checkout@v3\n"
            "      - name: download\n"
            "        uses: emo-bon/logsheet-downloader-action@master\n"
            "      - name: data-quality-control-action\n"
            "        uses: emo-bon/data-quality-control-action@main\n"
            "        env:\n"
            "          PAT: ${{ secrets.GITHUB_TOKEN }}\n"
            "          REPO: ${{ github.repository }}\n"
            "          ASSIGNEE: bulricht\n"
            "      - name: rocrate-sembench-setup\n"
            "        uses: vliz-be-opsci/rocrate-sembench-setup@main\n"
            "        env:\n"
            "          PROFILE: ${{ env.ROCRATE_PROFILE_URI }}\n"
            "      - name: semantify\n"
            "        uses: vliz-be-opsci/semantify@main\n"
            "      - name: rocrate-metadata-generator-action\n"
            "        uses: emo-bon/rocrate-metadata-generator-action@main\n"
            "        env:\n"
            "          PROFILE: ${{ env.ROCRATE_PROFILE_URI }}\n"
            "          REPO: ${{ github.repository }}\n"
            "      - name: rocrate-to-pages\n"
            "        uses: vliz-be-opsci/rocrate-to-pages@latest\n"
            "        with:\n"
            "          multiple_rocrates: true\n"
            "          release_management: false\n"
            "          include_draft: false\n"
            "          index_html: false\n"
            "      - name: actions-gh-pages\n"
            "        uses: peaceiris/actions-gh-pages@v3\n"
            "        with:\n"
            "          github_token: ${{ secrets.GITHUB_TOKEN }}\n"
            "          publish_dir: ./unicornpages\n"
            "      - name: git-auto-commit-action\n"
            "        uses: stefanzweifel/git-auto-commit-action@v5\n"
            "        with:\n"
            "          commit_message: workflow run\n"
        )
        create_or_update_file(repo_handle, path, content)

        # populate repo with workflow_properties.yml
        path = "./config/workflow_properties.yml"
        content = (
            f"water: {water_url}\n"
            f"sediment: {sediment_url}\n"
            f"data_quality_control_threshold_date: {data_quality_control_threshold_date}\n"
        )
        create_or_update_file(repo_handle, path, content)

        print()
