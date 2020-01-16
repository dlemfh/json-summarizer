#!/bin/bash


# cd into tests/
if [[ -d "tests" ]]; then
  cd tests || exit
fi

# summarize all files
for jsonfile in *.json; do
  echo "Summarizing $jsonfile"
  python3 ../summarize_json.py "$jsonfile" > "${jsonfile%%.*}.md"
done
