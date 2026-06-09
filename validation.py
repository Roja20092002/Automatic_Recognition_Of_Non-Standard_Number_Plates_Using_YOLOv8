import re


class PlateValidator:

    def clean_text(self, text):

        text = text.upper()
        text = text.replace(" ", "")

        return text

    def is_valid_plate(self, text):

        text = self.clean_text(text)

        pattern = (
            r'^[A-Z]{2}'
            r'[0-9]{2}'
            r'[A-Z]{1,2}'
            r'[0-9]{4}$'
        )

        return bool(
            re.fullmatch(
                pattern,
                text
            )
        )