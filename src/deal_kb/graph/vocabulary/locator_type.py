"""How an Evidence locator should be interpreted."""

from enum import StrEnum


class LocatorType(StrEnum):
    """The locator payload is only meaningful alongside its type."""

    TEXT_SPAN = "text_span"
    PDF_REGION = "pdf_region"
    PAGE = "page"
    SECTION = "section"
    SPREADSHEET_CELL = "spreadsheet_cell"
    SPREADSHEET_RANGE = "spreadsheet_range"
    SLIDE_REGION = "slide_region"
    STRUCTURED_RECORD = "structured_record"
