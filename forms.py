from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DecimalField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired() ])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    sManager = SubmitField('Are you a Store Manager? Click here')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired() ])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class newCategoryForm(FlaskForm):
    catName = StringField("Category name",validators = [DataRequired() ])
    submit = SubmitField('Create Category')


class newItemForm(FlaskForm):
    itemName = StringField("Item name",validators = [DataRequired() ])
    price = DecimalField("Item Price",validators = [DataRequired() ])
    stock = DecimalField("Stock",validators = [DataRequired() ])
    submit = SubmitField('Add Item')

class addItemForm(FlaskForm):
    quantity = DecimalField("Quantity",validators = [DataRequired(),NumberRange(0, 99)])
    submit = SubmitField('Add Item to cart')

class buyForm(FlaskForm):
    buy = SubmitField('Buy Now!')
    back = SubmitField('continue shopping')

class editCartForm(FlaskForm):
    quantity = DecimalField("Quantity", validators = [DataRequired() ])
    submit = SubmitField('Edit item')
    delete = SubmitField('Delete item')
    back = SubmitField('continue shopping')

class editForm(FlaskForm):
    quantity = DecimalField("Quantity", validators = [DataRequired() ])
    submit = SubmitField('Edit item')
    delete = SubmitField('Delete item')
    back = SubmitField('Back to Home')

class editPriceForm(FlaskForm):
    quantity = DecimalField("New Price", validators = [DataRequired() ])
    submit = SubmitField('Edit item')
    back = SubmitField('Back to Home')

class searchForm(FlaskForm):
    search = StringField("",validators = [DataRequired() ])
    submit = SubmitField('Go')

class approveForm(FlaskForm):
    approveBtn = SubmitField('Approve')
    rejectBtn  = SubmitField('Reject')

class confirmForm(FlaskForm):
    yesBtn = SubmitField('yes, I confirm')
    backBtn = SubmitField('No, take me back')

class GenerateReportForm(FlaskForm):
    GenerateBtn = SubmitField('Generate CSV Report')
