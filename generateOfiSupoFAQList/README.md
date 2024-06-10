## initialize project

```
python3 -m venv venv
source venv/bin/activate
```

## install required packages
```
pip install -r requirements.txt
```

## how to scrape the FAQ from Office Support
run
```
$ python3 generate-qa-list.py
```

## final output
then, the final output will be located under a current timestamp directory like 20240531_113549/qaList.json.