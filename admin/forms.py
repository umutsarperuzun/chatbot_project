from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length

class ResponseForm(FlaskForm):
    category = StringField('Category', validators=[DataRequired(), Length(max=100, message="Category name must be under 100 characters.")])
    type = SelectField('Type', choices=[('Type1', 'Type1'), ('Type2', 'Type2')], validators=[DataRequired()])
    variation = TextAreaField('Variation', validators=[DataRequired(), Length(max=500, message="Variations must be under 500 characters.")])
    response = TextAreaField('Response', validators=[DataRequired(), Length(max=500, message="Response must be under 500 characters.")])
    submit = SubmitField('Submit')
