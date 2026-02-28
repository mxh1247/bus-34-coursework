from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.choices import SelectField
from wtforms.fields.numeric import IntegerField, FloatField
from wtforms.fields.datetime import DateField

from wtforms.validators import DataRequired

from datetime import date


class UserHealthForm(FlaskForm):
    log_date = DateField(
        "Log Date",
        format="%Y-%m-%d",
        default=date.today
    )
    steps = IntegerField("Steps", validators=[DataRequired()])
    sleep = IntegerField("Hours of Sleep", validators=[DataRequired()])
    water = FloatField("Amount of Water Consumed (Litres)", validators=[DataRequired()])
    blood = FloatField("Blood Pressure", validators=[DataRequired()])
    heart = IntegerField("Heart Rate", validators=[DataRequired()])
    user_comment = StringField("Comment (optional)")
    submit = SubmitField("Submit Health Log")