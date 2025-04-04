import random
import string
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from config import Config

class CaptchaGenerator:
    def __init__(self):
        self.text = ''
        self.length = Config.CAPTCHA_LENGTH
        self.width = 200
        self.height = 100
        self.font = ImageFont.load_default()
        self.background_color = (255, 255, 255)
        self.text_colors = [(0, 0, 0)]  # Можно расширить палитру

    def generate(self):
        """Генерирует новую CAPTCHA и возвращает байты изображения"""
        self._generate_text()
        image = self._create_base_image()
        self._draw_text(image)
        self._add_noise(image)
        return self._image_to_bytes(image)

    def _generate_text(self):
        """Генерирует случайный текст для CAPTCHA"""
        chars = string.ascii_letters + string.digits
        self.text = ''.join(random.choices(chars, k=self.length)).upper()

    def _create_base_image(self):
        """Создает базовое изображение с белым фоном"""
        return Image.new('RGB', (self.width, self.height), self.background_color)

    def _draw_text(self, image):
        """Рисует текст на изображении со случайными смещениями"""
        draw = ImageDraw.Draw(image)
        for i, char in enumerate(self.text):
            x = 20 + i * 40 + random.randint(-15, 15)
            y = 30 + random.randint(-15, 15)
            color = random.choice(self.text_colors)
            draw.text((x, y), char, fill=color, font=self.font)

    def _add_noise(self, image, noise_points=100):
        """Добавляет визуальный шум на изображение"""
        draw = ImageDraw.Draw(image)
        for _ in range(noise_points):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            draw.point(
                (x, y), 
                fill=(
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255)
                )
            )

    def _image_to_bytes(self, image):
        """Конвертирует изображение в байты PNG"""
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()

    def verify(self, user_input):
        """Проверяет введенную пользователем CAPTCHA"""
        return user_input.strip().upper() == self.text.upper()