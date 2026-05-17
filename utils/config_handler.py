"""
读取 YAML 配置文件。

参考项目中：
- config/rag.yml 管模型
- config/chroma.yml 管向量库和切分
- config/prompts.yml 管 prompt 路径
"""

import yaml

from utils.path_tool import get_abs_path


def load_yaml_config(config_path: str, encoding: str = "utf-8"):
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def load_rag_config(config_path: str = get_abs_path("config/rag.yml")):
    return load_yaml_config(config_path)


def load_chroma_config(config_path: str = get_abs_path("config/chroma.yml")):
    return load_yaml_config(config_path)


def load_prompts_config(config_path: str = get_abs_path("config/prompts.yml")):
    return load_yaml_config(config_path)


rag_conf = load_rag_config()
chroma_conf = load_chroma_config()
prompts_conf = load_prompts_config()
