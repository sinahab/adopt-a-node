
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DecimalField, IntegerField, SubmitField
from wtforms.validators import DataRequired

class NewNodeForm(FlaskForm):
    """
    Form for a user to adopt a new node
    """
    bu_ad = IntegerField('Acceptance Depth (AD)', default=12, validators=[DataRequired()])
    bu_eb = DecimalField('Excessive Blocksize (EB)', default=16.00, validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    provider = SelectField('Cloud Provider', choices=[('aws', 'Amazon Web Services (AWS)'), ('digital_ocean', 'Digital Ocean')], validators=[DataRequired()])
    months = IntegerField('How long do you want to support this node?', default=6, validators=[DataRequired()])
    submit = SubmitField('Submit')

class ExistingNodeForm(FlaskForm):
    """
    Form for a user to edit an existing node
    """
    bu_ad = IntegerField('Acceptance Depth', validators=[DataRequired()])
    bu_eb = DecimalField('Excessive Blocksize', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Submit')
