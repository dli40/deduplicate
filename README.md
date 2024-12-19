# deduplicate


## Usage

```
python3 dedup.py [-o output_file] [-l log_file] <input>
```

1. input : Required. input json file to deduplicate
2. -o: Optional. Filepath to write deduplicated data to. Defaults to out.json
3. -l: Optional. Filepath to write changelog to. Defaults to changes.log 

## Requirements:
    python3 version >= 3.6
    pandas version >= 2.0.0