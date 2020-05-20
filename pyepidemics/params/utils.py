
import yaml


def read_yaml(filepath):
    return yaml.load(open(filepath,"r").read(),Loader=yaml.UnsafeLoader)