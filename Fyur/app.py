#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime
from sqlalchemy import desc
import pytz
utc=pytz.UTC
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

    # db.relationship

    shows = db.relationship('Show', backref=db.backref('venues', lazy=True))

    def __repr__(self):
      return f'<Venue {self.id} {self.name} {self.city}{self.state} {self.address} {self.phone} {self.website}{self.genres} {self.image_link} {self.seeking_talent}{self.facebook_link} {self.shows}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate [DONE]

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

    # db.relationship

    shows = db.relationship('Show', backref=db.backref('artist.id', lazy=True))

    def __repr__(self):
      return f'<Artist {self.id} {self.name} {self.genres} {self.city} {self.state} {self.phone} {self.website} {self.facebook_link} {self.seeking_venue} {self.seeking_description} {self.image_link} {self.show}>'

class Show(db.Model):
    __tablename__ = 'Show'

# TODO: implement any missing fields, as a database migration using Flask-Migrate [DONE]

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration. [DONE]

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'Venue.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)


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
  
  # TODO: replace with real venues data. [DONE]
  # create a dictionary for sorting venues according to city and state.[DONE]

  data=[]
  venues=Venue.query.distinct('city','state').all()
  for venue in venues:
    ven=Venue.query.filter_by(city=venue.city).all()
    num_upcomming_shows=Venue.query.filter_by(city=venue.city,state=venue.state)\
    .join(Show).filter(Show.start_time > datetime.utcnow().replace(tzinfo=pytz.UTC)).count()
    mydata={
      "city":venue.city,
      "state":venue.state,
      "venues":ven,
      "num_upcomming_shows":num_upcomming_shows
    }
    data.append(mydata)
  # num_shows should be aggregated based on number of upcoming shows per venue.
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive [DONE].

  search = "%{}%".format(request.form.get('search_term', ''))
  venues = Venue.query.filter(Venue.name.ilike(search)).all()
  count=len(venues)
  response={
    "count": count,
    "data": venues
  }

  db.session.close()

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id 
  # TODO: replace with real venue data from the venues table, using venue_id [DONE]
  myvenue = Venue.query.get(venue_id)
  if(len(Venue.query.filter_by(id=venue_id).all())!=0):
    past = []
    for show in Show.query.filter(Show.venue_id==venue_id).order_by(desc(Show.start_time)).limit(10):
      if utc.localize(show.start_time) < utc.localize(datetime.now()):
        past.append({
          "artist_id":show.artist_id,
          "artist_name":Artist.query.filter(Artist.id==show.artist_id).first().name,
          "artist_image_link":Artist.query.filter(Artist.id==show.artist_id).first().image_link,
          "start_time":show.start_time.strftime("%c")
        })
    upcoming = []
    for show in Show.query.filter(Show.venue_id==venue_id).order_by(desc(Show.start_time)).limit(10):
      if utc.localize(show.start_time) > utc.localize(datetime.now()):
        upcoming.append({
        "artist_id":show.artist_id,
        "artist_name":Artist.query.filter(Artist.id==show.artist_id).first().name,
        "artist_image_link":Artist.query.filter(Artist.id==show.artist_id).first().image_link,
        "start_time":show.start_time.strftime("%c")
        })
    
    data={
      "id": myvenue.id,
      "name": myvenue.name,
      "genres": myvenue.genres,
      "address": myvenue.address,
      "city": myvenue.city,
      "state": myvenue.state,
      "phone": myvenue.phone,
      "website": myvenue.website,
      "facebook_link": myvenue.facebook_link,
      "seeking_talent": myvenue.seeking_talent,
      # "seeking_description": myvenue.seeking_description,
      "image_link": myvenue.image_link,
      "past_shows":past,
      "upcoming_shows":upcoming,
      "past_shows_count": len(past),
      "upcoming_shows_count": len(upcoming)
    }
    data = list(filter(lambda d: d['id'] == venue_id, [data]))[0]
  return render_template('pages/show_venue.html',past_shows=past,upcoming_shows=upcoming,venue=data)


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
  status = False
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    status = True
    flash('Artist successfully deleted!')

  except:
    print(exc_info())
    db.session.rollback()
    status = False
    flash('Error deleting artist', category='error')

  finally:
    db.session.close()
  
  return jsonify({
    'success': status
    })


  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database [DONE]

  data = Artist.query.all()

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  search_term = request.form.get('search_term', '')
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
  myartist = Artist.query.get(artist_id)
  if(len(Artist.query.filter_by(id=artist_id).all())!=0):
    past = []
    for show in Show.query.filter(Show.artist_id==artist_id).order_by(desc(Show.start_time)).limit(10):
      if show.start_time < utc.localize(datetime.now()):
        past.append({
          "venue_id":show.venue_id,
          "venue_name":Venue.query.filter(Venue.id==show.venue_id).first().name,
          "venue_image_link":Venue.query.filter(Venue.id==show.venue_id).first().image_link,
          "start_time":show.start_time.strftime("%c")
          
        })  
    upcoming = []
    for show in Show.query.filter(Show.artist_id==artist_id).order_by(desc(Show.start_time)).limit(10):
      if utc.localize(show.start_time) > utc.localize(datetime.now()):
        upcoming.append({
          "venue_id":show.venue_id,
          "venue_name":Venue.query.filter(Venue.id==show.venue_id).first().name,
          "venue_image_link":Venue.query.filter(Venue.id==show.venue_id).first().image_link,
          "start_time":show.start_time.strftime("%c")
        })

    data={
      "id": myartist.id,
      "name": myartist.name,
      "genres": myartist.genres,
      "city": myartist.city,
      "state": myartist.state,
      "phone": myartist.phone,
      "website": myartist.website,
      "facebook_link": myartist.facebook_link,
      "seeking_venue": myartist.seeking_venue,
      "seeking_description": myartist.seeking_description,
      "image_link": myartist.image_link,
      "past_shows": past,
      "upcoming_shows": upcoming,
      "past_shows_count": len(past),
      "upcoming_shows_count": len(upcoming)
    }
    data = list(filter(lambda d: d['id'] == artist_id, [data]))[0]
  return render_template('pages/show_artist.html',past_shows=past,upcoming_shows=upcoming,artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

  # TODO: populate form with fields from artist with ID <artist_id> 
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  artist = Artist.query.get(artist_id)
  
  try:
    artist.name = request.form.get('name', '')
    artist.city = request.form.get('city', '')
    artist.state = request.form.get('state', '')
    artist.address = request.form.get('address', '')
    artist.phone = request.form.get('phone', '')
    artist.genres = request.form.get('genres', '')
    artist.facebook_link = request.form.get('facebook_link', '')
    
    db.session.commit()
    flash('artist ' + request.form['name'] + ' was successfully updated!')

  except:
    flash('An error occurred. artist ' + request.form['name'] + ' could not be updated.', category='error')
    print('exc_info():==========', exc_info())
    db.session.rollback()

  finally:
    db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))
 

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    # TODO: populate form with values from venue with ID <venue_id>

  form = VenueForm()
  venue = Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  venue = Venue.query.get(venue_id)

  try:
    venue.name = request.form('name')
    venue.genres = request.form('genres')
    venue.address = request.form('address')
    venue.city = request.form('city')
    venue.state = request.form('state')
    venue.phone = request.form('phone')
    venue.website = request.form('website_link')
    venue.seeking_talent = request.form('seeking_talent')
    venue.seeking_description = request.form('seeking_description')
    venue.facebook_link = request.form('facebook_link')
    venue.image_link = request.form('image_link')
    
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully updated!')

  except:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.', category='error')
    print('exc_info():==========', exc_info())
    db.session.rollback()

  finally:
    db.session.close()
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
  data=[]
  mydatas=db.session.query(Venue,Show,Artist).join(Show,Venue.id==Show.venue_id).join(Artist,Show.artist_id==Artist.id).filter(Show.start_time > datetime.now()).all()
  for mydata in mydatas:
    d=mydata.Show.start_time
    mydata={
      "venue_id":mydata.Venue.id,
      "venue_name": mydata.Venue.name,
      "artist_id": mydata.Artist.id,
      "artist_name":mydata.Artist.name,
      "artist_image_link": mydata.Artist.image_link,
      "start_time": d.strftime("%c")
    }
    data.append(mydata)
  return render_template('pages/shows.html', shows=data)

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
  # TODO: insert form data as a new Show record in the db, instead [DONE]
  
  artist_id = request.form.get('artist_id', '')
  venue_id = request.form.get('venue_id', '')
  start_time = request.form.get('start_time')
  print(start_time)

  show = Show(artist_id=artist_id,  venue_id=venue_id, start_time=start_time)

  try:
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')

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
