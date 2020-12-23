# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import sys

import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import distinct
from collections import defaultdict

from forms import *

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# TODO: connect to a local postgresql database


# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_talent_description = db.Column(db.String(1000))
    shows = db.relationship('Show', backref=db.backref('Venue', lazy=True), cascade="all, delete")

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_performance_venues = db.Column(db.Boolean)
    seeking_venues_description = db.Column(db.String(1000))
    shows = db.relationship('Show', backref=db.backref('Artist', lazy=True), cascade="all, delete")

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)


db.create_all()


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.

    all_venues = Venue.query.all()

    data = []
    stat_city = {}

    for venue in all_venues:
        stat_city.setdefault(venue.state, []).append(venue.city)
    stat_city = dict(zip(stat_city.keys(), map(set, stat_city.values())))
    for state in stat_city:
        for city in stat_city[state]:
            locations = {"city": city, "state": state, "venues": []}
            venues_ = Venue.query.filter_by(city=city, state=state).all()
            for venue_ in venues_:
                upcoming_shows = Show.query.filter_by(venue_id=venue_.id).filter(Show.start_time > datetime.now()).all()
                venue_list = {
                    "id": venue_.id,
                    "name": venue_.name,
                    "num_upcoming_shows": len(upcoming_shows),
                }
            locations["venues"].append(venue_list)
        data.append(locations)

    # data = [{
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "venues": [{
    #         "id": 1,
    #         "name": "The Musical Hop",
    #         "num_upcoming_shows": 0,
    #     },
    #         {
    #             "id": 3,
    #             "name": "Park Square Live Music & Coffee",
    #             "num_upcoming_shows": 1,
    #         }]
    # }, {
    #     "city": "New York",
    #     "state": "NY",
    #     "venues": [{
    #         "id": 2,
    #         "name": "The Dueling Pianos Bar",
    #         "num_upcoming_shows": 0,
    #     }]
    # }]
    return render_template('pages/venues.html', areas=data);


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get('search_term', '')
    response = {"count": 0, "data": []}
    search_results = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term))).all()
    response['count'] = len(search_results)

    for result in search_results:
        item = {
            "id": result.id,
            "name": result.name
        }
        response['data'].append(item)

    # response = {
    #     "count": 1,
    #     "data": [{
    #         "id": 2,
    #         "name": "The Dueling Pianos Bar",
    #         "num_upcoming_shows": 0,
    #     }]
    # }
    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id db.session.query(id)
    # amshy 3ala show show a geb el start time bta3o
    # TODO: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.get(venue_id)
    shows = Show.query.filter_by(venue_id=venue_id)
    past = shows.filter(Show.start_time < datetime.now()).all()
    upcoming = shows.filter(Show.start_time >= datetime.now()).all()
    past_shows = []
    upcoming_shows = []
    for show in past:
        artist = Artist.query.get(show.artist_id)
        show_data = {
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": str(show.start_time),
        }
        past_shows.append(show_data)
    for show in upcoming:
        artist = Artist.query.get(show.artist_id)
        show_data = {
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": str(show.start_time),
        }
        upcoming.append(show_data)

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres.split(','),
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }

    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    venue = Venue()

    try:
        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.address = request.form['address']
        venue.phone = request.form['phone']
        venue.genres = request.form.getlist('genres')
        venue.facebook_link = request.form['facebook_link']
        venue.website = request.form['website_link']
        venue.image_link = request.form['image_link']
        if request.form['isSeeking']:
            venue.seeking_talent = True
        venue.seeking_talent_description = request.form['seekingDescription']
        db.session.add(venue)
        db.session.commit()
        db.session.refresh(venue)
        flash('Venue ' + request.form['name'] + ' was successfully listed!')

    except:
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')

    # on successful db insert, flash success

    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        venue = Venue.query.get(venue_id)
        venue.delete()
        db.session.commit()
        flash("Venue was successfully deleted.")

    except:
        db.session.rollback()

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    # data = [{
    #     "id": 4,
    #     "name": "Guns N Petals",
    # }, {
    #     "id": 5,
    #     "name": "Matt Quevedo",
    # }, {
    #     "id": 6,
    #     "name": "The Wild Sax Band",
    # }]
    data = Artist.query.with_entities(Artist.id, Artist.name)
    dd = db.session.query(Artist).all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    search_term = request.form.get('search_term', '')
    response = {"count": 0, "data": []}
    search_results = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term))).all()
    response['count'] = len(search_results)

    for result in search_results:
        shows = Show.query.filter_by(artist_id=result.id)
        upcoming = shows.filter(Show.start_time >= datetime.now()).all()
        item = {
            "id": result.id,
            "name": result.name,
            "num_upcoming_shows": len(upcoming)
        }
        response['data'].append(item)

    # response = {
    #     "count": 1,
    #     "data": [{
    #         "id": 4,
    #         "name": "Guns N Petals",
    #         "num_upcoming_shows": 0,
    #     }]
    # }
    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    artist = Artist.query.get(artist_id)
    shows = Show.query.filter_by(artist_id=artist_id)
    past = shows.filter(Show.start_time < datetime.now()).all()
    upcoming = shows.filter(Show.start_time >= datetime.now()).all()
    past_shows = []
    upcoming_shows = []
    for show in past:
        venue = Venue.query.get(show.artist_id)
        show_data = {
            "avenue_id": venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": str(show.start_time),
        }
        past_shows.append(show_data)
    for show in upcoming:
        venue = Venue.query.get(show.artist_id)
        show_data = {
            "venue_id": venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": str(show.start_time),
        }
        upcoming.append(show_data)

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres.split(','),
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_performance_venues,
        "seeking_description": artist.seeking_venues_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }

    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = {}
    try:
        retrieved_artist = Artist.query.get(artist_id)
        artist = {
            "id": retrieved_artist.id,
            "name": retrieved_artist.name,
            "genres": retrieved_artist.genres,
            "city": retrieved_artist.city,
            "state": retrieved_artist.state,
            "phone": retrieved_artist.phone,
            "website": retrieved_artist.website,
            "facebook_link": retrieved_artist.facebook_link,
            "seeking_venue": retrieved_artist.seeking_performance_venues,
            "seeking_description": retrieved_artist.seeking_venues_description,
            "image_link": retrieved_artist.image_link
        }
    except:
        flash('An error occurred.')
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    try:
        retrieved_artist = Artist.query.get(artist_id)
        retrieved_artist.name = request.form['name']
        retrieved_artist.city = request.form['city']
        retrieved_artist.state = request.form['state']
        retrieved_artist.phone = request.form['phone']
        retrieved_artist.facebook_link = request.form['facebook_link']
        retrieved_artist.website = request.form['website']
        if request.form['isSeeking']:
            retrieved_artist.seeking_performance_venues = True
        else:
            retrieved_artist.seeking_performance_venues = False
        retrieved_artist.seeking_venues_description = request.form['seekingDescription']
        retrieved_artist.genres = request.form.getlist('genres')
        retrieved_artist.image_link = request.form['image_link']
        db.session.add(retrieved_artist)
        db.session.commit()

    except:
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be Updated.')

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = {}
    try:
        retrieved_venue = Venue.query.get(venue_id)
        venue = {
            "id": retrieved_venue.id,
            "name": retrieved_venue.name,
            "genres": retrieved_venue.genres,
            "address": retrieved_venue.address,
            "city": retrieved_venue.city,
            "state": retrieved_venue.state,
            "phone": retrieved_venue.phone,
            "website": retrieved_venue.website,
            "facebook_link": retrieved_venue.facebook_link,
            "seeking_talent": retrieved_venue.seeking_talent,
            "seeking_description": retrieved_venue.seeking_talent_description,
            "image_link": retrieved_venue.image_link
        }
    except:
        flash('An error occurred.')
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    try:
        retrieved_venue = Venue.query.get(venue_id)
        retrieved_venue.name = request.form['name']
        retrieved_venue.city = request.form['city']
        retrieved_venue.state = request.form['state']
        retrieved_venue.phone = request.form['phone']
        retrieved_venue.facebook_link = request.form['facebook_link']
        retrieved_venue.website = request.form['website']
        if request.form['isSeeking']:
            retrieved_venue.seeking_talent = True
        else:
            retrieved_venue.seeking_performance_venues = False
        retrieved_venue.seeking_talent_description = request.form['seekingDescription']
        retrieved_venue.genres = request.form.getlist('genres')
        retrieved_venue.image_link = request.form['image_link']
        db.session.add(retrieved_venue)
        db.session.commit()

    except:
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be Updated.')
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    artist = Artist()

    try:
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        artist.facebook_link = request.form['facebook_link']
        artist.website = request.form['website']
        if request.form['isSeeking']:
            artist.seeking_performance_venues = True
        else:
            artist.seeking_performance_venues = False
        artist.seeking_venues_description = request.form['seekingDescription']
        artist.genres = request.form.getlist('genres')
        artist.image_link = request.form['image_link']
        db.session.add(artist)
        db.session.commit()

    except:
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    # on successful db insert, flash success
    # flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    data = []

    try:
        shows = Show.query.all()
        for show in shows:
            venue = Venue.query.get(show.venue_id)
            artist = Artist.query.get(show.artist_id)

            show_data = {
                "venue_id": venue.id,
                "venue_name": venue.name,
                "artist_id": artist.id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": str(show.start_time),
            }

            data.append(show_data)
    except:
        flash('An error occurred.')

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    show = Show()
    artist = Artist.query.get(request.form['artist_id'])
    venue = Venue.query.get(request.form['venue_id'])
    if artist and venue is not None:
        try:
            show.artist_id = request.form['artist_id']
            show.venue_id = request.form['venue_id']
            show.start_time = request.form['start_time']
            db.session.add(show)
            db.session.commit()
            flash('Show was successfully listed!')
        except:
            flash('An error occurred. Show could not be listed.')
    else:
        flash('Artist or Venue Not Existed')
    # on successful db insert, flash success

    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
