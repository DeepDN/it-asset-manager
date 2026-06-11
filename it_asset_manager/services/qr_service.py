import os
import io
from flask import current_app
from PIL import Image
from typing import Optional


def _get_qr_dir():
    return current_app.config.get('QR_CODE_DIR',
                                   os.path.join(os.path.dirname(current_app.instance_path), 'uploads', 'qrcodes'))


def _get_barcode_dir():
    return current_app.config.get('BARCODE_DIR',
                                   os.path.join(os.path.dirname(current_app.instance_path), 'uploads', 'barcodes'))


def generate_qr_image(asset_tag: str, base_url: str = 'http://localhost:5000') -> str:
    import qrcode
    qr_dir = _get_qr_dir()
    os.makedirs(qr_dir, exist_ok=True)

    filepath = os.path.join(qr_dir, f"{asset_tag}.png")
    if os.path.exists(filepath):
        return filepath

    data_url = f"{base_url}/asset/{asset_tag}"
    qr = qrcode.make(data_url)
    qr.save(filepath)
    return filepath


def generate_qr_bytes(asset_tag: str, base_url: str = 'http://localhost:5000') -> bytes:
    import qrcode
    data_url = f"{base_url}/asset/{asset_tag}"
    qr = qrcode.make(data_url)
    buf = io.BytesIO()
    qr.save(buf, format='PNG')
    return buf.getvalue()


def generate_barcode_image(asset_tag: str) -> str:
    from barcode import Code128
    from barcode.writer import ImageWriter
    bc_dir = _get_barcode_dir()
    os.makedirs(bc_dir, exist_ok=True)

    filepath = os.path.join(bc_dir, asset_tag)
    if os.path.exists(f"{filepath}.png"):
        return f"{filepath}.png"

    code = Code128(asset_tag, writer=ImageWriter())
    full_path = code.save(filepath)
    return full_path


def generate_barcode_bytes(asset_tag: str) -> bytes:
    from barcode import Code128
    from barcode.writer import ImageWriter
    code = Code128(asset_tag, writer=ImageWriter())
    buf = io.BytesIO()
    code.write(buf)
    return buf.getvalue()
