"""
Pulls raw text out of an uploaded resume file. This is intentionally kept
separate from the AI parsing step: extraction is deterministic and cheap,
parsing (raw text -> structured JSON) is what costs an LLM call.
"""
import io

import docx2txt
import pdfplumber


class UnsupportedFileTypeError(Exception):
    pass


class EmptyResumeTextError(Exception):
    pass


class CorruptFileError(Exception):
    pass


def extract_text(file_bytes: bytes, content_type: str) -> str:
    try:
        if content_type == "application/pdf":
            text = _extract_pdf(file_bytes)
        elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text = _extract_docx(file_bytes)
        else:
            raise UnsupportedFileTypeError(f"Unsupported content type: {content_type}")
    except (UnsupportedFileTypeError, EmptyResumeTextError):
        raise
    except Exception as exc:  # noqa: BLE001 - pdfplumber/docx2txt raise various parser-specific errors
        # e.g. pdfminer.PDFSyntaxError on a corrupted/non-PDF file claiming to be one,
        # or a password-protected file. Surface this as a clean 422, not a raw 500.
        raise CorruptFileError(
            "This file couldn't be read - it may be corrupted, password-protected, "
            "or not a valid PDF/DOCX. Please try re-exporting and uploading again."
        ) from exc

    text = text.strip()
    if not text or len(text) < 30:
        # Very short extraction usually means a scanned/image-only PDF with no
        # selectable text layer - we surface this clearly instead of silently
        # sending near-empty text to the LLM and getting a hallucinated profile back.
        raise EmptyResumeTextError(
            "Could not extract readable text from this file. If it's a scanned "
            "image, please upload a text-based PDF or DOCX instead."
        )
    return text


def _extract_pdf(file_bytes: bytes) -> str:
    chunks: list[str] = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            chunks.append(page_text)
    return "\n".join(chunks)


def _extract_docx(file_bytes: bytes) -> str:
    with io.BytesIO(file_bytes) as buf:
        return docx2txt.process(buf) or ""
