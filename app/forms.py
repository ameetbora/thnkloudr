from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from flask_wtf.file import FileField, FileAllowed, FileRequired
# from flask_wtf.html5 import URLField
from wtforms.fields.html5 import URLField
from wtforms.validators import DataRequired, url, Length


class TestCycleForm(FlaskForm):
    testcyclename = StringField('Test Cycle Name', validators=[DataRequired(), Length(min=0, max=40)])
    testcycledesc = StringField('Test Cycle Description', validators=[DataRequired(), Length(min=0, max=300)])
    projectname = StringField('Project Name', validators=[DataRequired(), Length(min=0, max=40)])
    projectdesc = StringField('Project Description', validators=[DataRequired(), Length(min=0, max=300)])
    trellolink = URLField('Enter Trello Board', validators=[url()])
    testcycleimage = FileField('Image', validators=[
        FileAllowed(['jpg', 'png'], 'Images only!')
    ])
    createtestcycle = SubmitField('Create')


class TestItemForm(FlaskForm):
    testitemname = StringField('Test Name', validators=[DataRequired(), Length(min=0, max=40)])
    testitemdesc = StringField('Test Cycle Description', validators=[DataRequired(), Length(min=0, max=150)])
    testvideo = FileField('Upload Video', validators=[
        FileAllowed(['mp4'], 'mp4 files only')
    ])
    submit = SubmitField('Create')


class TestItemUpdateForm(FlaskForm):
    testitemname = StringField('Test Name', validators=[DataRequired(), Length(min=0, max=40)])
    testitemdesc = StringField('Test Cycle Description', validators=[DataRequired(), Length(min=0, max=300)])
    testvideo = FileField('Upload Video', validators=[
        FileAllowed(['mp4'], 'mp4 files only')
    ])
    submit = SubmitField('Update')


class TestCycleUpdateForm(FlaskForm):
    testcyclename = StringField('Test Cycle Name', validators=[DataRequired(), Length(min=0, max=40)])
    testcycledesc = StringField('Test Cycle Description', validators=[DataRequired(), Length(min=0, max=300)])
    projectname = StringField('Project Name', validators=[DataRequired(), Length(min=0, max=40)])
    projectdesc = StringField('Project Description', validators=[DataRequired(), Length(min=0, max=300)])
    trellolink = URLField('Enter Trello Board', validators=[url()])
    testcycleimage = FileField('Image', validators=[
        FileAllowed(['jpg', 'png'], 'Images only!')
    ])
    createtestcycle = SubmitField('Update')
