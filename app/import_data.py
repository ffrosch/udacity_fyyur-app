from app import db, Venue, Artist, Show, ArtistGenres, VenueGenres, GenreEnum, StateEnum
from data.venues import *
from data.artists import *
from data.shows import *

db.session.query(Show).delete()
db.session.query(ArtistGenres).delete()
db.session.query(VenueGenres).delete()
db.session.query(Artist).delete()
db.session.query(Venue).delete()

for i, x in enumerate([venues, artists]):

    for obj in x:
        if i == 0:
            o = Venue()
        if i == 1:
            o = Artist()

        o.name = obj['name']
        try:
            o.address = obj['address']
        except:
            pass
        o.city = obj['city']
        o.state = obj['state']
        o.phone = obj['phone']
        o.website = obj.get('website')
        o.facebook_link = obj.get('facebook_link')
        try:
            o.seeking_talent = obj['seeking_talent']
        except:
            o.seeking_venue = obj['seeking_venue']
        o.seeking_description = obj.get('seeking_description')
        o.image_link = obj['image_link']

        for genre in obj['genres']:
            if genre in [g.value for g in GenreEnum]:
                if isinstance(o, Venue):
                    g = VenueGenres(genre=genre)
                elif isinstance(o, Artist):
                    g = ArtistGenres(genre=genre)
                o.genres.append(g)
            
        db.session.add(o)
        
db.session.commit()

for show in shows:
    v = db.session.query(Venue).filter(Venue.name == show['venue_name']).first()
    a = db.session.query(Artist).filter(Artist.name == show['artist_name']).first()
    t = show['start_time']
    o = Show(venue=v, artist=a, starttime=t)
    db.session.add(o)

db.session.commit()