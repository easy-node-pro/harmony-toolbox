import os
from os import environ
from utils.config import validatorToolbox
from utils.installer import cloneShards, loadVarFile
from utils.shared import loaderIntro

if __name__ == "__main__":
    os.system("clear")
    loaderIntro()
    loadVarFile()
    print(
        "* Harmony ONE Validator Shard Downloader"
    )
    cloneShards()