import csv, yaml, os
from typing import List, Dict
from testing.oracle import Oracle
import logging
import sys

query_id = 32

logging.basicConfig(format='%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='(%m-%d) %H:%M:%S',
                    filename='simulate.log', level=logging.INFO)
from pglast import prettify
# the script is to simulate the execution of tester in the CIGES loop

# paths
raw_output_queries_path = "../../experiment_result/12-27-calcite-SC-raw-output/queries/calcite_sales"
classified_queries_path = "../../experiment_result/12-28-calcite-SC-fixed-database/1672297940/"
input_queries_path = "../../benchmarks/calcite_benchmarks/calcite_sales.csv"

print(os.getcwd())

with open("config.yml") as f:
    config = yaml.safe_load(f)

def get_raw_queries(qid: str) -> List[str]:
    queries = []
    if not os.path.exists(f"{raw_output_queries_path}/{qid}.txt"):
        return []
    with open(f"{raw_output_queries_path}/{qid}.txt") as f:
        reader = csv.reader(f)
        for line in reader:
            query = line[0].strip()
            queries.append(query)
    return queries

def get_classified_queries(qid: str) -> Dict:
    classified_queries = {}
    labels = ["equiv_fast", "equiv_slow", "inequiv", "undetermined_slow"]
    for label in labels:
        if not os.path.exists(f"{classified_queries_path}/{label}/calcite_sales-{qid}.csv"):
            continue
        with open(f"{classified_queries_path}/{label}/calcite_sales-{qid}.csv") as f:
            # csv schema: query_id,query,is_equiv,is_faster,exeution_plan,cost,speed_up_ratio
            reader = csv.reader(f)
            _ = next(reader)
            for row in reader:
                output_qid, query, is_equiv, is_faster, _, cost, _ = row
                output_qid = int(output_qid)
                classified_queries[output_qid] = {
                    "query": query,
                    "is_equiv": is_equiv,
                    "is_faster": is_faster,
                    "cost": cost
                }
    return classified_queries

def get_input_queries() -> List[List[str]]:
    queries = []
    with open(input_queries_path) as f:
        reader = csv.reader(f)
        for row in reader:
            queries.append(row)
    return queries



input_queries = get_input_queries()
for qid, input_query in input_queries:
    if int(qid) != query_id:
        continue
    input_query = input_query.lower()
    raw_output_queries = get_raw_queries(qid)
    if len(raw_output_queries) == 0:
        continue
    logging.info(f"query {qid}:")
    classified_output_queries = get_classified_queries(qid)
    logging.info("\n"+prettify(input_query))
    tester_classified_query = {}
    oracle = Oracle(config_json=config, qid=qid)
    oracle.init_generator(input_query)
    conns = []
    for output_qid, query in enumerate(raw_output_queries):
        logging.info(f"testing output query {output_qid}")
        query = query.lower()
        res, conns = oracle.test(query, input_query, conns)
        tester_classified_query[output_qid] = res

    data = []
    for output_qid in tester_classified_query:
        test_res = tester_classified_query[output_qid]
        is_equiv = classified_output_queries[output_qid]["is_equiv"]
        is_faster = classified_output_queries[output_qid]["is_faster"]
        cost = classified_output_queries[output_qid]["cost"]
        data.append([output_qid, test_res, is_equiv, is_faster, cost])
    with open(f"results/{qid}.csv", 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["qid", "test_result", "is_equiv", "is_faster", "cost"])
        writer.writerows(data)
    oracle.clear_counterexample(conns)
    oracle.clean()
