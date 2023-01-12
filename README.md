# emobon_dm_repo_constructor

To give an example, the following workflow file will construct new repos based on the information provided in the metadata file.

```
on: [push]
jobs:
  emobon_dm_repo_constructor:
    runs-on: ubuntu-latest
    steps:
      - name: checkout
        uses: actions/checkout@v3
      - name: emobon dm repo constructor
        uses: emo-bon/emobon_dm_repo_constructor@master
        env:
          PAT: ${{ secrets.PAT }}
          FILE_PATH: EMO_BON_metadata_links.csv
          ORG: emo-bon
          CHILD_ACTION: emo-bon/emobon_dm_gdrive_downloader@master
```

with:

* `PAT`: a personal access token with repo and workflow scopes
* `FILE_PATH`: the path to the metadata file
* `ORG`: the organization in which to construct the new repos
* `CHILD_ACTION`: the action to add in the workflow of a newly constructed repo
