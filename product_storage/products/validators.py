from django.core.validators import RegexValidator

from product_storage.constants import BARCODE_LENGTH_1, BARCODE_LENGTH_2

barcode_regex_validator = RegexValidator(
    regex=rf'^\d{{{BARCODE_LENGTH_1}}}$|^\d{{{BARCODE_LENGTH_2}}}$',
    message=f'Штрихкод должен иметь длину {BARCODE_LENGTH_1} или '
    f'{BARCODE_LENGTH_2} ' 'символов и состоять из цифр')
