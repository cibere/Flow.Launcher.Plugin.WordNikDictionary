import os
import sys

parent_folder_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(parent_folder_path)
sys.path.append(os.path.join(parent_folder_path, "lib"))
sys.path.append(os.path.join(parent_folder_path, "plugin"))

from WordnikDictionary.core import WordnikDictionaryPlugin
from WordnikDictionary.utils import setup_logging

if __name__ == "__main__":
    setup_logging()
    WordnikDictionaryPlugin()
