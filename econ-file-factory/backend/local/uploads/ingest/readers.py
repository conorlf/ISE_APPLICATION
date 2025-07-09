import pandas as pd
import csv
import chardet
from typing import Tuple
from io import BytesIO, StringIO


def detect_encoding(sample: bytes) -> str:
    result = chardet.detect(sample)
    return result.get("encoding", "utf-8")


def safe_read_csv(path_or_buf, **kwargs) -> Tuple[pd.DataFrame, dict]:
    """Read a CSV file with auto-detection of delimiter, encoding, quoting.
    Returns (DataFrame, diagnostics_dict)
    """
    diagnostics = {}
    # Read first 32k to guess delimiter & encoding
    if isinstance(path_or_buf, (str, bytes)):
        with open(path_or_buf, "rb") as fh:
            sample_bytes = fh.read(32768)
    else:
        sample_bytes = path_or_buf.read(32768)
        path_or_buf.seek(0)

    encoding = detect_encoding(sample_bytes)
    diagnostics["encoding"] = encoding
    try:
        sample_str = sample_bytes.decode(encoding, errors="ignore")
    except Exception:
        sample_str = sample_bytes.decode("utf-8", errors="ignore")

    # Sniff delimiter
    sniffer = csv.Sniffer()
    try:
        dialect = sniffer.sniff(sample_str)
        delimiter = dialect.delimiter
    except Exception:
        delimiter = ","
    diagnostics["delimiter"] = delimiter

    # quick ragged-row detection: if any line in sample has more delimiters than header -> use manual
    header_delims = sample_str.splitlines()[0].count(delimiter)
    if any(line.count(delimiter) > header_delims for line in sample_str.splitlines()[1:]):
        raise ValueError("ragged rows detected; use manual parser")

    # Read with pandas
    try:
        df = pd.read_csv(
            path_or_buf,
            encoding=encoding,
            sep=delimiter,
            engine="python",
            thousands="," ,
            **kwargs,
        )
        return df, diagnostics
    except Exception as e:
        # fallback: manual CSV parsing with row-repair for ragged lines
        diagnostics["fallback"] = str(e)
        path_or_buf.seek(0)
        text = path_or_buf.read() if isinstance(path_or_buf, BytesIO) else path_or_buf.read()
        if isinstance(text, bytes):
            text = text.decode(encoding, errors="ignore")

        reader = csv.reader(StringIO(text), delimiter=delimiter)
        rows = list(reader)
        if not rows:
            return pd.DataFrame(), diagnostics

        header = rows[0]
        header_len = len(header)

        def _repair_row(row: list[str]) -> list[str]:
            # Merge consecutive digit cells if concatenation forms a >=1000 number
            while len(row) > header_len:
                merged_any = False
                for i in range(len(row) - 1):
                    if row[i].isdigit() and row[i + 1].isdigit():
                        merged = row[i] + row[i + 1]
                        if int(merged) >= 1000:
                            row[i:i + 2] = [merged]
                            merged_any = True
                            break
                if not merged_any:
                    # Cannot repair further; truncate extra cells
                    row = row[:header_len]
            # pad missing cells
            if len(row) < header_len:
                row += [""] * (header_len - len(row))
            return row

        fixed_rows = [_repair_row(r) for r in rows[1:]]
        df = pd.DataFrame(fixed_rows, columns=header)
        return df, diagnostics 