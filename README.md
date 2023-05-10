# repo-constructor-action

To give an example, the following workflow file will construct new repos based on the information provided in the metadata file.

```
on: [push]
jobs:
  repo-constructor-action:
    runs-on: ubuntu-latest
    steps:
      - name: checkout
        uses: actions/checkout@v3
      - name: repo constructor action
        uses: emo-bon/repo-constructor-action@master
        env:
          PAT: ${{ secrets.PAT }}
          FILE_PATH: logsheets.csv
          ORG: emo-bon
          CHILD_ACTION: emo-bon/logsheet-downloader-action@master
```

with:

* `PAT`: a personal access token with repo and workflow scopes
* `FILE_PATH`: the path to the metadata file
* `ORG`: the organization in which to construct the new repos
* `CHILD_ACTION`: the action to add in the workflow of a newly constructed repo
