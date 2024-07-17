"""Data Summary Node."""

from typing import Dict, Tuple

import pandas as pd
from langchain_core.prompts import ChatPromptTemplate

try:
    from pydantic.v1 import BaseModel, Field
except ImportError:  # pragma: no cov
    from pydantic import BaseModel, Field


def _get_df_info(df: pd.DataFrame) -> Tuple[Dict[str, str], pd.DataFrame]:
    """Get the dataframe schema and head info as strings."""
    formatted_pairs = {col_name: str(dtype) for col_name, dtype in df.dtypes.items()}
    df_sample = df.sample(5)
    return formatted_pairs, df_sample


df_sum_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a data assistant with expertise naming a pandas dataframe. \n
            Inspect the provided data and give a short unique name to the dataset. \n
            Here is the dataframe sample:  \n ------- \n  {df_sample} \n ------- \n
            Here is the schema:  \n ------- \n  {df_schema} \n ------- \n
            AVOID the following names: \n ------- \n {current_df_names} \n ------- \n
            \n ------- \n
            """,
        ),
        ("placeholder", "{messages}"),
    ]
)


class DfInfo(BaseModel):
    """Data Info output."""

    dataset_name: str = Field(pattern=r"^[a-z]+(_[a-z]+)?$", description="Small snake case name of the dataset.")
