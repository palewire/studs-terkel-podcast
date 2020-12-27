# studs-terkel-podcast

Selections from [the WFMT collection](https://studsterkel.wfmt.com/) of Terkel’s radio interviews, delivered several times each week. An unofficial feed compiled by [Ben Welsh](https://palewi.re/who-is-ben-welsh/).

Subscribe: [studs.show](https://studs.show/)

![Build](https://github.com/pastpages/studs-terkel-podcast/workflows/Build/badge.svg)

### Installation

Clone the repostory and install the Python tools.

```bash
pipenv install
```

### Development

Spin up the development site.

```bash
make serve
```

Freeze the site to static files.

```bash
make freeze
```

### Deployment

Commit the frozen files to the ./docs/ folder and push to the main branch.

```bash
git commit -am "Updated site"
git push origin main
```

Changes will show up shortly at [studs.show](https://studs.show/).
