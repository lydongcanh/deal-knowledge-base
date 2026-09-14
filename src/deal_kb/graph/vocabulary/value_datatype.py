"""Datatype of a normalised Value."""

from enum import StrEnum


class ValueDatatype(StrEnum):
    """`canonical_value` is always populated; typed columns are filled when
    the datatype needs correct filtering or comparison."""

    TEXT = "text"
    NUMBER = "number"
    MONEY = "money"
    PERCENT = "percent"
    DATE = "date"
    DATETIME = "datetime"
    DURATION = "duration"
    BOOLEAN = "boolean"
