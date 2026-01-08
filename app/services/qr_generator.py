"""
QR Code Generator Service
"""
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer, CircleModuleDrawer, SquareModuleDrawer
from PIL import Image, ImageDraw
import io
import os
from typing import Optional, Tuple
from app.config import settings


class QRCodeGenerator:
    """Service for generating and customizing QR codes"""
    
    def __init__(self):
        self.storage_path = settings.QR_STORAGE_PATH
        os.makedirs(self.storage_path, exist_ok=True)
    
    def generate(
        self,
        data: str,
        *,
        size: int = 300,
        error_correction: str = "M",
        foreground_color: str = "#000000",
        background_color: str = "#FFFFFF",
        style: str = "square",
        logo_path: Optional[str] = None,
        logo_size_ratio: float = 0.3
    ) -> Tuple[bytes, bytes, bytes]:
        """
        Generate QR code with customization
        
        Args:
            data: Data to encode (URL, text, etc.)
            size: Output size in pixels
            error_correction: L, M, Q, or H
            foreground_color: Hex color for QR modules
            background_color: Hex color for background
            style: square, rounded, or dots
            logo_path: Path to logo image to embed
            logo_size_ratio: Logo size relative to QR (0-1)
        
        Returns:
            Tuple of (png_bytes, svg_bytes, pdf_bytes)
        """
        # Map error correction
        ec_map = {
            "L": qrcode.constants.ERROR_CORRECT_L,
            "M": qrcode.constants.ERROR_CORRECT_M,
            "Q": qrcode.constants.ERROR_CORRECT_Q,
            "H": qrcode.constants.ERROR_CORRECT_H,
        }
        
        # Create QR code instance
        qr = qrcode.QRCode(
            version=None,  # Auto-determine
            error_correction=ec_map.get(error_correction, qrcode.constants.ERROR_CORRECT_M),
            box_size=10,
            border=4,
        )
        
        qr.add_data(data)
        qr.make(fit=True)
        
        # Select style
        module_drawer = self._get_module_drawer(style)
        
        # Generate image
        if module_drawer:
            img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=module_drawer,
                fill_color=foreground_color,
                back_color=background_color
            )
        else:
            img = qr.make_image(
                fill_color=foreground_color,
                back_color=background_color
            )
        
        # Add logo if provided
        if logo_path and os.path.exists(logo_path):
            img = self._add_logo(img, logo_path, logo_size_ratio)
        
        # Resize to desired size
        img = img.resize((size, size), Image.Resampling.LANCZOS)
        
        # Convert to bytes
        png_bytes = self._to_png(img)
        svg_bytes = self._to_svg(qr, foreground_color, background_color)
        pdf_bytes = self._to_pdf(img)
        
        return png_bytes, svg_bytes, pdf_bytes
    
    def _get_module_drawer(self, style: str):
        """Get module drawer based on style"""
        if style == "rounded":
            return RoundedModuleDrawer()
        elif style == "dots":
            return CircleModuleDrawer()
        else:  # square
            return None  # Use default
    
    def _add_logo(self, qr_img: Image.Image, logo_path: str, size_ratio: float) -> Image.Image:
        """Add logo to center of QR code"""
        qr_img = qr_img.convert("RGBA")
        
        # Open and resize logo
        logo = Image.open(logo_path)
        logo = logo.convert("RGBA")
        
        # Calculate logo size
        qr_width, qr_height = qr_img.size
        logo_size = int(min(qr_width, qr_height) * size_ratio)
        logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
        
        # Create white background for logo
        logo_bg = Image.new('RGBA', (logo_size + 20, logo_size + 20), 'white')
        logo_bg_pos = ((logo_bg.size[0] - logo_size) // 2, (logo_bg.size[1] - logo_size) // 2)
        logo_bg.paste(logo, logo_bg_pos, logo)
        
        # Paste logo in center
        logo_pos = ((qr_width - logo_bg.size[0]) // 2, (qr_height - logo_bg.size[1]) // 2)
        qr_img.paste(logo_bg, logo_pos, logo_bg)
        
        return qr_img
    
    def _to_png(self, img: Image.Image) -> bytes:
        """Convert PIL Image to PNG bytes"""
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()
    
    def _to_svg(self, qr: qrcode.QRCode, fill_color: str, back_color: str) -> bytes:
        """Generate SVG representation"""
        # For now, return empty bytes - full SVG implementation would be here
        # This requires additional library like qrcode[svg]
        return b""
    
    def _to_pdf(self, img: Image.Image) -> bytes:
        """Convert to PDF bytes"""
        buffer = io.BytesIO()
        img_rgb = img.convert("RGB")
        img_rgb.save(buffer, format="PDF")
        return buffer.getvalue()
    
    def save_files(self, short_code: str, png_data: bytes, svg_data: bytes, pdf_data: bytes) -> dict:
        """
        Save QR code files to storage
        
        Returns:
            Dict with file paths
        """
        base_path = os.path.join(self.storage_path, short_code)
        
        paths = {
            "png": f"{base_path}.png",
            "svg": f"{base_path}.svg" if svg_data else None,
            "pdf": f"{base_path}.pdf",
        }
        
        # Save files
        with open(paths["png"], "wb") as f:
            f.write(png_data)
        
        if svg_data:
            with open(paths["svg"], "wb") as f:
                f.write(svg_data)
        
        with open(paths["pdf"], "wb") as f:
            f.write(pdf_data)
        
        return paths


# Global instance
qr_generator = QRCodeGenerator()
