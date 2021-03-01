#! /usr/bin/env python3
import sys
import os
import csv


def read_stats(f):
    with open(f, "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)
        res = {
            "total_files": 0,
            "total_inserted": 0,
            "total_deleted": 0,
            "total_modified": 0,
            "files": {},
            "total_test_files": 0,
            "total_test_inserted": 0,
            "total_test_deleted": 0,
            "total_test_modified": 0,
            "test_files": {},
        }
        for row in csv_reader:
            if "test" in row[3]:
                res["test_files"] = {row[3]: {
                    "inserted": int(row[0]),
                    "deleted": int(row[1]),
                    "modified": int(row[2])}}
                res["total_test_files"] += 1
                res["total_test_inserted"] += int(row[0])
                res["total_test_deleted"] += int(row[1])
                res["total_test_modified"] += int(row[2])
            else:
                res["files"] = {row[3]: {
                    "inserted": int(row[0]),
                    "deleted": int(row[1]),
                    "modified": int(row[2])}}
                res["total_files"] += 1
                res["total_inserted"] += int(row[0])
                res["total_deleted"] += int(row[1])
                res["total_modified"] += int(row[2])
        if res["total_files"] == 0 and res["total_test_files"] == 0:
            print("{}: is empty".format(f))
        return res


def get_avg(res, key):
    return sum(d[key] for d in res) / len(res)


if len(sys.argv) != 2:
    sys.exit("usage: get_stats.py DIR")

directory = sys.argv[1]

results = []
for d in os.listdir(directory):
    for lang in os.listdir(os.path.join(directory, d)):
        print("Process: {}/{}".format(d, lang))
        for i in os.listdir(os.path.join(directory, d, lang)):
            f = os.path.join(directory, d, lang, i)
            results.append(read_stats(f))
print("Average files per fix: {}".format(get_avg(results, "total_files")))
print("Average insertions per fix: {}".format(get_avg(results, "total_inserted")))
print("Average deletions per fix: {}".format(get_avg(results, "total_deleted")))
print("Average modified lines per fix: {}".format(get_avg(results, "total_modified")))
