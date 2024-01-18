# repo-constructor-action

To give an example, the following workflow file will construct new repos based on the information provided in the logsheets file.

```
on: [push]
jobs:
  job:
    runs-on: ubuntu-latest
    steps:
      - name: checkout
        uses: actions/checkout@v3
      - name: repo-constructor-action
        uses: emo-bon/repo-constructor-action@master
        env:
          PAT: ${{ secrets.PAT }}
          FILE_PATH: logsheets.csv
          ORG: emo-bon
```

with:

* `PAT`: a personal access token with repo and workflow scopes
* `FILE_PATH`: the path to the metadata file
* `ORG`: the organization in which to construct the new repos
