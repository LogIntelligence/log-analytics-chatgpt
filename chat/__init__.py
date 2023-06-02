"""
Configuration
"""
config = {
    "OPEN_AI_KEY": "<PLACE_YOUR_API_KEY>",
    "MODEL": "gpt-3.5-turbo-0301",
    "TEMPERATURE": 0.0,
    "FREQUENCY_PENALTY": 0.0,
    "PRESENCE_PENALTY": 0.0,
    "ZERO_SHOT_PROMPT": {
        "id": "zero_shot",
        "desc": "without description + with post-processing",
        "sys_msg": {"role": "system",
                    "content": """You will be provided with a log line"""
                    },
        "prompt": """You will be provided with a log message delimited by backticks. You must abstract variables with `{{placeholders}}` to extract the corresponding template.
Print the input log's template delimited by backticks.

Log message: `{0}`
"""
    },
    "FEW_SHOT_PROMPT": {
        "id": "few_shot",
        "desc": "without description + with post-processing",
        "sys_msg": {"role": "system",
                    "content": """You will be provided with a log line."""
                    },
        "demo_format": """The template of `{0}` is `{1}`.""",
        "demo_instruct": """You will be provided with a log message delimited by backticks. You must abstract variables with `{placeholders}` to extract the corresponding template.
For examples:\n""",
        "prompt": """Print the input log's template delimited by backticks.

Log message: `{0}`
"""
    },

    "ZERO_SHOT_SIMPLE_PROMPT": {
        "id": "zero_shot_prompt_simple",
        "desc": "without description + with post-processing",
        "sys_msg": {"role": "system",
                    "content": """You will be provided with a log line"""
                    },
        "prompt": """You will be provided with a log message delimited by backticks. Please extract the log template from this log message:
`{0}`

Log template: """
    },
    "ZERO_SHOT_ENHANCE_PROMPT": {
        "id": "zero_shot_prompt_enhance",
        "desc": "without description + with post-processing",
        "sys_msg": {"role": "system",
                    "content": """You will be provided with a log line"""
                    },
        "prompt": """You will be provided with a log message delimited by backticks. You must identify and abstract all the dynamic variables in logs with `{{placeholders}}` and output a static log template.
Print the input log's template delimited by backticks.
    
Log message: `{0}`"""
    },

}

from .ChatGPT import ChatGPT
