# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
import datetime
from forms import *
import ast

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)


# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    seeking_talent = db.Column(db.String(1))
    seeking_description = db.Column(db.String(500))

    def insert(self):
        db.session.add(self)
        try:
            db.session.commit()
        except Exception as e:
            print(f'Error {e} - while trying to commit to database')
            db.session.rollback()

    def delete(self):
        db.session.delete(self)
        try:
            db.session.commit()
        except Exception as e:
            print(f'Error {e} - while trying to commit to database')
            db.session.rollback()

    def update(self):
        try:
            db.session.commit()
        except Exception as e:
            print(f'Error {e} - while trying to commit to database')
            db.session.rollback()


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.String(1))
    seeking_description = db.Column(db.String(500))

    def insert(self):
        db.session.add(self)
        try:
            db.session.commit()
        except Exception as e:
            print(f'Error {e} - while trying to commit to database')
            db.session.rollback()

    def delete(self):
        db.session.delete(self)
        try:
            db.session.commit()
        except Exception as e:
            print(f'Error {e} - while trying to commit to database')
            db.session.rollback()

    def update(self):
        try:
            db.session.commit()
        except Exception as e:
            print(f'Error {e} - while trying to commit to database')
            db.session.rollback()


class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer)
    venue_id = db.Column(db.Integer)
    time = db.Column(db.DateTime)

    def insert(self):
        db.session.add(self)
        try:
            db.session.commit()
        except Exception as e:
            print(f'Error {e} - while trying to commit to database')
            db.session.rollback()

    def delete(self):
        db.session.delete(self)
        try:
            db.session.commit()
        except Exception as e:
            print(f'Error {e} - while trying to commit to database')
            db.session.rollback()

    def update(self):
        try:
            db.session.commit()
        except Exception as e:
            print(f'Error {e} - while trying to commit to database')
            db.session.rollback()


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


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
    venues = Venue.query.all()
    data = []
    # on itere à travers les venues et on créé tous les lieux
    # les bars
    for venue in venues:
        exists = False
        # les lieux
        for area in data:
            if venue.city in area.get('city'):
                exists = True
        print(f'la ville {venue.city} existe? {exists}')
        if not exists:
            data.append({"city": venue.city, "state": venue.state, "venues": []})

    # on itere encore une fois et on ajoute les bars aux différents lieux
    for venue in venues:
        # itere à travers les lieux
        for area in data:
            if venue.city in area.get('city'):
                area['venues'].append({"id": venue.id, "name": venue.name})
    return render_template('pages/venues.html', areas=data);


@app.route('/venues/search', methods=['POST'])
def search_venues():
    query = request.form.get("search_term")
    venues = Venue.query.filter(Venue.name.ilike('%' + query + '%')).all()
    count = len(venues)
    now = datetime.now()
    data = []
    for venue in venues:
        shows = Show.query.filter(Show.venue_id == venue.id).filter(Show.time > now).all()
        data.append({"id": venue.id, "name": venue.name, "num_upcoming_shows": len(shows)})
    response = {"count": count, "data": data}
    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    venue = Venue.query.filter_by(id=venue_id).first()
    shows = Show.query.filter_by(venue_id=venue_id).all()
    upcoming_shows = []
    upcoming_shows_count = 0
    past_shows = []
    past_shows_count = 0
    now = datetime.now()
    for show in shows:
        if show.time > now:
            upcoming_shows_count += 1
            artist = Artist.query.filter_by(id=show.artist_id).first()
            upcoming_shows.append(
                {"artist_id": artist.id, "artist_name": artist.name, "artist_image_link": artist.image_link,
                 "start_time": format_datetime(show.time.strftime("%m/%d/%Y, %H:%M:%S"), format='full')})
        else:
            past_shows_count += 1
            artist = Artist.query.filter_by(id=show.artist_id).first()
            past_shows.append(
                {"artist_id": artist.id, "artist_name": artist.name, "artist_image_link": artist.image_link,
                 "start_time": format_datetime(show.time.strftime("%m/%d/%Y, %H:%M:%S"), format='full')})

    data = {"name": venue.name, "city": venue.city, "state": venue.state, "address": venue.address,
            "phone": venue.phone, "image_link": venue.image_link, "facebook_link": venue.facebook_link,
            "website_link": venue.website_link, "genres": ast.literal_eval(venue.genres),
            "upcoming_shows": upcoming_shows,
            "upcoming_shows_count": upcoming_shows_count, "past_shows": past_shows,
            "past_shows_count": past_shows_count, "id": venue.id}

    # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
    print(data)
    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

    # on successful db insert, flash success
    data = request.form
    venue = Venue(name=data.get('name'), city=data.get('city'), state=data.get('state'), address=data.get('address'),
                  phone=data.get('phone'), image_link=data.get('image_link'), genres='["'+ data.get('genres')+'"]',
                  facebook_link=data.get('facebook_link'), website_link=data.get('website_link'),
                  seeking_talent=data.get('seeking_talent'), seeking_description=data.get('seeking_description'))
    venue.insert()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    venue = Venue.query.filter_by(id=venue_id).first()
    venue.delete()
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    artists = Artist.query.all()
    data = []
    for artist in artists:
        data.append({"id": artist.id, "name": artist.name})
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    query = request.form.get("search_term")
    artists = Artist.query.filter(Artist.name.ilike('%' + query + '%')).all()
    count = len(artists)
    now = datetime.now()
    data = []
    for artist in artists:
        shows = Show.query.filter(Show.artist_id == artist.id).filter(Show.time > now).all()
        data.append({"id": artist.id, "name": artist.name, "num_upcoming_shows": len(shows)})
    response = {"count": count, "data": data}
    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    artist = Artist.query.filter_by(id=artist_id).first()
    shows = Show.query.filter_by(artist_id=artist_id).all()
    upcoming_shows = []
    upcoming_shows_count = 0
    past_shows = []
    past_shows_count = 0
    now = datetime.now()
    for show in shows:
        if show.time > now:
            upcoming_shows_count += 1
            venue = Venue.query.filter_by(id=show.venue_id).first()
            upcoming_shows.append(
                {"venue_id": venue.id, "venue_name": venue.name, "venue_image_link": venue.image_link,
                 "start_time": format_datetime(show.time.strftime("%m/%d/%Y, %H:%M:%S"), format='full')})
        else:
            past_shows_count += 1
            venue = Venue.query.filter_by(id=show.venue_id).first()
            past_shows.append(
                {"venue_id": venue.id, "venue_name": venue.name, "venue_image_link": venue.image_link,
                 "start_time": format_datetime(show.time.strftime("%m/%d/%Y, %H:%M:%S"), format='full')})

    data = {"id": artist.id, "name": artist.name, "genres": ast.literal_eval(artist.genres), "city": artist.city,
            "state": artist.state,
            "phone": artist.phone, "seeking_venue": artist.seeking_venue, "image_link": artist.image_link,
            "facebook_link": artist.facebook_link, "website": artist.website_link,
            "seeking_description": artist.seeking_description, "past_shows": past_shows,
            "upcoming_shows": upcoming_shows, "past_shows_count": past_shows_count,
            "upcoming_shows_count": upcoming_shows_count}
    # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    a = Artist.query.filter_by(id=artist_id).first()

    artist = {
        "id": a.id,
        "name": a.name,
        "genres": a.genres,
        "city": a.city,
        "state": a.state,
        "phone": a.phone,
        "website": a.website_link,
        "facebook_link": a.facebook_link,
        "seeking_venue": a.seeking_venue,
        "seeking_description": a.seeking_description,
        "image_link": a.image_link
    }
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    data = request.form
    artist = Artist.query.filter_by(id=artist_id).first()
    artist.name=data.get('name')
    artist.city=data.get('city')
    artist.state=data.get('state')
    artist.phone=data.get('phone')
    artist.image_link=data.get('image_link')
    artist.genres='["' + data.get('genres') + '"]'
    artist.facebook_link=data.get('facebook_link')
    artist.website_link=data.get('website_link')
    artist.seeking_venue=data.get('seeking_talent')
    artist.seeking_description=data.get('seeking_description')
    artist.update()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    v = Venue.query.filter_by(id=venue_id).first()
    venue = {
        "id": v.id,
        "name": v.name,
        "genres": v.genres,
        "address": v.address,
        "city": v.city,
        "state": v.state,
        "phone": v.phone,
        "website": v.website_link,
        "facebook_link": v.facebook_link,
        "seeking_talent": v.seeking_talent,
        "seeking_description": v.seeking_description,
        "image_link": v.image_link
    }
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    data = request.form
    venue = Venue.query.filter_by(id=venue_id).first()
    venue.name = data.get('name')
    venue.city = data.get('city')
    venue.state = data.get('state')
    venue.address = data.get('address')
    venue.phone = data.get('phone')
    venue.image_link = data.get('image_link')
    venue.genres = '["' + data.get('genres') + '"]'
    venue.facebook_link = data.get('facebook_link')
    venue.website_link = data.get('website_link')
    venue.seeking_talent = data.get('seeking_talent')
    venue.seeking_description = data.get('seeking_description')
    venue.update()

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

    # on successful db insert, flash success
    data = request.form
    venue = Artist(name=data.get('name'), city=data.get('city'), state=data.get('state'),
                  phone=data.get('phone'), image_link=data.get('image_link'), genres='["'+ data.get('genres')+'"]',
                  facebook_link=data.get('facebook_link'), website_link=data.get('website_link'),
                  seeking_venue=data.get('seeking_talent'), seeking_description=data.get('seeking_description'))
    venue.insert()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows

    shows = Show.query.all()
    data = []
    for show in shows:
        venue = Venue.query.filter_by(id=show.venue_id).first()
        artist = Artist.query.filter_by(id=show.artist_id).first()
        data.append({"venue_id": venue.id, "venue_name": venue.name, "artist_id": artist.id, "artist_name": artist.name, "artist_image_link": artist.image_link, "start_time": format_datetime(str(show.time), 'full')})


    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    data = request.form
    show = Show(artist_id=data.get('artist_id'), venue_id=data.get('venue_id'), time=data.get('start_time'))
    show.insert()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
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
