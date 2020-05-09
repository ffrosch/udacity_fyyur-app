#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import enum
import babel
from datetime import datetime
from flask import Flask, abort, render_template, request, Response, flash, redirect, url_for
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import backref
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from custom_enum import GenreEnum, StateEnum


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

GenreEnum_ = db.Enum(GenreEnum, name='genres', values_callable=lambda x: [str(e.value) for e in GenreEnum])
StateEnum_ = db.Enum(StateEnum, name='states', values_callable=lambda x: [str(e.value) for e in StateEnum])

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
  __tablename__ = 'Venue'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False, unique=True)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(StateEnum_, nullable=False)
  address = db.Column(db.String(120), nullable=False)
  phone = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  website = db.Column(db.String(120))
  seeking_talent = db.Column(db.Boolean, default=False)
  seeking_description = db.Column(db.String())
  genres = db.relationship('VenueGenres', backref='venue', lazy='dynamic',
                            cascade="all, delete-orphan")
  
  shows = db.relationship('Show', lazy='select', backref='venue')
  artists = association_proxy('shows', 'artist')
  
  @property
  def past_shows(self):
    return Show.query.filter(
      Show.starttime < datetime.now(),
      Show.venue_id == self.id).all()

  @property
  def upcoming_shows(self):
    return Show.query.filter(
      Show.starttime > datetime.now(),
      Show.venue_id == self.id).all()

  @property
  def num_upcoming_shows(self):
    return len(self.upcoming_shows)

  @property
  def num_past_shows(self):
    return len(self.past_shows)
  
  @property
  def summary(self):
    return  {
      'id': self.id,
      'name': self.name,
      'num_upcoming_shows': self.num_upcoming_shows
    }

  # @property
  # def show_count(self):
  #   # return db.object_session(self).query(Show).with_parent(self).count()
  #   return len(self.shows)

  def __repr__(self):
    return f'<Venue: {self.name}>'
  
  def get_areas_with_venue():
    locations = Venue.query.distinct(Venue.city, Venue.state).all()
    return [{'city': l.city, 'state': l.state} for l in locations]
  
  def get_venues_by_area(city, state):
    return Venue.query.filter_by(city=city, state=state).all()

  def get_venues_by_partial_name(name):
    return Venue.query.filter(Venue.name.ilike(f'%{name}%')).all()

  def to_dict(self):
    return {
      'id': self.id,
      'name': self.name,
      'city': self.city,
      'state': self.state,
      'address': self.address,
      'phone': self.phone,
      'image_link': self.image_link,
      'facebook_link': self.facebook_link,
      'website': self.website,
      'seeking_talent': self.seeking_talent,
      'seeking_description': self.seeking_description,
      'genres': [g.genre for g in self.genres],
      "past_shows": [{
        'artist_id': show.artist.id,
        'artist_name': show.artist.name,
        'artist_image_link': show.artist.image_link,
        'start_time': show.starttime.isoformat() + 'Z'
      } for show in self.past_shows],
      "upcoming_shows": [{
        'artist_id': show.artist.id,
        'artist_name': show.artist.name,
        'artist_image_link': show.artist.image_link,
        'start_time': show.starttime.isoformat() + 'Z'
      } for show in self.upcoming_shows],
      "past_shows_count": self.num_past_shows,
      "upcoming_shows_count": self.num_upcoming_shows
    }
    
  def from_dict(self, data):
    for field in ['name', 'city', 'state', 'address', 'phone', 'facebook_link']:
      if field in data:
        setattr(self, field, data[field])
    if 'genres' in data:
      self.genres = [VenueGenres(genre=GenreEnum[genre]) for genre in data.getlist('genres')]


class VenueGenres(db.Model):
  __tablename__ = 'VenueGenres'

  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
  genre = db.Column(GenreEnum_, primary_key=True)
  
  def __repr__(self):
    return f'{self.genre}'


class Artist(db.Model):
  __tablename__ = 'Artist'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False, unique=True)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(StateEnum_, nullable=False)
  phone = db.Column(db.String(120), nullable=False)
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  website = db.Column(db.String(120))
  seeking_venue = db.Column(db.Boolean, default=False)
  seeking_description = db.Column(db.String())
  genres = db.relationship('ArtistGenres', backref='artist', lazy='dynamic',
                            cascade="all, delete-orphan")

  def __repr__(self):
    return f'Artist: {self.name}'

  @property
  def past_shows(self):
    return Show.query.filter(
      Show.starttime < datetime.now(),
      Show.artist_id == self.id).all()

  @property
  def upcoming_shows(self):
    return Show.query.filter(
      Show.starttime > datetime.now(),
      Show.artist_id == self.id).all()

  @property
  def num_upcoming_shows(self):
    return len(self.upcoming_shows)

  @property
  def num_past_shows(self):
    return len(self.past_shows)

  @property
  def summary(self):
    return  {
      'id': self.id,
      'name': self.name,
      'num_upcoming_shows': self.num_upcoming_shows
    }

  def get_artists_by_partial_name(name):
    return Artist.query.filter(Artist.name.ilike(f'%{name}%')).all()

  def to_dict(self):
    return {
      'id': self.id,
      'name': self.name,
      'city': self.city,
      'state': self.state,
      'phone': self.phone,
      'image_link': self.image_link,
      'facebook_link': self.facebook_link,
      'website': self.website,
      'seeking_venue': self.seeking_venue,
      'seeking_description': self.seeking_description,
      'genres': [g.genre for g in self.genres],
      'past_shows': [{
        'venue_id': show.venue.id,
        'venue_name': show.venue.name,
        'venue_image_link': show.venue.image_link,
        'start_time': show.starttime.isoformat() + 'Z'
      } for show in self.past_shows],
      'upcoming_shows': [{
        'venue_id': show.venue.id,
        'venue_name': show.venue.name,
        'venue_image_link': show.venue.image_link,
        'start_time': show.starttime.isoformat() + 'Z'
      } for show in self.upcoming_shows],
      'past_shows_count': self.num_past_shows,
      'upcoming_shows_count': self.num_upcoming_shows
      }

  def from_dict(self, data):
    for field in ['name', 'city', 'state', 'phone', 'facebook_link']:
      if field in data:
        setattr(self, field, data[field])
    if 'genres' in data:
      self.genres = [ArtistGenres(genre=GenreEnum[genre]) for genre in data.getlist('genres')]

class ArtistGenres(db.Model):
  __tablename__ = 'ArtistGenres'
  
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
  genre = db.Column(GenreEnum_, primary_key=True)

  def __repr__(self):
    return f'{self.genre}'


class Show(db.Model):
  __tablename__ = 'Show'
  
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
  starttime = db.Column(db.DateTime, primary_key=True)

  artist = db.relationship('Artist', lazy='joined')
  
  @property
  def info(self):
    return {
      'venue_id': self.venue.id,
      'venue_name': self.venue.name,
      'artist_id': self.artist.id,
      'artist_name': self.artist.name,
      'artist_image_link': self.artist.image_link,
      'start_time': self.starttime.isoformat() + 'Z'
    }
  
  def __init__(self, venue=None, artist=None, starttime=None):
    self.venue = venue
    self.artist = artist
    self.starttime = starttime
        
  def __repr__(self):
      return f'<{self.artist.name} @ {self.venue.name}: {self.starttime}>'


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
  data = Venue.get_areas_with_venue()
  for d in data:
    venues = Venue.get_venues_by_area(d['city'], d['state'])
    d['venues'] = [venue.summary for venue in venues]

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  venues = Venue.get_venues_by_partial_name(search_term)
  response = {
    'count': len(venues),
    'data': [venue.summary for venue in venues]
  }
  
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  data = Venue.query.filter(Venue.id == venue_id).first().to_dict()

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  data = request.form

  try:
    venue = Venue()
    venue.name = data['name']
    venue.city = data['city']
    venue.state = data['state']
    venue.address = data['address']
    venue.phone = data.get('phone', '')
    venue.facebook_link = data.get('facebook_link', '')
    venue.genres = [VenueGenres(genre=GenreEnum[genre]) for genre in data.getlist('genres')]
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    data = venue.to_dict()
    db.session.close()

  if not error:
    # on successful db insert, flash success
    flash(f'Venue {data["name"]} was successfully listed!', 'alert-success')
  else:
    # on unsuccessful db insert, flash an error
    flash(f'An error occurred. Venue {data["name"]} could not be listed. Does the venue exist already?', 'alert-danger')

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  data = {}
  error = False
  try:
    venue = Venue.query.filter_by(id=venue_id).first()
    # delete associated shows if no upcoming show is scheduled
    if venue.num_upcoming_shows == 0:
      db.session.query(Show).filter_by(venue_id=venue_id).delete()
    # this will fail if there are still upcoming shows associated with the Venue
    db.session.delete(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    data = venue.to_dict()
    db.session.close()

  # on success redirect to index
  if not error:
    flash(f'Venue {data["name"]} was successfully deleted!', 'alert-success')
    return redirect(url_for('index'), code=301)

  # else stay on the page
  flash(f'An error occurred. Venue {data["name"]} could not be deleted. \
          Please make sure there are no upcoming shows scheduled for this location',
          'alert-danger')
  return redirect(url_for('show_venue', venue_id=venue_id), code=304)


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.all()
  data = [artist.summary for artist in artists]
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  artists = Artist.get_artists_by_partial_name(search_term)
  response = {
    "count": len(artists),
    "data": [artist.summary for artist in artists]
  }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  data = Artist.query.filter(Artist.id == artist_id).first().to_dict()
  
  return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.filter(Artist.id == artist_id).first()
  form = ArtistForm(obj=artist)
  form.genres.data = [GenreEnum(str(genre)).name for genre in artist.genres]

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  data = request.form
  artist = Artist.query.filter(Artist.id == artist_id).first()
  try:
    artist.from_dict(data)
    db.session.commit()
    flash('Update successful!', 'alert-success')
  except:
    error = True
    db.session.rollback()
    flash('Update failed!', 'alert-danger')
  finally:
    db.session.close()
  
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.filter(Venue.id == venue_id).first()
  form = VenueForm(obj=venue)
  form.genres.data = [GenreEnum(str(genre)).name for genre in venue.genres]

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  data = request.form
  venue = Venue.query.filter(Venue.id == venue_id).first()
  try:
    venue.from_dict(data)
    db.session.commit()
    flash('Update successful!', 'alert-success')
  except:
    error = True
    db.session.rollback()
    flash('Update failed!', 'alert-danger')
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
  error = False
  data = request.form

  try:
    artist = Artist()
    artist.name = data['name']
    artist.city = data['city']
    artist.state = data['state']
    artist.phone = data.get('phone', '')
    artist.facebook_link = data.get('facebook_link', '')
    artist.genres = [ArtistGenres(genre=GenreEnum[genre]) for genre in data.getlist('genres')]
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    data = artist.to_dict()
    db.session.close()

  if not error:
    # on successful db insert, flash success
    flash(f'Artist {data["name"]} was successfully listed!', 'alert-success')
  else:
    # on unsuccessful db insert, flash an error
    flash(f'An error occurred. Artist {data["name"]} could not be listed. Does the artist exist already?', 'alert-danger')

  return render_template('pages/home.html')

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  data = {}
  error = False
  try:
    artist = Artist.query.filter_by(id=artist_id).first()
    # delete all associated shows if no upcoming show is scheduled
    if artist.num_upcoming_shows == 0:
      db.session.query(Show).filter_by(artist_id=artist_id).delete()
    # this will fail if there are still shows associated with the Artist
    db.session.delete(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    data = artist.to_dict()
    db.session.close()

  # on success redirect to index
  if not error:
    flash(f'Artist {data["name"]} was successfully deleted!', 'alert-success')
    return redirect(url_for('index'), code=301)

  # else stay on the page
  flash(f'An error occurred. Artist {data["name"]} could not be deleted. \
          Please make sure there are no upcoming shows scheduled for this location',
          'alert-danger')
  return redirect(url_for('show_artist', artist_id=artist_id), code=304)

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = [show.info for show in Show.query.all()]
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  data = request.form
  
  try:
    venue = Venue.query.filter_by(id=data['venue_id']).first()
  except:
    error = True
    flash(f'There is no venue with ID {venue_id}', 'alert-danger')
    
  try:
    artist = Artist.query.filter_by(id=data['artist_id']).first()
  except:
    error = True
    flash(f'There is no artist with ID {artist_id}', 'alert-danger')

  try:
    starttime = data['start_time']
    show = Show(venue=venue , artist=artist , starttime=str(starttime))
    print(show)
    db.session.add(show)
    db.session.commit()
  except:
    error = True
    flash('Something went wrong. Maybe an invalid start time?', 'alert-danger')
  finally:
    db.session.close()

  if not error:
    flash('Show was successfully listed!', 'alert-success')
  
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

app.config.update({"KONCH_CONTEXT": {"db": db,
                                     "Artist": Artist,
                                     "Venue": Venue,
                                     "ArtistGenres": ArtistGenres,
                                     "VenueGenres": VenueGenres,
                                     "Show": Show
                                     }})
app.config.update({'KONCH_SHELL': 'ipy'})