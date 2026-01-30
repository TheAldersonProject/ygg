"""DsPy CLI"""

import os
from typing import Literal

from dotenv import load_dotenv
from dspy import Signature
from pydantic import BaseModel, Field

from ygg.utils.custom_decorators import singleton


class TableColumn(BaseModel):
    column: str = Field(description="Column name")
    data_type: str = Field(description="Data type")
    description: str = Field(description="Description")
    businessName: str = Field(description="Business friendly name")
    primaryKey: Literal[True, False] | None = Field(
        default=False,
        description="Whether the column can be used as a primary key, multiple columns can be set true. Rely on nullables count on the summary to make the decision.",
    )
    uniqueKey: Literal[True, False] | None = Field(
        default=False, description="Whether the column can be used as a unique key, if not sure, set false."
    )
    dateOrTimestamp: Literal[True, False] | None = Field(
        default=False, description="Whether the column is or not a date or timestamp, if not sure, set false."
    )
    dateOrTimestampType: Literal["date", "timestamp", "timestamp_ntz", "timestamp_ltz"] | None = Field(
        default=None, description="Date or timestamp type if the column is a date or timestamp."
    )
    dateOrTimestampPagination: Literal[True, False] | None = Field(
        default=False,
        description="Whether the column is or not a date or timestamp to be used for start point for pagination.",
    )
    examples: list[str] | None = Field(default_factory=list, description="List of examples, maximum of 5.")


class Table(BaseModel):
    name: str = Field(description="Table name")
    schemaName: str = Field(description="Schema name")
    description: str = Field(description="Description")
    businessName: str = Field(description="Human friendly name")
    tags: list[str] = Field(description="List of relevant tags")
    # columns: list[TableColumn] = Field(description="List of columns")
    dataGranularityDescription: str = Field(
        description="Granular level of the data in the object",
        examples=["Aggregation by country"],
    )


class TableColumns(BaseModel):
    model: list[TableColumn] = Field(description="List of columns")


@singleton
class DsPyCli:
    """DsPy CLI"""

    def __init__(self):
        """Initialize DsPy CLI"""
        self.dspy = None
        self._configure()

    def _configure(self):
        """Configure DsPy CLI"""

        if not self.dspy:
            import dspy

            load_dotenv()
            gemini_key = os.getenv("GEMINI_API_KEY")
            lm = dspy.LM("gemini/gemini-3-flash-preview", api_key=gemini_key)
            dspy.configure(lm=lm)

            self.dspy = dspy

    def basic_predict(self, content: str):
        """Predict"""

        class TextTract(Signature):
            input: str = self.dspy.InputField()
            model: Table = self.dspy.OutputField()

        module = self.dspy.Predict(TextTract)
        response = module(input=content)

        return response

    def columns_predict(self, authoritative_definition: str, data_sample_summary: str, data_sample: str):
        """Predict"""

        class TextTract(Signature):
            authoritativeDefinition: str = self.dspy.InputField(
                descr="Authoritative definition of the source table or view."
            )
            dataSampleSummary: str = self.dspy.InputField(
                descr="Markdown formatted summary of data representing up to 20% of the data."
            )
            dataSample: str = self.dspy.InputField(
                descr="Markdown formatted sample of data representing up to 20% of the data."
            )
            model: list[TableColumn] = self.dspy.OutputField()

        module = self.dspy.Predict(TextTract)
        response = module(
            authoritativeDefinition=authoritative_definition,
            dataSampleSummary=data_sample_summary,
            dataSample=data_sample,
        )

        return response
