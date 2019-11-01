json-summarizer
===============

> Summarizes JSON file contents (or native Python data structures)

Ported to run on Python>=3.5 (no longer runs on 2.X):

```sh
python summarize_json.py <file.json>
```

Meant to be used like the following:

```sh
python summarize_json.py <file.json> > summary.md
# Enjoy Markdown's syntax & color highlighting
```

Get simple summary without examples:

```sh
python summarize_json.py <file.json> | grep -v '#' > simple.md
# -v means --invert-match, i.e. see all non-comment lines only
```

#### Original author: [Philip Guo](https://github.com/pgbovine), Edit by: [Jethro Lee](https://github.com/dlemfh)

> This script prints out a summary of your JSON file's contents, essentially inferring a schema using some simple heuristics.

> It comes in handy for understanding the structure of a blob of JSON (or native Python) data that someone else hands to you
without proper documentation. And it can also be used to manually sanity-check files for
outliers, weird values, inconsistencies, etc.
