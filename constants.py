DEFAULTS = {
    'DEFAULT': {
        'IMAGE_DIRECTORY': 'Images',
        'OUTPUT_DIRECTORY': 'Output',
        'API_BASE_URL': 'http://127.0.0.1:7864',
        'API_KEY': '',
        'TIMEOUT': 40,
        'LOGGING_LEVEL': 'DEBUG',
        'LOGGING_FORMAT': '%(message)s',
        'LOG_TO_CONSOLE': True,
        'LOG_TO_FILE': True,
        'LOG_FILE': 'Log.log',
        'LOG_MODE': 'w',
        'LOG_API_COMMUNICATION': True,
        'MODEL': 'ViT-g-14/laion2B-s34B-b88K',
        'CAPTION_TYPES': 'caption,best,fast,classic,negative',
        'ANALYSIS_TYPE': 1,
        'LLM_API_BASE_URL': 'https://api.openai.com/v1/chat/completions',
        'LLM_API_KEY': '',
        'LLM_API_HEADERS': '{"Content-Type": "application/json"}',
        'LLM_SYSTEM_CONTENT': 'Your default system content here',
        'LLM_MODEL': 'gpt-4o',  # Default LLM model
        'SELECTED_PROMPT': 1,
        'IMAGE_FILE_EXTENSIONS': '.png,.jpg,.jpeg',
        'CREATE_INDIVIDUAL_FILES': True,  # Ensure this key is included
        'CREATE_PROMPT_LIST': True,
        'CREATE_MASTER_FILES': True,
        'LIST_FILE_MODE': 'w',
        'MASTER_ANALYSIS_FILENAME': 'master_analysis.json',
        'PROCESS_JSON_WITHOUT_IMAGES': False
    },
    'Prompt Options': {
        '1': {
            'PROCESS_NAME': 'DetailedDescription',
            'PROMPT_TEXT': (
                "Provide a detailed description of the image's content, focusing on essential elements such as key figures, objects, setting, and any significant interactions. "
                "You should not mention anything associated with style like colors, artist names or techniques. "
                "Just describe what is happening in the scene. Ensure the description is clear and comprehensive enough for someone who has never seen the image to accurately recreate it in a painting. "
                "Each answer should be one paragraph per image only."
            ),
            'TEMPERATURE': 0.7,
            'MAX_TOKENS': 100
        },
        '2': {
            'PROCESS_NAME': 'EnhanceDetails',
            'PROMPT_TEXT': "Enhance the image details, making colors more vibrant and edges sharper.",
            'TEMPERATURE': 0.6,
            'MAX_TOKENS': 150
        },
        '3': {
            'PROCESS_NAME': 'ObjectInteraction',
            'PROMPT_TEXT': "Remove any style or art references from the image description, focusing purely on the objects and interactions.",
            'TEMPERATURE': 0.5,
            'MAX_TOKENS': 200
        },
        '4': {
            'PROCESS_NAME': 'DeepDescription',
            'PROMPT_TEXT': "Provide a deep description of the image, including subtle details and background elements.",
            'TEMPERATURE': 0.8,
            'MAX_TOKENS': 250
        },
        '5': {
            'PROCESS_NAME': 'HistoricalAnalysis',
            'PROMPT_TEXT': "Analyze the image for any historical or cultural references, providing context and background information.",
            'TEMPERATURE': 0.9,
            'MAX_TOKENS': 300
        }
    },
    'LLM_1': {
        'ENABLED': True,
        'API_URL': 'https://api.openai.com/v1/chat/completions',
        'API_KEY': ''  # Will be fetched from the environment variable 'OPENAI_API_KEY'
    },
    'LLM_2': {
        'ENABLED': False,
        'API_URL': 'https://example.com/api1',
        'API_KEY': ''
    },
    'LLM_3': {
        'ENABLED': False,
        'API_URL': 'https://example.com/api2',
        'API_KEY': ''
    },
    'LLM_4': {
        'ENABLED': False,
        'API_URL': 'https://example.com/api3',
        'API_KEY': ''
    }
}
