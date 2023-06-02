from datasets import load_dataset
import pandas as pd


def load_train_data(r_dir=".", dataset="Apache", shot=4):
    dataset = load_dataset('json', data_files=f'{r_dir}/{dataset}/{4}shot/1.json')
    examples = [(x['text'], x['label']) for x in dataset['train']]
    return examples


def load_test_data(r_dir=".", dataset="Apache"):
    logs = pd.read_csv(f"{r_dir}/{dataset}/{dataset}_2k.log_structured_corrected.csv")
    return logs.Content.tolist()


def get_log_messages(r_dir, dataset, shot=0):
    train, test = [], []
    if shot > 0:
        demos = load_train_data(f"{r_dir}/dataset", dataset, shot)
        for demo in demos:
            train.append((demo[0].strip(), demo[1].strip()))
    test_logs = load_test_data(f"{r_dir}/dataset", dataset)
    for i, log in enumerate(test_logs):
        test.append(log.strip())

    return train, test
