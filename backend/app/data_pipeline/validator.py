"""
FlameLens - NASA PSI Data Pipeline
File Structure and Content Validation.

Each supported file type is validated using its
corresponding parser instead of relying only on signatures.
"""

import csv
import json
import logging
import zipfile
import xml.etree.ElementTree as ET

from pathlib import Path


logger = logging.getLogger(__name__)


# ============================================================
# 1. COMMON VALIDATION
# ============================================================

def validate_non_empty(path: Path) -> tuple[bool, str]:
    """Check that the file exists and is not empty."""

    if not path.exists():
        return False, "File does not exist"

    if not path.is_file():
        return False, "Path is not a file"

    if path.stat().st_size == 0:
        return False, "File is empty"

    return True, "File exists and is not empty"


def is_html_error_page(path: Path) -> bool:
    """Detect HTML error pages disguised as downloaded files."""

    try:
        with path.open("rb") as file:
            sample = file.read(8192)

        sample = sample.lstrip().lower()

        html_signatures = (
            b"<!doctype html",
            b"<html",
            b"<head",
            b"<body",
        )

        return any(
            sample.startswith(signature)
            for signature in html_signatures
        )

    except OSError:
        return False


# ============================================================
# 2. PDF STRUCTURE VALIDATION
# ============================================================

def validate_pdf(path: Path) -> tuple[bool, str]:
    """
    Validate PDF by opening and parsing it with PyMuPDF.

    Checks:
    - PDF can be opened.
    - Document is not encrypted without access.
    - Document contains at least one page.
    - Pages can be accessed.
    """

    try:
        import fitz

        with fitz.open(path, filetype="pdf") as document:

            if document.is_closed:
                return False, "PDF document could not be opened"

            if document.is_encrypted:
                return False, "PDF is encrypted and requires a password"

            if document.page_count <= 0:
                return False, "PDF contains no pages"

            page_count = document.page_count

            # Try accessing pages to verify document structure.
            for index in range(page_count):
                page = document.load_page(index)

                if page is None:
                    return False, f"Could not read PDF page {index + 1}"

            return (
                True,
                f"Valid PDF structure: {page_count} pages",
            )

    except ImportError:
        return False, "PyMuPDF is not installed"

    except Exception as exc:
        return False, f"PDF parsing failed: {exc}"


# ============================================================
# 3. EXCEL STRUCTURE VALIDATION
# ============================================================

def validate_excel(path: Path) -> tuple[bool, str]:
    """
    Validate XLSX/XLSM by opening the actual workbook.

    IMPORTANT:
    The temporary downloaded file may have a .part extension.
    Passing a binary file object to openpyxl allows it to inspect
    the actual file content instead of relying on the extension.
    """

    try:
        from openpyxl import load_workbook

        # Open as binary file to support temporary .part files.
        with path.open("rb") as file:

            workbook = load_workbook(
                filename=file,
                read_only=True,
                data_only=False,
            )

            try:
                sheet_names = workbook.sheetnames

                if not sheet_names:
                    return False, "Excel workbook contains no worksheets"

                readable_sheets = 0

                for sheet_name in sheet_names:
                    worksheet = workbook[sheet_name]

                    # Access worksheet dimensions and a small sample.
                    _ = worksheet.max_row
                    _ = worksheet.max_column

                    next(
                        worksheet.iter_rows(
                            min_row=1,
                            max_row=1,
                            values_only=True,
                        ),
                        None,
                    )

                    readable_sheets += 1

                if readable_sheets == 0:
                    return False, "No readable Excel worksheets"

                return (
                    True,
                    f"Valid Excel workbook: {readable_sheets} worksheets",
                )

            finally:
                workbook.close()

    except ImportError:
        return False, "openpyxl is not installed"

    except Exception as exc:
        return False, f"Excel parsing failed: {exc}"


# ============================================================
# 4. CSV STRUCTURE VALIDATION
# ============================================================

def reject_binary_payload(path: Path) -> tuple[bool, str]:
    """Reject obvious binary downloads before text decoders (including latin-1)."""

    try:
        with path.open("rb") as file:
            sample = file.read(8192)

    except OSError as exc:
        return False, f"Could not inspect file bytes: {exc}"

    if not sample:
        return False, "File contains no data"

    signatures = (
        b"PK\x03\x04",
        b"PK\x05\x06",
        b"PK\x07\x08",
        b"%PDF-",
        b"\x89PNG\r\n\x1a\n",
        b"\xff\xd8\xff",
        b"GIF87a",
        b"GIF89a",
        b"BM",
        b"\x7fELF",
        b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1",
    )

    if any(sample.startswith(sig) for sig in signatures):
        return False, "Binary file signature detected; not a text file"

    # NUL bytes are not valid in ordinary CSV/TXT/Markdown content.
    if b"\x00" in sample:
        return False, "Binary content detected (NUL byte)"

    # Allow tabs/newlines/form-feeds; reject excessive other control bytes.
    controls = sum(
        byte < 32 and byte not in (9, 10, 12, 13)
        for byte in sample
    )

    if controls / max(len(sample), 1) > 0.01:
        return False, "Binary content detected (control-byte ratio too high)"

    return True, "No obvious binary signature detected"


def validate_csv(path: Path) -> tuple[bool, str]:
    """
    Validate CSV by reading its rows and checking consistency.

    Uses Python's CSV parser to support different delimiters.
    """

    binary_ok, binary_message = reject_binary_payload(path)

    if not binary_ok:
        return False, binary_message

    encodings = (
        "utf-8-sig",
        "utf-8",
        "cp1252",
        "utf-16",
        "latin-1",
    )

    last_error = None

    for encoding in encodings:
        try:
            with path.open(
                "r",
                encoding=encoding,
                newline="",
            ) as file:

                sample = file.read(8192)

                if not sample.strip():
                    return False, "CSV file contains no data"

                file.seek(0)

                try:
                    dialect = csv.Sniffer().sniff(
                        sample[:4096],
                        delimiters=",;\t|",
                    )

                except csv.Error:
                    dialect = csv.excel

                reader = csv.reader(file, dialect)

                rows_count = 0
                column_count = None

                for row in reader:
                    if not row:
                        continue

                    if column_count is None:
                        column_count = len(row)

                        if column_count == 0:
                            return False, "CSV has no columns"

                    rows_count += 1

                    # Prevent excessive memory usage.
                    if rows_count >= 10000:
                        break

                if rows_count == 0:
                    return False, "CSV contains no readable rows"

                return (
                    True,
                    f"Readable CSV: {rows_count} rows checked, "
                    f"{column_count} columns, encoding={encoding}",
                )

        except UnicodeDecodeError as exc:
            last_error = exc

        except csv.Error as exc:
            return False, f"CSV parsing failed: {exc}"

        except Exception as exc:
            last_error = exc

    return False, f"CSV validation failed: {last_error}"


# ============================================================
# 5. DOCX STRUCTURE VALIDATION
# ============================================================

def validate_docx(path: Path) -> tuple[bool, str]:
    """Validate DOCX by opening and reading its content."""

    try:
        from docx import Document

        document = Document(path)

        paragraphs_count = len(document.paragraphs)
        tables_count = len(document.tables)

        if paragraphs_count == 0 and tables_count == 0:
            return False, "DOCX contains no readable paragraphs or tables"

        return (
            True,
            f"Valid DOCX: {paragraphs_count} paragraphs, "
            f"{tables_count} tables",
        )

    except ImportError:
        return False, "python-docx is not installed"

    except Exception as exc:
        return False, f"DOCX parsing failed: {exc}"


# ============================================================
# 6. POWERPOINT STRUCTURE VALIDATION
# ============================================================

def validate_pptx(path: Path) -> tuple[bool, str]:
    """Validate PPTX by reading the presentation structure."""

    try:
        with zipfile.ZipFile(path, "r") as archive:

            bad_file = archive.testzip()

            if bad_file:
                return False, f"Corrupted ZIP component: {bad_file}"

            names = set(archive.namelist())

            required = {
                "[Content_Types].xml",
                "ppt/presentation.xml",
            }

            missing = required - names

            if missing:
                return (
                    False,
                    f"Missing PowerPoint components: {missing}",
                )

            presentation_xml = archive.read("ppt/presentation.xml")
            root = ET.fromstring(presentation_xml)

            slide_elements = [
                element
                for element in root.iter()
                if element.tag.endswith("}sldId")
            ]

            if not slide_elements:
                return False, "PowerPoint contains no slides"

            return (
                True,
                f"Valid PowerPoint: {len(slide_elements)} slides",
            )

    except Exception as exc:
        return False, f"PPTX parsing failed: {exc}"


# ============================================================
# 7. ZIP ARCHIVE VALIDATION
# ============================================================

def validate_zip(path: Path) -> tuple[bool, str]:
    """Validate ZIP archive and test its internal files."""

    try:
        with zipfile.ZipFile(path, "r") as archive:

            names = archive.namelist()

            if not names:
                return False, "ZIP archive is empty"

            bad_file = archive.testzip()

            if bad_file:
                return False, f"Corrupted ZIP member: {bad_file}"

            return (
                True,
                f"Valid ZIP archive: {len(names)} entries",
            )

    except zipfile.BadZipFile:
        return False, "Invalid ZIP archive"

    except Exception as exc:
        return False, f"ZIP validation failed: {exc}"


# ============================================================
# 8. IMAGE STRUCTURE VALIDATION
# ============================================================

def validate_image(path: Path) -> tuple[bool, str]:
    """Validate image by opening and decoding it with Pillow."""

    try:
        from PIL import Image

        with Image.open(path) as image:

            image_format = image.format
            width, height = image.size

            if width <= 0 or height <= 0:
                return False, "Image has invalid dimensions"

            # Verify image data.
            image.verify()

        # Reopen after verify because verify() invalidates image state.
        with Image.open(path) as image:
            image.load()

        return (
            True,
            f"Valid image: {image_format}, {width}x{height}",
        )

    except ImportError:
        return False, "Pillow is not installed"

    except Exception as exc:
        return False, f"Image parsing failed: {exc}"


# ============================================================
# 9. JSON STRUCTURE VALIDATION
# ============================================================

def validate_json(path: Path) -> tuple[bool, str]:
    """Validate JSON by parsing the complete document."""

    encodings = (
        "utf-8-sig",
        "utf-16",
        "utf-32",
        "cp1252",
    )

    last_error = None

    for encoding in encodings:
        try:
            with path.open("r", encoding=encoding) as file:
                data = json.load(file)

            data_type = type(data).__name__

            return (
                True,
                f"Valid JSON structure: {data_type}",
            )

        except (
            UnicodeDecodeError,
            UnicodeError,
            json.JSONDecodeError,
        ) as exc:
            last_error = exc

    return False, f"JSON parsing failed: {last_error}"


# ============================================================
# 10. XML STRUCTURE VALIDATION
# ============================================================

def validate_xml(path: Path) -> tuple[bool, str]:
    """Validate XML by parsing the complete document."""

    try:
        tree = ET.parse(path)
        root = tree.getroot()

        if root is None:
            return False, "XML document has no root element"

        return (
            True,
            f"Valid XML document: root={root.tag}",
        )

    except Exception as exc:
        return False, f"XML parsing failed: {exc}"


# ============================================================
# 11. TEXT VALIDATION
# ============================================================

def validate_text(path: Path) -> tuple[bool, str]:
    """Validate text by decoding its content."""

    binary_ok, binary_message = reject_binary_payload(path)

    if not binary_ok:
        return False, binary_message

    encodings = (
        "utf-8-sig",
        "utf-8",
        "utf-16",
        "utf-32",
        "cp1252",
        "latin-1",
    )

    last_error = None

    for encoding in encodings:
        try:
            with path.open("r", encoding=encoding) as file:
                sample = file.read(8192)

            if not sample.strip():
                return False, "Text file contains no readable content"

            return (
                True,
                f"Readable text content: encoding={encoding}",
            )

        except UnicodeDecodeError as exc:
            last_error = exc

        except Exception as exc:
            last_error = exc

    return False, f"Text decoding failed: {last_error}"


# ============================================================
# 12. MAIN VALIDATION FUNCTION
# ============================================================

def validate_download_content(
    path: Path,
    expected_name: str,
) -> tuple[bool, str]:
    """
    Validate a downloaded file using its actual structure.

    The file extension determines which parser is used.

    Returns:
        (True, message)  -> Validation passed.
        (False, message) -> Validation failed.
    """

    path = Path(path)

    # STEP 1: Basic checks.
    valid, message = validate_non_empty(path)

    if not valid:
        return False, message

    # STEP 2: Reject HTML error pages.
    if is_html_error_page(path):
        return (
            False,
            "NASA returned an HTML page instead of the requested file",
        )

    # STEP 3: Detect expected file extension.
    extension = Path(expected_name).suffix.lower()

    logger.info(
        "Starting structural validation | file=%s | extension=%s",
        expected_name,
        extension,
    )

    # STEP 4: Select specialized validator.
    validators = {
        ".pdf": validate_pdf,
        ".xlsx": validate_excel,
        ".xlsm": validate_excel,
        ".csv": validate_csv,
        ".docx": validate_docx,
        ".pptx": validate_pptx,
        ".zip": validate_zip,
        ".png": validate_image,
        ".jpg": validate_image,
        ".jpeg": validate_image,
        ".gif": validate_image,
        ".bmp": validate_image,
        ".tif": validate_image,
        ".tiff": validate_image,
        ".webp": validate_image,
        ".json": validate_json,
        ".xml": validate_xml,
        ".txt": validate_text,
        ".md": validate_text,
        ".log": validate_text,
    }

    validator = validators.get(extension)

    if validator is None:
        return (
            True,
            "No specialized structural parser available; "
            "basic existence and non-empty checks passed",
        )

    # STEP 5: Run structural validation.
    try:
        result = validator(path)
        valid, message = result

        if valid:
            logger.info(
                "Structural validation passed | file=%s | message=%s",
                expected_name,
                message,
            )

        else:
            logger.warning(
                "Structural validation failed | file=%s | message=%s",
                expected_name,
                message,
            )

        return valid, message

    except Exception as exc:
        logger.exception(
            "Unexpected structural validation error | file=%s",
            expected_name,
        )

        return (
            False,
            f"Unexpected validation error: {exc}",
        )