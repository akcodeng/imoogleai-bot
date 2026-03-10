"""
Imoogle 5.0 Image Generation Service
Multi-provider image generation with Pictura AI branding.
Supports: Mistral, Stability AI, Leonardo AI, Fal.ai
"""

import httpx
import base64
from typing import Optional, Dict, Any
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import asyncio

from app.config import settings


class ImageGenerationService:
    """
    Image generation service with:
    1. Mistral Pixtral (primary - for image understanding and generation)
    2. Stability AI (high quality)
    3. Leonardo AI (artistic)
    4. Fal.ai (fast)
    5. Pictura AI branding overlay
    """
    
    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=120.0)
    
    async def close(self):
        await self.http_client.aclose()
    
    async def generate(
        self,
        prompt: str,
        style: str = "auto",
        size: str = "1024x1024",
        add_branding: bool = True,
    ) -> Optional[bytes]:
        """
        Generate an image from prompt.
        
        Args:
            prompt: Image description
            style: "realistic", "artistic", "anime", "auto"
            size: Image size
            add_branding: Whether to add Imoogle watermark
        
        Returns:
            Image bytes or None if failed
        """
        image_bytes = None
        
        # Enhance prompt for better results
        enhanced_prompt = self._enhance_prompt(prompt, style)
        
        # Try providers in order
        providers = [
            ("mistral", self._mistral_generate),
            ("stability", self._stability_generate),
            ("leonardo", self._leonardo_generate),
            ("fal", self._fal_generate),
        ]
        
        for provider_name, provider_func in providers:
            try:
                image_bytes = await provider_func(enhanced_prompt, size)
                if image_bytes:
                    print(f"[ImoogleAI] Image generated with {provider_name}")
                    break
            except Exception as e:
                print(f"[ImoogleAI] {provider_name} image gen failed: {e}")
                continue
        
        if image_bytes and add_branding:
            image_bytes = self._add_branding(image_bytes)
        
        return image_bytes
    
    def _enhance_prompt(self, prompt: str, style: str) -> str:
        """Enhance prompt for better image generation."""
        style_modifiers = {
            "realistic": "photorealistic, highly detailed, professional photography, 8k resolution",
            "artistic": "digital art, vibrant colors, artistic, creative composition",
            "anime": "anime style, manga art, Japanese animation, vibrant colors",
            "auto": "high quality, detailed, professional",
        }
        
        modifier = style_modifiers.get(style, style_modifiers["auto"])
        return f"{prompt}, {modifier}"
    
    async def _mistral_generate(self, prompt: str, size: str) -> Optional[bytes]:
        """Generate image using Mistral Pixtral model."""
        # Mistral doesn't have native image generation yet
        # This is a placeholder for when they add it
        # For now, skip to next provider
        return None
    
    async def _stability_generate(self, prompt: str, size: str) -> Optional[bytes]:
        """Generate image using Stability AI."""
        if not settings.STABILITY_API_KEY:
            return None
        
        url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
        
        width, height = map(int, size.split("x"))
        
        headers = {
            "Authorization": f"Bearer {settings.STABILITY_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        payload = {
            "text_prompts": [
                {"text": prompt, "weight": 1.0},
                {"text": "blurry, bad quality, distorted, ugly", "weight": -1.0},
            ],
            "cfg_scale": 7,
            "width": min(width, 1024),
            "height": min(height, 1024),
            "samples": 1,
            "steps": 30,
        }
        
        response = await self.http_client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        if data.get("artifacts"):
            image_b64 = data["artifacts"][0]["base64"]
            return base64.b64decode(image_b64)
        
        return None
    
    async def _leonardo_generate(self, prompt: str, size: str) -> Optional[bytes]:
        """Generate image using Leonardo AI."""
        if not settings.LEONARDO_API_KEY:
            return None
        
        # Create generation
        url = "https://cloud.leonardo.ai/api/rest/v1/generations"
        
        headers = {
            "Authorization": f"Bearer {settings.LEONARDO_API_KEY}",
            "Content-Type": "application/json",
        }
        
        width, height = map(int, size.split("x"))
        
        payload = {
            "prompt": prompt,
            "negative_prompt": "blurry, bad quality, distorted, ugly, watermark",
            "modelId": "6bef9f1b-29cb-40c7-b9df-32b51c1f67d3",  # Leonardo Creative
            "width": min(width, 1024),
            "height": min(height, 1024),
            "num_images": 1,
        }
        
        response = await self.http_client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        generation_id = data.get("sdGenerationJob", {}).get("generationId")
        if not generation_id:
            return None
        
        # Poll for completion
        for _ in range(30):
            await asyncio.sleep(2)
            
            status_url = f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}"
            status_response = await self.http_client.get(status_url, headers=headers)
            status_data = status_response.json()
            
            generations = status_data.get("generations_by_pk", {})
            if generations.get("status") == "COMPLETE":
                images = generations.get("generated_images", [])
                if images:
                    image_url = images[0].get("url")
                    if image_url:
                        image_response = await self.http_client.get(image_url)
                        return image_response.content
                break
        
        return None
    
    async def _fal_generate(self, prompt: str, size: str) -> Optional[bytes]:
        """Generate image using Fal.ai (fast)."""
        if not settings.FAL_API_KEY:
            return None
        
        url = "https://fal.run/fal-ai/flux/schnell"
        
        headers = {
            "Authorization": f"Key {settings.FAL_API_KEY}",
            "Content-Type": "application/json",
        }
        
        width, height = map(int, size.split("x"))
        
        payload = {
            "prompt": prompt,
            "image_size": {"width": width, "height": height},
            "num_images": 1,
            "enable_safety_checker": True,
        }
        
        response = await self.http_client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        images = data.get("images", [])
        if images:
            image_url = images[0].get("url")
            if image_url:
                image_response = await self.http_client.get(image_url)
                return image_response.content
        
        return None
    
    def _add_branding(self, image_bytes: bytes) -> bytes:
        """Add Imoogle branding watermark to image."""
        try:
            # Open image
            image = Image.open(BytesIO(image_bytes))
            draw = ImageDraw.Draw(image)
            
            # Watermark text
            watermark = "Generated by ImoogleAI"
            
            # Try to use a nice font, fallback to default
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
            except Exception:
                font = ImageFont.load_default()
            
            # Calculate position (bottom right)
            bbox = draw.textbbox((0, 0), watermark, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = image.width - text_width - 10
            y = image.height - text_height - 10
            
            # Draw shadow
            draw.text((x + 1, y + 1), watermark, font=font, fill=(0, 0, 0, 128))
            # Draw text
            draw.text((x, y), watermark, font=font, fill=(255, 255, 255, 200))
            
            # Save to bytes
            output = BytesIO()
            image.save(output, format="PNG")
            return output.getvalue()
        except Exception as e:
            print(f"[ImoogleAI] Branding failed: {e}")
            return image_bytes


# Singleton instance
image_service = ImageGenerationService()
