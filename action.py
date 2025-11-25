import base64
import os
import pandas as pd
import yaml
from pathlib import Path
from github import Github, GithubException

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
    GITHUB_WORKSPACE = Path(os.getenv("GITHUB_WORKSPACE"))
    OCTOKIT = Github(os.getenv("PAT"))

    df = pd.read_csv(GITHUB_WORKSPACE / "logsheets.csv")
    df = df[df["autogenerate"] == 1]
    repos = [f"observatory-{obs.lower()}-crate" for obs in df["EMOBON_observatory_id"]]
    water_urls = [url for url in df["Water Column"]]
    sediment_urls = [url for url in df["Soft sediment"]]
    hard_urls = [url for url in df["Hard_substrates"]]
    data_quality_control_threshold_dates = [date for date in df["data_quality_control_threshold_date"]]
    data_quality_control_assignees = [assignee for assignee in df["data_quality_control_assignee"]]
    rocrate_profile_uris = [uri for uri in df["rocrate_profile_uri"]]

    for repo, water_url, sediment_url, hard_url, data_quality_control_threshold_date, data_quality_control_assignee, rocrate_profile_uri in zip(repos, water_urls, sediment_urls, hard_urls, data_quality_control_threshold_dates, data_quality_control_assignees, rocrate_profile_uris):
        organization = OCTOKIT.get_organization("emo-bon")

        # create repo
        try:
            organization.create_repo(repo)
            print(f"successfully created {repo}")
        except GithubException as e:
            print(f"failed to create {repo}; {e}")
        
        # acquire reference to repo
        repo_handle = organization.get_repo(repo)

        # generate workflow file
        with open("/opt/workflow_template.yml", "r") as f:
            workflow = yaml.load(f, loader=yaml.BaseLoader)
        
        workflow["jobs"]["job"]["env"]["ROCRATE_PROFILE_URI"] = rocrate_profile_uri
        workflow["jobs"]["job"]["env"]["WATER_LOGSHEET_URL"] = water_url
        workflow["jobs"]["job"]["env"]["SEDIMENT_LOGSHEET_URL"] = sediment_url
        workflow["jobs"]["job"]["env"]["HARD_LOGSHEET_URL"] = hard_url
        workflow["jobs"]["job"]["env"]["DATA_QUALITY_CONTROL_THRESHOLD_DATE"] = data_quality_control_threshold_date
        workflow["jobs"]["job"]["env"]["DATA_QUALITY_CONTROL_ASSIGNEE"] = data_quality_control_assignee

        # commit workflow file
        create_or_update_file(
            repo_handle=repo_handle,
            path="./.github/workflows/workflow.yml",
            content=yaml.dump(workflow, default_flow_style=False)
        )
