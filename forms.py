from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField, SubmitField
from wtforms.validators import DataRequired, ValidationError
from flask_wtf.file import FileAllowed, FileRequired
from models import Product

class ProductForm(FlaskForm):
    serial_number = StringField('Serial Number', validators=[DataRequired()])
    name = StringField('Product Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    image = FileField('Product Image', validators=[
        FileRequired(message='Image is required.'),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    submit = SubmitField('Save')

    def __init__(self, original_serial_number=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_serial_number = original_serial_number

    def validate_serial_number(self, field):
        existing = Product.query.filter_by(serial_number=field.data).first()
        if existing and field.data != self.original_serial_number:
            raise ValidationError('A product with this serial number already exists.')

