import shutil

from src import CHROMA_DB_PATH


def compress_chroma_db() -> str:
    return shutil.make_archive(str(CHROMA_DB_PATH), "xztar", root_dir=CHROMA_DB_PATH)
