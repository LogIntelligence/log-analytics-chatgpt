import re

from chat import config
import openai
import tiktoken
from utils import get_log_messages
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)
import logging


class ChatGPT:
    def __init__(self, model, prompt, demo_format=None, demo_instruct=None):
        openai.api_key = config['OPEN_AI_KEY']
        self.model = model
        self.prompt = prompt
        self.demo_format = demo_format
        self.demo_instruct = demo_instruct

    def num_tokens_from_messages(self, messages):
        """Returns the number of tokens used by a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model(self.model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        if self.model == "gpt-3.5-turbo-0301":  # note: future models may deviate from this
            num_tokens = len(encoding.encode(messages)) + 2
            return num_tokens
        else:
            raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {self.model}. 
            See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
    def get_response(self, messages, request_type=True, demos=None):
        if request_type:
            msg = f"{messages[0][:500]}"
            content = self.prompt.format(msg)
        else:
            msg = "\n".join([f"{i + 1}. `{' '.join(x[:600].split())}`" for i, x in enumerate(messages)])
            content = self.prompt.format(len(messages), msg)
        if demos:
            demo_list = [self.demo_format.format(x[0], x[1]) for x in demos]
            demo_str = "\n".join(demo_list)
            instr = self.demo_instruct + demo_str
            chat_msg = [{'role': 'user', 'content': instr}, {'role': 'user', 'content': content}]
        else:
            chat_msg = [{'role': 'user', 'content': content}]
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=chat_msg,
            temperature=config['TEMPERATURE'],
            frequency_penalty=config['FREQUENCY_PENALTY'],
            presence_penalty=config['PRESENCE_PENALTY']
        )
        if request_type:
            return self.parse_single_log_template(response['choices'][0]['message']['content'], content)
        else:
            return self.parse_batch_log_template(response['choices'][0]['message']['content'], content, logs=messages)

    def parse_single_log_template(self, response, prompt):
        reg = re.compile("`([^`]+)`")
        template = reg.findall(response)
        if len(template) > 0:
            return template[-1], response
        else:
            if "\n" in response.strip():
                logging.warning(prompt)
                logging.warning(response)
                logging.warning("=" * 20)
            return response, response

    def parse_batch_log_template(self, response, prompt, logs=None):
        if "\n\n" in response:
            logging.warning(prompt)
            logging.warning(response)
            response = response.split("\n\n")[0]
            logging.warning("-" * 10)
        reg = re.compile("`([^`]+)`")
        no_logs = len(logs)
        res = []
        templates = response.split("\n")
        templates = [x.strip() for x in templates]
        templates = [x for x in templates if len(x) > 0]
        for i, template in enumerate(templates):
            tmp = reg.findall(template)
            if len(tmp) > 0:
                tmp = tmp[-1]
                res.append(tmp)
        if len(res) < no_logs:
            if len(res) == 1:
                res = res * no_logs
            else:
                logging.error(response)
                logging.error(prompt)
                res = res + res[:1] * (no_logs - len(res))
                logging.error("-" * 10)
                # raise ValueError("Wrong response!")
        elif len(res) > no_logs:
            logging.error(response)
            logging.error(prompt)
            logging.error("-" * 10)
            res = res[:no_logs]

        return res, response
