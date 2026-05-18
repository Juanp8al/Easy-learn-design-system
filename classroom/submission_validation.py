"""Validación de archivos de entrega."""

import os

from django.core.exceptions import ValidationError

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {
    ".pdf", ".doc", ".docx", ".odt", ".txt", ".rtf",
    ".zip", ".rar",
    ".png", ".jpg", ".jpeg", ".gif", ".webp",
    ".ppt", ".pptx", ".xls", ".xlsx",
}


def validate_submission_file(uploaded_file):
    if not uploaded_file:
        return
    if uploaded_file.size > MAX_UPLOAD_BYTES:
        raise ValidationError(
            f"El archivo supera el tamaño máximo ({MAX_UPLOAD_BYTES // (1024 * 1024)} MB)."
        )
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            "Tipo de archivo no permitido. Use PDF, Word, imágenes, ZIP u hojas de cálculo."
        )
