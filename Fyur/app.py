#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False, server_default="false")
    image_link = db.Column(db.String(120))

    

    def __repr__(self):
      return f'<Venue {self.id} {self.name} {self.city}{self.state} {self.address} {self.phone} {self.website}{self.genres} {self.image_link} {self.seeking_talent}{self.facebook_link} {self.shows}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    image_link = db.Column(db.String(120))

    def __repr__(self):
      return f'<Artist {self.id} {self.name} {self.genres} {self.city} {self.state} {self.phone} {self.website} {self.facebook_link} {self.seeking_venue} {self.seeking_description} {self.image_link} {self.show}>'

class Show(db.Model):
    __tablename__ = 'Show'

# TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'Venue.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    venue = db.relationship('Venue', backref=db.backref('shows', lazy=True))
    artist = db.relationship('Artist', backref=db.backref('shows', lazy=True))

    def __repr__(self):
        return f'<Show {self.id, self.start_time, self.artist}>'

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  
  # TODO: replace with real venues data.

  data = Venue.query.all()
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.

  search_term = request.form.get('search_term', '')
  venue_result = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()

  response = {
    "count": len(venue_result),
    "data": []
  }

  for result in venue_result:
    response["data"].append({
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": len(result.shows)
    })
  
  db.session.close()

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  venue = Venue.query.get(venue_id)
  
  # data = list(filter(lambda d: d['id'] == venue_id))[0]
  venue.query.all()
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  name = request.form.get('name', '')
  city = request.form.get('city', '')
  state = request.form.get('state', '')
  address = request.form.get('address', '')
  phone = request.form.get('phone', '')
  genres = request.form.get('genres', '')
  facebook_link = request.form.get('facebook_link', '')

  venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, facebook_link=facebook_link )

  try:
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  except:
    flash('An error occurred. Venue ' + new_venue.name + ' could not be listed.', category='error')
    db.session.rollback()

  finally:
    db.session.close()

  return render_template('pages/home.html', data=Venue.query.all())




@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  data = Artist.query.all()

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  search_term = get_value('search_term')
  artist_result = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()

  response = {
    "count": len(artist_result),
    "data": []
  }

  for result in artist_result:
    response["data"].append({
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": len(result.shows)
    })
  
  db.session.close()
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = Show.query.all()
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  # TODO: populate form with fields from artist with ID <artist_id>

  name = request.form.get('name', '')
  city = request.form.get('city', '')
  state = request.form.get('state', '')
  phone = request.form.get('phone', '')
  genres = request.form.get('genres', '')
  facebook_link = request.form.get('facebook_link', '')

  artist = Artist(name = name, city = city, state= state, phone= phone, genres=genres, facebook_link=facebook_link)


  try:
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  except:
    flash('An error occurred. Artist ' + new_artist.name + ' could not be listed.', category='error')
    print('exc_info(): ', exc_info())
    db.session.rollback()

  finally:
    db.session.close()

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  form = ArtistForm()
  venue = Arist.query.get(venue_id)

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # TODO: populate form with values from venue with ID <venue_id>

  form = VenueForm()
  venue = Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  form = VenueForm()
  form.validate_on_submit()

  venue = Venue.query.get(venue_id)
  print('request.form: ========== ', form.errors)

  try:
    venue.name = get_value('name')
    venue.genres = get_value('genres')
    venue.address = get_value('address')
    venue.city = get_value('city')
    venue.state = get_value('state')
    venue.phone = get_value('phone')
    venue.website = get_value('website_link')
    venue.seeking_talent = get_value('seeking_talent')
    venue.seeking_description = get_value('seeking_description')
    venue.facebook_link = get_value('facebook_link')
    venue.image_link = get_value('image_link')
    
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully updated!')

  except:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.', category='error')
    print('exc_info():==========', exc_info())
    db.session.rollback()

  finally:
    db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))
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
  name = request.form.get('name', '')
  city = request.form.get('city', '')
  state = request.form.get('state', '')
  phone = request.form.get('phone', '')
  genres = request.form.get('genres', '')
  facebook_link = request.form.get('facebook_link', '')


  artist = Artist(name=name,  city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link)

  db.session.add(artist)
  db.session.commit()

  try:
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  except:
    flash('An error occurred. Artist ' + new_artist.name + ' could not be listed.', category='error')
    db.session.rollback()

  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

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
  
  artist_id = request.form.get('artist_id', '')
  venue_id = request.form.get('venue_id', '')
  start_time = request.form.get('start_time')

  show = Show(artist_id=artist_id,  venue_id=venue_id, start_time=start_time)

  try:
    db.session.add(show)
    db.session.commit()
    flash('Show ' + request.form['id'] + ' was successfully listed!')

  except:
    flash('An error occurred. Show could not be listed.', category='error')
    db.session.rollback()

  finally:
    db.session.close()

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

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
