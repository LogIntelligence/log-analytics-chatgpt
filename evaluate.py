from evaluation.evaluator import evaluate

out_dir = "outputs/ChatGPT/zero_shot"

datasets = ['BGL', 'HDFS', 'Linux', 'HealthApp', 'OpenStack', 'OpenSSH', 'Proxifier', 'HPC', 'Zookeeper', 'Mac',
            'Hadoop', 'Android', 'Windows', 'Apache', 'Thunderbird', 'Spark']

if __name__ == '__main__':
    for dataset in datasets:
        evaluate(f"dataset/{dataset}/{dataset}_2k.log_structured_corrected.csv",
                 f"{out_dir}/{dataset}_2k.log_structured_adjusted.csv")
