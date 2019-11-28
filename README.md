json-summarizer
===============

> Summarizes JSON file contents (or native Python data structures)

<br/>

Ported to run on Python>=3.5 (No longer runs on 2.X):

```sh
python3 summarize_json.py <file.json>
```

Meant to be used like the following:

```sh
python3 summarize_json.py <file.json> > summary.md
# Enjoy Markdown's syntax & color highlighting
```

Get simple summary without examples:

```sh
python3 summarize_json.py <file.json> | grep -v '#' > simple.md
# -v means --invert-match, i.e. see all non-comment lines only
```

Or use a script like following, to summarize all json files in directory:

```sh
for f in *.json; do                 # For all json files:
{
   echo "$f"                        # print file name
   python3 summarize_json.py "$f"   # print summary
} >> summaries.md                   # into this output file
done
```

## Sample input/output

<details><summary>[INPUT] <i>colors.json</i></summary>
<p>

```json
[
  {
    "color": "black",
    "category": "hue",
    "type": "primary",
    "code": {
      "rgba": [255,255,255,1],
      "hex": "#000"
    }
  },
  {
    "color": "red",
    "category": "hue",
    "type": "primary",
    "code": {
      "rgba": [255,0,0,1],
      "hex": "#FF0"
    }
  },
  {
    "color": "blue",
    "category": "hue",
    "type": "primary",
    "code": {
      "rgba": [0,0,255,1],
      "hex": "#00F"
    }
  },
  {
    "color": "yellow",
    "category": "hue",
    "type": "primary",
    "code": {
      "rgba": [255,255,0,1],
      "hex": "#FF0"
    }
  },
  {
    "color": "green",
    "category": "hue",
    "type": "secondary",
    "code": {
      "rgba": [0,255,0,1],
      "hex": "#0F0"
    }
  }
]
```

</p>
</details>

<details><summary>[OUTPUT] <i>summary.md</i></summary>
<p>

```py
# LEN: 5
[
    {
        'color': str,
          # 'black'{1}, ...[5 singleton(s)]
        'category': str,
          # 'hue'{5} [1 uniq val(s)]
        'type': str,
          # 'primary'{4}, 'secondary'{1} [2 uniq val(s)]
        'code': {
            'rgba': [
              # LEN: 4
                int,
                  # 255{8}, 0{7}, 1{5}
            ],
            'hex': str,
              # '#FF0'{2}, '#000'{1}, ...[4 uniq val(s)]
        },
    },
]
```

</p>
</details>

----------

#### Original author: [Philip Guo](https://github.com/pgbovine), Edit by: [Jethro Lee](https://github.com/dlemfh)

> This script prints out a summary of your JSON file's contents, essentially inferring a schema using some simple heuristics.

> It comes in handy for understanding the structure of a blob of JSON (or native Python) data that someone else hands to you
without proper documentation. And it can also be used to manually sanity-check files for
outliers, weird values, inconsistencies, etc.
