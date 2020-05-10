from flask import abort, render_template, request, Response, flash, \
                  redirect, url_for
from app.forms import ArtistForm, VenueForm, ShowForm
from app.models import Artist, Venue, Show, ArtistGenres, VenueGenres
from app.app import app, db
from app.custom_enum import GenreEnum, StateEnum


#----------------------------------------------------------------------------#
# Main Page
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#----------------------------------------------------------------------------#
# Venues
#----------------------------------------------------------------------------#


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

    return render_template('pages/search_venues.html', results=response,
                           search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    data = Venue.query.filter(Venue.id == venue_id).first().to_dict()

    return render_template('pages/show_venue.html', venue=data)


#    Create Venue
#    ----------------------------------------------------------------


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
        venue.genres = [VenueGenres(genre=GenreEnum[genre])
                        for genre in data.getlist('genres')]
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
        flash(f'Venue {data["name"]} was successfully listed!',
              'alert-success')
    else:
        # on unsuccessful db insert, flash an error
        flash(f'An error occurred. Venue {data["name"]} could not be listed. \
              Does the venue already exist?', 'alert-danger')

    return render_template('pages/home.html')


#    Update Venue
#    ----------------------------------------------------------------


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


#    Delete Venue
#    ----------------------------------------------------------------


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    data = {}
    error = False
    try:
        venue = Venue.query.filter_by(id=venue_id).first()
        # delete associated shows if no upcoming show is scheduled
        if venue.num_upcoming_shows == 0:
            db.session.query(Show).filter_by(venue_id=venue_id).delete()
        # this will fail if there are upcoming shows associated with the Venue
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
        flash(f'Venue {data["name"]} was successfully deleted!',
              'alert-success')
        return redirect(url_for('index'), code=301)

    # else stay on the page
    flash(f'An error occurred. Venue {data["name"]} could not be deleted. \
            Please make sure there are no upcoming shows scheduled \
            for this location', 'alert-danger')
    return redirect(url_for('show_venue', venue_id=venue_id), code=304)


#----------------------------------------------------------------------------#
# Artists
#----------------------------------------------------------------------------#


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
    return render_template('pages/search_artists.html', results=response,
                           search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    data = Artist.query.filter(Artist.id == artist_id).first().to_dict()

    return render_template('pages/show_artist.html', artist=data)


#    Create Artist
#    ----------------------------------------------------------------


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
        artist.genres = [ArtistGenres(genre=GenreEnum[genre])
                         for genre in data.getlist('genres')]
        db.session.add(artist)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        data = artist.to_dict()
        db.session.close()

    if not error:
        flash(f'Artist {data["name"]} was successfully listed!',
              'alert-success')
    else:
        flash(f'An error occurred. Artist {data["name"]} could not be listed. \
              Does the artist exist already?', 'alert-danger')

    return render_template('pages/home.html')


#    Update Artists
#    ----------------------------------------------------------------


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


#    Delete Artists
#    ----------------------------------------------------------------

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
        flash(f'Artist {data["name"]} was successfully deleted!',
              'alert-success')
        return redirect(url_for('index'), code=301)

    # else stay on the page
    flash(f'An error occurred. Artist {data["name"]} could not be deleted. \
            Please make sure there are no upcoming shows scheduled \
            for this location', 'alert-danger')
    return redirect(url_for('show_artist', artist_id=artist_id), code=304)


#----------------------------------------------------------------------------#
# Shows
#----------------------------------------------------------------------------#


@app.route('/shows')
def shows():
    data = [show.info for show in Show.query.all()]
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


#    Create Shows
#    ----------------------------------------------------------------


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False
    data = request.form

    try:
        venue = Venue.query.filter_by(id=data['venue_id']).first()
    except:
        error = True
        flash(f'There is no venue with ID {data["venue_id"]}', 'alert-danger')

    try:
        artist = Artist.query.filter_by(id=data['artist_id']).first()
    except:
        error = True
        flash(f'There is no artist with ID {data["artist_id"]}', 'alert-danger')

    try:
        starttime = data['start_time']
        show = Show(venue=venue, artist=artist, starttime=str(starttime))
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


#----------------------------------------------------------------------------#
# Error Handlers
#----------------------------------------------------------------------------#


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500
