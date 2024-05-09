from flask import Flask, render_template, redirect, url_for, session
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, URLField, BooleanField
from wtfforms_buttonfield import ButtonField
from wtforms.validators import DataRequired, URL

# This is the text to be displayed on the cover page:
default_title = "Cafe Database"
default_subtitle = ("Welcome to my cafe database. Feel free to view info about all the stored cafes. "
                    "You're free to add or delete other cafes that have yet to be listed.")
title_after_add = "Success!"
subtitle_after_add = "You've successfully added a cafe to the database! You can view it by clicking the button below."
title_after_delete = "Success!"
subtitle_after_delete = "You've successfully deleted a cafe from the database."


app = Flask(__name__)
app.config['SECRET_KEY'] = "p5EtRgsIPRxOvSZfo5PPiy02yWKEBj7CSeK4yF5YH147dY7yOcJaNH7IWZ4L4yqr"
Bootstrap5(app)


# CREATE DB
class Base(DeclarativeBase):
    pass


# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
database = SQLAlchemy(model_class=Base)
database.init_app(app)


# Cafe TABLE Configuration
class Cafe(database.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)


columns = ["id", "name", "map_url", "img_url", "location", "seats", "has_toilet", "has_wifi", "has_sockets",
           "can_take_calls", "coffee_price"]


class AddCafeForm(FlaskForm):
    name = StringField("Cafe Name:", validators=[DataRequired()])
    map_url = URLField("Cafe Location on Google Maps (URL):", validators=[DataRequired(), URL()])
    img_url = URLField("Cafe Image (URL):", validators=[DataRequired(), URL()])
    location = StringField("Location Name:", validators=[DataRequired()])
    seats = StringField("Number of Seats (0-10, 10-20, 20-30, 30-40, 40-50, or 50+):", validators=[DataRequired()])
    has_toilet = BooleanField("Does the cafe have restrooms?")
    has_wifi = BooleanField("Does the cafe provide complementary wifi?")
    has_sockets = BooleanField("Does the cafe provide electrical sockets?")
    can_take_calls = BooleanField("Does the cafe have reception to take calls?")
    coffee_price = StringField("What's the cheapest coffee price at that cafe? Please give to the nearest cent:",
                               default="£")
    # I created my own ButtonField in wtfforms_buttonfield.py
    # so that the submit element would be a button and not an input. Thus, the proper styling could then be applied.
    submit = ButtonField(default="Submit", class_="btn btn-dark rounded-pill px-3")


class DeleteCafeForm(FlaskForm):
    id = StringField("Id of Cafe to be Deleted:", validators=[DataRequired()])
    name = StringField("Name of Cafe to be Deleted:", validators=[DataRequired()])
    submit = ButtonField(default="Submit", class_="btn btn-dark rounded-pill px-3")


with app.app_context():
    database.create_all()


@app.route("/")
def home():
    title = session.get('title', default_title)
    subtitle = session.get('subtitle', default_subtitle)
    session.pop('title', None)  # Remove the stored title from session
    session.pop('subtitle', None)  # Remove the stored subtitle from session
    return render_template("index.html", title=title, subtitle=subtitle)


@app.route("/cafes")
def show_cafes():
    result = database.session.execute(database.select(Cafe))
    cafes = result.scalars()
    return render_template("cafes.html", columns=columns, cafes=cafes)


@app.route("/add", methods=["GET", "POST"])
def add_cafe():
    add_form = AddCafeForm()
    if add_form.validate_on_submit() is True:
        new_cafe = Cafe(name=add_form.name.data,
                        map_url=add_form.map_url.data,
                        img_url=add_form.img_url.data,
                        location=add_form.location.data,
                        seats=add_form.seats.data,
                        has_toilet=add_form.has_toilet.data,
                        has_wifi=add_form.has_wifi.data,
                        has_sockets=add_form.has_sockets.data,
                        can_take_calls=add_form.can_take_calls.data,
                        coffee_price=add_form.coffee_price.data)

        database.session.add(new_cafe)
        database.session.commit()
        session["title"] = title_after_add
        session["subtitle"] = subtitle_after_add

        return redirect(url_for('home'))

    heading = "Add a new cafe into the database"
    return render_template("add_or_delete.html", heading=heading, form=add_form)


@app.route("/delete", methods=["GET", "POST"])
def delete_cafe():
    heading = "Delete a cafe from the database"
    delete_form = DeleteCafeForm()

    if delete_form.validate_on_submit() is True:
        cafe_to_delete = database.session.execute(database.select(Cafe).where(Cafe.id == delete_form.id.data)).scalar()

        if cafe_to_delete is None:
            heading = "Cafe with that id is not found in database. Please try again."

        elif cafe_to_delete.name != delete_form.name.data:
            heading = "Cafe id and name do not match. Please try again."

        else:
            database.session.delete(cafe_to_delete)
            database.session.commit()
            session["title"] = title_after_delete
            session["subtitle"] = subtitle_after_delete
            return redirect(url_for('home'))

    return render_template("add_or_delete.html", heading=heading, form=delete_form)


if __name__ == "__main__":
    app.run()
