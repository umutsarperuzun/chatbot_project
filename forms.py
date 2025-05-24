from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField,TextAreaField,DateField
from wtforms.validators import DataRequired, ValidationError, Length,Optional
from models import Type, User


# Form for creating or updating chatbot responses
class ResponseForm(FlaskForm):
    category = StringField('Category', validators=[DataRequired(message="Category is required.")])
    variation = StringField('Variations (comma-separated)', validators=[DataRequired(message="At least one variation is required.")])
    response = StringField('Responses (comma-separated)', validators=[DataRequired(message="At least one response is required.")])
    type = SelectField('Type', validators=[DataRequired(message="Type selection is required.")], coerce=int)

    submit = SubmitField('Save')
    
    def __init__(self, *args, **kwargs):
        super(ResponseForm, self).__init__(*args, **kwargs)
        # Dynamically populate type choices
        self.type.choices = [(type.id, type.name) for type in Type.query.order_by(Type.name).all()]

    def validate_variation(self, field):
        # Validate that variations are not empty
        variations = [v.strip() for v in field.data.split(',')]
        if not all(variations):
            raise ValidationError('All variations must be non-empty.')
        if len(variations) > 20:  # Optional: Limit the number of variations
            raise ValidationError('Too many variations. Limit is 20.')

    def validate_response(self, field):
        # Validate that responses are not empty
        responses = [r.strip() for r in field.data.split(',')]
        if not all(responses):
            raise ValidationError('All responses must be non-empty.')
        if len(responses) > 10:  # Optional: Limit the number of responses
            raise ValidationError('Too many responses. Limit is 10.')


# Form for chatbot message submission
class MessageForm(FlaskForm):
    message = StringField('Message', validators=[DataRequired(message="Please enter a message.")])
    submit = SubmitField('Send')


# Form for user login
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message="Username is required."),
        Length(min=4, max=50, message="Username must be between 4 and 50 characters.")
    ])
    department = StringField('Department', validators=[
        DataRequired(message="Department is required."),
        Length(min=2, max=100, message="Department must be between 2 and 100 characters.")
    ])
    submit = SubmitField('Login')


# Form for user registration
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message="Username is required."),
        Length(min=4, max=50, message="Username must be between 4 and 50 characters.")
    ])
    department = StringField('Department', validators=[
        DataRequired(message="Department is required."),
        Length(min=2, max=100, message="Department must be between 2 and 100 characters.")
    ])
    submit = SubmitField('Register')

    def validate_username(self, username):
        # Ensure the username is unique
        existing_user = User.query.filter_by(username=username.data).first()
        if existing_user:
            raise ValidationError('This username is already taken. Please choose a different one.')

# Form for maintenance report
class MaintenanceReportForm(FlaskForm):
    issue_title = StringField("Issue Title", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    urgency = SelectField("Urgency", choices=[("Low", "Low"), ("Medium", "Medium"), ("High", "High")], validators=[DataRequired()])
    department = SelectField("Department", choices=[("IT", "IT"), ("Maintenance", "Maintenance"), ("Operations", "Operations")], validators=[DataRequired()])
    type_of_maintenance = SelectField(
        "Type of Maintenance",
        choices=[("Routine", "Routine"), ("Oil", "Oil"), ("Engine", "Engine")],
        validators=[DataRequired()]
    )
    
class VehicleCreateForm(FlaskForm):
    plate_number = StringField('Vehicle Plate', validators=[DataRequired(), Length(max=20)])
    vehicle_type = StringField('Vehicle Type', validators=[DataRequired(), Length(max=50)])
    location = StringField('Location', validators=[Optional(), Length(max=100)])
    last_maintenance_date = DateField('Last Maintenance Date (YYYY-MM-DD)', format='%Y-%m-%d', validators=[Optional()])
    next_maintenance_date = DateField('Next Maintenance Date (YYYY-MM-DD)', format='%Y-%m-%d', validators=[Optional()])
    work_type = StringField('Work Type', validators=[Optional(), Length(max=100)])
    submit = SubmitField('Create Vehicle')

class VehicleUpdateForm(FlaskForm):
    location = StringField('Location', validators=[Optional(), Length(max=100)])
    last_maintenance_date = DateField('Last Maintenance Date (YYYY-MM-DD)', format='%Y-%m-%d', validators=[Optional()])
    next_maintenance_date = DateField('Next Maintenance Date (YYYY-MM-DD)', format='%Y-%m-%d', validators=[Optional()])
    work_type = StringField('Work Type', validators=[Optional(), Length(max=100)])
    submit = SubmitField('Update Vehicle')