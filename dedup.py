import argparse
import os
import sys
import json
import pandas as pd

# Author: Daniel Li


def get_all_records(fname):
    if not os.path.exists(fname):
        sys.exit(f'Given file {fname} does not exist, exiting!')
    try:
        with open(fname, 'r') as infile:
            data = json.load(infile)
    except:
        sys.exit(f'Failed to parse data from {fname}, exiting!')

    return data['leads']  # assume leads is always first entry


# get best record for each id. email. both must be unique, then sorted on recent date, then by entry in list
def deduplicate(records):
    df = pd.DataFrame(records)
    # add artificial index for sorting
    df['order'] = range(len(df))

    df = df.sort_values(by=['entryDate', 'order'], ascending=[
                        False, False]).drop_duplicates(subset=['_id'], keep='first')

    df = df.sort_values(by=['entryDate', 'order'], ascending=[
                        False, False]).drop_duplicates(subset=['email'], keep='first')

    df = df.drop(columns=['order'])
    return df


# used to prepared data for log files
def get_differences(record1, record2):
    difference = []

    for key, val1 in record1.items():
        if val1 != record2[key]:
            difference.append(
                f'updated column {key} from {val1} to {record2[key]}')

    return difference


# return records with correct data and log file info
def update_records(records, uniques):

    new_records = {}
    log_changes = []

    for record in records:
        id = record['_id']
        email = record['email']
        by_id_or_email = uniques[(uniques['_id'] == id)
                                 | (uniques['email'] == email)]

        updated_data = by_id_or_email.iloc[0].to_dict()

        original = json.dumps(record)
        new_data = json.dumps(updated_data)

        log_changes.append(
            (original, new_data, get_differences(record, updated_data)))

        new_records[id] = updated_data
    return new_records, log_changes


# write out the log file of changes.
def write_log_file(fname, all_data):
    try:
        with open(fname, 'w') as f:
            # tuple format is original json, update json, and list of changes
            for orig, new_data, change_list in all_data:
                f.write('original entry ' + orig + '\n')
                f.write('updated entry: ' + new_data + '\n')
                for line in change_list:
                    f.write(line + '\n')
                f.write('-------------------------\n')
    except:
        sys.exit(f'Unable to write to {fname}, exiting!')


# write out deduplicated data to outfile
def write_deduplicate_data(outfile, json_data):
    try:
        with open(outfile, 'w') as f:
            json.dump(json_data, f, indent=2)
    except:
        sys.exit(f'Unable to write to {outfile}, exiting!')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help='Input filename. Required')
    parser.add_argument('-l', '--log', default='changes.log',
                        help='Log file to write changes to. Defaults to changes.log.')
    parser.add_argument('-o', '--output', default='out.json',
                        help='Output file after deduplication to write. Defaults to out.jsonn.')
    args = parser.parse_args()

    # first fetch all data
    all_records = get_all_records(args.input)

    # find ground truth records
    uniques = deduplicate(all_records)

    # update data structures for changelog and clean records
    new_records, log = update_records(all_records, uniques)

    # add back original structure
    leads = [{"_id": info["_id"], "email": info["email"], "firstName": info["firstName"], "lastName": info["lastName"],
              "address": info["address"], "entryDate": info["entryDate"]} for info in new_records.values()]

    result = {'leads': leads}

    # write out log file and data
    write_log_file(args.log, log)
    print(f'wrote log file to {args.log}')

    write_deduplicate_data(args.output, result)
    print(f'wrote deduplicated data to {args.output}')


if __name__ == '__main__':
    main()
