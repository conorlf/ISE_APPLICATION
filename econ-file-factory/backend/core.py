import pandas as pd
from typing import List, Union
from pathlib import Path

from .ingest.readers import safe_read_csv
from .schema.inference import infer_mapping
from .reshapers.registry import reshape
from .cleaners.registry import clean


class Wrangler:

    @staticmethod
    def run(file_paths: List[Union[str, Path]], api_key=None) -> pd.DataFrame:
        dataframes = []
        sources = []
        for fp in file_paths:
            if str(fp).lower().endswith(".csv"):
                df, diag = safe_read_csv(fp)
            else:
                df = pd.read_excel(fp)
                diag = {}
            dataframes.append(df)
            sources.append(Path(fp).name)
        from normalize_and_merge import normalize_and_merge  # import lazily
        master, *_ = normalize_and_merge(dataframes, sources, api_key=api_key, use_openai=bool(api_key))
        return master 