import yaml
import os

global_config = None
if os.path.exists('global_config.yaml'):
    global_config = yaml.load(open('global_config.yaml', 'r', encoding='utf-8'), Loader=yaml.SafeLoader)

if os.path.exists('../global_config.yaml'):
    global_config = yaml.load(open('../global_config.yaml', 'r', encoding='utf-8'), Loader=yaml.SafeLoader)

if os.path.exists('../../global_config.yaml'):
    global_config = yaml.load(open('../../global_config.yaml', 'r', encoding='utf-8'), Loader=yaml.SafeLoader)
