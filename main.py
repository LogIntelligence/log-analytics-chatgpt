import os
from chat import ChatGPT, config
from utils import get_log_messages
import pandas as pd
from collections import Counter
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from dataset.data_loader import load_train_data

datasets = ['BGL', 'HDFS', 'Linux', 'HealthApp', 'OpenStack', 'OpenSSH', 'Proxifier', 'HPC', 'Zookeeper', 'Mac',
            'Hadoop', 'Android', 'Windows', 'Apache', 'Thunderbird', 'Spark']

MSG_LEN = 1


def zero_shot_benchmark(model, prompt_template, dataset, out_dir="."):
    chat = ChatGPT(model=model, prompt=prompt_template)
    _, test = get_log_messages("./", dataset, 0)
    log_chunks = []
    for i in tqdm(range(len(test) // MSG_LEN)):
        log_chunks.append(test[i * MSG_LEN: (i + 1) * MSG_LEN])
    with ThreadPoolExecutor(max_workers=16) as executor:
        templates = list(
            tqdm(executor.map(lambda chunk: chat.get_response(chunk, request_type=MSG_LEN == 1), log_chunks),
                 total=len(log_chunks)))
        print("Completed!")
    os.makedirs("logs", exist_ok=True)
    with open(f"logs/{dataset}_{out_dir}.log", mode="w") as f:
        [f.write(x[1] + "\n =================== \n") for x in templates]
    templates = [x[0] for x in templates]
    if MSG_LEN > 1:
        templates = sum(templates, [])
    unique_templates = Counter(templates).items()
    logs_df = pd.read_csv(f"dataset/{dataset}/{dataset}_2k.log_structured_corrected.csv")
    logs_df.EventTemplate = pd.Series(templates)
    temp_df = pd.DataFrame(unique_templates, columns=['EventTemplate', 'Occurrences'])
    os.makedirs(f"outputs/{out_dir}", exist_ok=True)
    logs_df.to_csv(f"outputs/{out_dir}/{dataset}_2k.log_structured.csv")
    temp_df.to_csv(f"outputs/{out_dir}/{dataset}_2k.log_templates.csv")


def few_shot_benchmark(model, demo, prompt_template, demo_format, demo_inst, dataset, out_dir="."):
    chat = ChatGPT(model=model, prompt=prompt_template, demo_format=demo_format, demo_instruct=demo_inst)
    _, test = get_log_messages("./", dataset, 0)
    log_chunks = []
    for i in tqdm(range(len(test) // MSG_LEN)):
        log_chunks.append(test[i * MSG_LEN: (i + 1) * MSG_LEN])
    with ThreadPoolExecutor(max_workers=8) as executor:
        templates = list(
            tqdm(executor.map(lambda chunk: chat.get_response(chunk, demos=demo), log_chunks), total=len(log_chunks)))
        print("Completed!")
    os.makedirs("logs", exist_ok=True)
    with open(f"logs/{dataset}_{out_dir}.log", mode="w") as f:
        [f.write(x[1] + "\n =================== \n") for x in templates]
    templates = [x[0] for x in templates]
    unique_templates = Counter(templates).items()
    logs_df = pd.read_csv(f"dataset/{dataset}/{dataset}_2k.log_structured_corrected.csv")
    logs_df.EventTemplate = pd.Series(templates)
    temp_df = pd.DataFrame(unique_templates, columns=['EventTemplate', 'Occurrences'])
    os.makedirs(f"outputs/{out_dir}", exist_ok=True)
    logs_df.to_csv(f"outputs/{out_dir}/{dataset}_2k.log_structured.csv")
    temp_df.to_csv(f"outputs/{out_dir}/{dataset}_2k.log_templates.csv")


if __name__ == '__main__':
    """ zero-shot benchmark
    """
    prompt = config['ZERO_SHOT_PROMPT']
    print(prompt['prompt'], "-" * 5, prompt['desc'])
    for dname in datasets:
        print(f"============== {dname} ==============")
        zero_shot_benchmark(config['MODEL'], prompt['prompt'], dname, f"{prompt['id']}")

    """ few-shot benchmark
    """
    prompt = config['FEW_SHOT_PROMPT']
    print(prompt['prompt'])
    for shot in [1, 2, 4]:
        print(f"************ {shot} shot ************")
        for dname in datasets:
            print(f"============== {dname} ==============")
            demos = load_train_data(r_dir="./dataset", dataset=dname, shot=shot)
            few_shot_benchmark(config['MODEL'], demos, prompt['prompt'], prompt['demo_format'],
                               prompt['demo_instruct'], dname, f"{prompt['id']}_{shot}")
