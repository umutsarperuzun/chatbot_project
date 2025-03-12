from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
from models import Type

class ResponseForm(FlaskForm):
    category = StringField('Category', validators=[DataRequired()])
    variation = StringField('Variations (comma-separated)', validators=[DataRequired()])
    response = StringField('Responses (comma-separated)', validators=[DataRequired()])
    type = SelectField('Type', validators=[DataRequired()], coerce=str)

    submit = SubmitField('Save')

    def __init__(self, *args, **kwargs):
        super(ResponseForm, self).__init__(*args, **kwargs)
        # Type seçenekleri form başlatıldığında sorgulanır
        self.type.choices = [(type.id, type.name) for type in Type.query.order_by(Type.name).all()]
