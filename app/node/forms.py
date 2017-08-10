
import re
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DecimalField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, AnyOf, NumberRange, ValidationError

from app.models.node import CLOUD_PROVIDERS

def validate_name_alphanumeric(form, field):
    if field.data:
        alphanumeric = re.match('^[a-zA-Z0-9_]+$', field.data) is not None
        if not alphanumeric:
            raise ValidationError('Name: must only include alphanumeric or underscore characters.')

class NewNodeForm(FlaskForm):
    """
    Form for a user to adopt a new node
    """
    bu_ad = IntegerField('Acceptance Depth (AD)', default=12, validators=[
        DataRequired(message='AD: cannot be blank.'),
        NumberRange(min=1, max=100, message='AD: must be between between 1 and 100.')
    ])

    bu_eb = DecimalField('Excessive Blocksize (EB)', default=16.00, validators=[
        DataRequired(message='EB: cannot be blank.'),
        NumberRange(min=0.1, max=200.0, message='EB: must be between 0.10 and 200.00.')
    ])

    name = StringField('Name', validators=[
        Length(max=12, message='Name: must be less than 12 characters.'),
        validate_name_alphanumeric
    ])

    provider = SelectField('Cloud Provider',
        choices=[('digital_ocean', 'Digital Ocean'), (('aws', 'Amazon Web Services (AWS)'))],
        validators=[
            DataRequired(message='Cloud Provider: cannot be blank.'),
            AnyOf(values=CLOUD_PROVIDERS, message='Cloud Provider: must be allowed value.')
        ])

    months = IntegerField('How long do you want to support this node (in months)?', default=6,
        validators=[
            DataRequired(message='Months: cannot be blank.'),
            NumberRange(min=1, max=36, message='Months: must be between 1 and 36.')
        ])

    submit = SubmitField('Submit')

class ExistingNodeForm(FlaskForm):
    """
    Form for a user to edit an existing node
    """
    bu_ad = IntegerField('Acceptance Depth (AD)', default=12, validators=[
        DataRequired(message='AD: cannot be blank.'),
        NumberRange(min=1, max=100, message='AD: must be between between 1 and 100.')
    ])

    bu_eb = DecimalField('Excessive Blocksize (EB)', default=16.00, validators=[
        DataRequired(message='EB: cannot be blank.'),
        NumberRange(min=0.1, max=200.0, message='EB: must be between 0.10 and 200.00.')
    ])

    name = StringField('Name', validators=[
        Length(max=12, message='Name: must be less than 12 characters.'),
        validate_name_alphanumeric
    ])

    submit = SubmitField('Submit')
