#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask.ext.babel import gettext
from flask.ext.wtf import Form
from flask_security.utils import get_message
from wtforms import widgets
from wtforms.fields import *
from wtforms.fields.html5 import EmailField, DecimalRangeField
from wtforms.validators import *

from Dater.data.choices import choices
from models import Users

# password: Minimum 8 characters at least 1 Uppercase Alphabet, 1 Lowercase Alphabet and 1 Number
password_regex = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d_]{8,}$"

messages = {
    'length': 'The number of characters the field must from 5 to 166',
    'data_required': gettext('Field must be filled'),
    'email': gettext('In the field must be an email address'),
    'password_regex': gettext('Minimum 8 characters at least 1 Uppercase Alphabet, 1 Lowercase Alphabet and 1 Number')
}


def any_of(name_choices):
    """
        :param name_choices is list of tuples
        :return AnyOf of Wtforms with list of values
    """
    return AnyOf(set(values[0] for values in choices[name_choices]))


class RegisterForm(Form):
    max_chars = 255
    _validators = {
        'first_name': [DataRequired(message=messages['data_required']),
                       Length(min=2, max=max_chars, message=gettext(messages['length'].format(2, 160)))],
        'last_name': [DataRequired(message=messages['data_required']),
                      Length(min=2, max=max_chars, message=messages['length'])],
        'login': [DataRequired(message=messages['data_required'])],
        'email': [DataRequired(message=messages['data_required']),
                  Email(message=messages['email']),
                  Length(min=8, max=max_chars, message=messages['length'])],
        'password': [DataRequired(message=messages['data_required']),
                     Length(min=8, max=max_chars, message=messages['length']),
                     EqualTo('confirm', message=gettext('Passwords must match')),
                     Regexp(regex=password_regex, message=messages['password_regex'])],
        'confirm': [DataRequired(message=messages['data_required']),
                    Length(min=8, max=max_chars, message=messages['length']),
                    Regexp(regex=password_regex, message=messages['password_regex'])]
    }

    first_name = StringField(validators=_validators['first_name'])
    last_name = StringField(validators=_validators['last_name'])
    login = StringField(validators=_validators['login'])
    email = EmailField(validators=_validators['email'])
    password = PasswordField(validators=_validators['password'])
    confirm = PasswordField(validators=_validators['confirm'])

    def validate(self):
        if not super(RegisterForm, self).validate():
            return False

        if Users.objects(email=self.email.data.strip()):
            self.email.errors.append(get_message('HAVE_USER_WITH_THIS_EMAIL')[0])
            return False

        if Users.objects(login=self.login.data.strip()):
            self.login.errors.append(get_message('HAVE_USER_WITH_THIS_LOGIN')[0])
            return False

        if self.password.data != self.confirm.data:
            self.password.errors.append(get_message('DIFFERENT_PASSWORDS')[0])
            return False

        return True

    def get_user(self):
        return Users.objects(login=self.login.data, email=self.email.data).first()


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class EditProfile(Form):
    max_chars = 255

    _validators = {
        'first_name': [DataRequired(message=messages['data_required']),
                       Length(min=2, max=max_chars, message=messages['length'])],
        'last_name': [DataRequired(message=messages['data_required']),
                      Length(min=2, max=max_chars, message=messages['length'])],
        'place': [Optional(), Length(min=3, max=max_chars, message=messages['length'])],
        'description': [Optional(), Length(min=0, max=160, message=messages['length'])],
        'birthday': [Optional()],
        'gender': [any_of('gender')],
        'marital_status': [any_of('marital_status')],
        'goals': [any_of('target')],
        'growth': [any_of('growth')],
        'weight': [any_of('weight')],
        'body': [any_of('body')],
        'smoking': [any_of('smoking')],
        'food': [any_of('food')],
        'origin': [any_of('origin')],
        'hairs': [any_of('hair')],
        'eyes': [any_of('eyes')],
        'drink': [any_of('alcohol')],
        'films': [any_of('films')],
        'animals': [any_of('animals')],
        'personality': [any_of('personality')],
        'music': [any_of('music')],
        'languages': [any_of('languages')],
        'feature': [any_of('feature')],
        'presentation': [Optional(), Length(min=0, max=160, message=messages['length'])],
        'presentation_research': [Optional(), Length(min=0, max=160, message=messages['length'])]
    }

    # main
    first_name = StringField(validators=_validators['first_name'])
    last_name = StringField(validators=_validators['last_name'])

    # place
    # country = SelectField(choices=empty(form_choices.country_choices()), coerce=str)
    place = StringField()

    # main info
    # birthday = FormField(Birthday) # Поле, импортирующее класс
    description = TextAreaField()
    birthday = DateField(format='%m/%d/%Y', validators=_validators['birthday'])
    gender = SelectField(choices=choices['gender'], validators=_validators['gender'])

    marital_status = SelectField(choices=choices['marital_status'], validators=_validators['marital_status'])
    goals = MultiCheckboxField(choices=choices['target'], validators=_validators['goals'])
    growth = SelectField(choices=choices['growth'], validators=_validators['growth'])
    weight = SelectField(choices=choices['weight'], validators=_validators['weight'])
    body = SelectField(choices=choices['body'], validators=_validators['body'], coerce=str)
    smoking = SelectField(choices=choices['smoking'], validators=_validators['smoking'], coerce=str)
    food = SelectField(choices=choices['food'], validators=_validators['food'], coerce=str)
    origin = SelectField(choices=choices['origin'], validators=_validators['origin'], coerce=str)
    hairs = SelectField(choices=choices['hair'], validators=_validators['hairs'], coerce=str)
    eyes = SelectField(choices=choices['eyes'], validators=_validators['eyes'], coerce=str)
    drink = SelectField(choices=choices['alcohol'], validators=_validators['drink'], coerce=str)
    films = MultiCheckboxField(choices=choices['films'], validators=_validators['films'])
    animals = MultiCheckboxField(choices=choices['animals'], validators=_validators['animals'], coerce=str)
    personality = MultiCheckboxField(choices=choices['personality'], validators=_validators['personality'], coerce=str)
    music = MultiCheckboxField(choices=choices['music'], validators=_validators['music'])
    languages = MultiCheckboxField(choices=choices['languages'], validators=_validators['languages'])
    feature = MultiCheckboxField(choices=choices['feature'], validators=_validators['feature'])
    presentation = TextAreaField(validators=_validators['presentation'])
    presentation_research = TextAreaField(validators=_validators['presentation_research'])

    search_gender = SelectField(choices=choices['gender'])
    search_age_min = SelectField(choices=choices['age'])
    search_age_max = SelectField(choices=choices['age'])
    search_country = SelectField(choices=choices['countries'])

    def validate(self):
        if not super(EditProfile, self).validate():
            return False
        return True


class LoadMediaFile(Form):
    file_data = FileField(validators=[DataRequired()])
    description = TextAreaField(validators=[Length(max=160)])


class HeaderSearch(Form):
    age = DecimalRangeField('Age', default=0)


class SearchUsersViaCity(Form):
    city = StringField()


class SearchUsersViaParameters(Form):
    _validators = {
        'man': [],
        'woman': [],
        'min_age': [any_of('age')],
        'max_age': [any_of('age')],
        'photo': [],
        'place': [Optional(), ],
        'area': [any_of('area')]
    }

    man = BooleanField(default=False, label=gettext("Men"))
    woman = BooleanField(default=False, label=gettext("Woman"))
    min_age = SelectField(choices=choices['age'], label=gettext("Minimal Age"))
    max_age = SelectField(choices=choices['age'], label=gettext("Maximal Age"))
    photo = BooleanField(default=False, label=gettext("Photo"))
    place = StringField(label=gettext("Place"))
    area = SelectField(choices=choices['area'], label=gettext("Area"))