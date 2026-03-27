import os
import yaml

_config_cache = None


def load_config(config_path: str = None) -> dict:
    """加载 YAML 配置文件，带模块级缓存"""
    global _config_cache
    if _config_cache is not None:
        return _config_cache

    if config_path is None:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, "config", "config.yaml")

    with open(config_path, "r", encoding="utf-8") as f:
        _config_cache = yaml.safe_load(f)

    return _config_cache


def reset_config_cache():
    """重置配置缓存（用于测试时切换配置）"""
    global _config_cache
    _config_cache = None
