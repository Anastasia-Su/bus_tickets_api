from datetime import datetime
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont


class ImageGenerator:
    @staticmethod
    def create_ticket_image(
        username: str, route: str, departure_time: datetime, seat_number: int
    ) -> BytesIO:
        """Creates a ticket image with the provided details."""

        img = Image.new("RGB", (400, 200), color=(255, 255, 255))
        font = ImageFont.load_default()
        draw = ImageDraw.Draw(img)

        draw.text((10, 10), f"Name: {username}", fill=(0, 0, 0), font=font)
        draw.text((10, 40), f"Route: {route}", fill=(0, 0, 0), font=font)
        draw.text(
            (10, 70),
            f"Departure Time: {departure_time}",
            fill=(0, 0, 0),
            font=font,
        )
        draw.text(
            (10, 100), f"Seat Number: {seat_number}", fill=(0, 0, 0), font=font
        )

        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format="JPEG")
        img_byte_arr.seek(0)

        return img_byte_arr
