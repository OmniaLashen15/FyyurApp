#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *
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
  data = []
  venues = Venue.query.all()
  sites = set()  # It is used to prevent duplicate values of venues

  for venue in venues:  
    sites.add((venue.city, venue.state)) # put the city and states in tuples which are stored in sites

  for site in sites:
    data.append({
        "city": site[0],
        "state": site[1],
        "venues": []
    })

  for venue in venues:
    num_upcoming_shows = 0 # Set all venues' upcoming shows numbers to zero

    shows = Show.query.filter_by(venue_id=venue.id).all()
    present_date = datetime.now() # To get the present date 

    for show in shows:
      if show.start_time > present_date: # comparing the present date by the start date of the show to increment number of upcoming shows
          num_upcoming_shows += 1

    for VenueSite in data:
      if venue.state == VenueSite['state'] and venue.city == VenueSite['city']:
        VenueSite['venues'].append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": num_upcoming_shows
        })
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  outcome = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')) # To get the data which is like to that written in search, if it is not found false will be returned.

  response={
    "count": outcome.count(),
    "data": outcome
  }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id): # Displays each venue page with its venue's id
  
  venue = Venue.query.get(venue_id)
  shows = Show.query.filter_by(venue_id=venue_id).all()
  PreviousShows = []
  UpcomingShows = []
  present_time = datetime.now()

  for show in shows:
    data = {
          "artist_id": show.artist_id,
          "artist_name": show.artist.name,
           "artist_image_link": show.artist.image_link,
           "start_time": format_datetime(str(show.start_time))
        }
    if show.start_time < present_time:
      PreviousShows.append(data)
    else:
      UpcomingShows.append(data)
      
  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description":venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": PreviousShows,
    "upcoming_shows": UpcomingShows,
    "past_shows_count": len(PreviousShows),
    "upcoming_shows_count": len(UpcomingShows)
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  venue_form = VenueForm()
  return render_template('forms/new_venue.html', form=venue_form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  try: 
    venue_form = VenueForm()             # To pass the data from the form to database and create new venue
    venue = Venue(name=venue_form.name.data, city=venue_form.city.data, state=venue_form.state.data, address=venue_form.address.data,
                  phone=venue_form.phone.data, image_link=venue_form.image_link.data,genres=venue_form.genres.data, 
                  facebook_link=venue_form.facebook_link.data, seeking_description=venue_form.seeking_description.data,
                  website=venue_form.website.data, seeking_talent=venue_form.seeking_talent.data)
    
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  except:
    db.session.rollback()
    flash('There is an error. Venue ' + request.form['name'] + ' could not be listed.')
  
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.get(venue_id)
    VenueName = venue.name

    db.session.delete(venue)
    db.session.commit()

    flash('Venue ' + VenueName + ' was deleted')
  except:
    flash('There is an error and Venue ' + VenueName + ' was not deleted')
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = []

  Artists = Artist.query.all()

  for artist in Artists:
    data.append({
        "id": artist.id,
        "name": artist.name
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')

  
  result = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')) # We use it here the same as venue 

  response={
    "count": result.count(),
    "data": result
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):           # Displays each artist page with its artist's id
  artist = Artist.query.get(artist_id)
  shows = Show.query.filter_by(artist_id=artist_id).all()
  PreviousShows = []
  UpcomingShows = []
  present_time = datetime.now()

  for show in shows:
    data = {
          "venue_id": show.venue_id,
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time": format_datetime(str(show.start_time))
        }
    if show.start_time < present_time:
      PreviousShows.append(data)
    else:
      UpcomingShows.append(data)
      
  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "facebook_link": artist.facebook_link,
    "image_link": artist.image_link,
    "past_shows": PreviousShows,
    "upcoming_shows": UpcomingShows,
    "past_shows_count": len(PreviousShows),
    "upcoming_shows_count": len(UpcomingShows)
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist_form = ArtistForm()

  artist = Artist.query.get(artist_id)

  ArtistData = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "facebook_link": artist.facebook_link,
        "image_link": artist.image_link
    }

  return render_template('forms/edit_artist.html', form=artist_form, artist=ArtistData)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try:
    artist_form = ArtistForm()
    artist = Artist.query.get(artist_id)

    artist.name = artist_form.name.data
    artist.phone = artist_form.phone.data
    artist.state = artist_form.state.data
    artist.city = artist_form.city.data
    artist.genres = artist_form.genres.data
    artist.image_link = artist_form.image_link.data
    artist.facebook_link = artist_form.facebook_link.data
    
    db.session.commit()
    flash('The Artist ' + request.form['name'] + ' has been successfully updated!')
  except:
    db.session.rolback()
    flash('There is an error and the update unsuccessful')
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue_form = VenueForm()
  venue = Venue.query.get(venue_id)
  venue={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
  }
  
  return render_template('forms/edit_venue.html', form=venue_form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try:
    venue_form = VenueForm()
    venue = Venue.query.get(venue_id)
  
    venue.name = venue_form.name.data
    venue.genres = venue_form.genres.data
    venue.city = venue_form.city.data
    venue.state = venue_form.state.data
    venue.address = venue_form.address.data
    venue.phone = venue_form.phone.data
    venue.facebook_link = venue_form.facebook_link.data
    venue.website = venue_form.website.data
    venue.image_link = venue_form.image_link.data
    venue.seeking_talent = venue_form.seeking_talent.data
    venue.seeking_description = venue_form.seeking_description.data

    db.session.commit()
    flash('venue ' + request.form['name'] + ' has been successfully updated!')
  except:
    db.session.rollback()
    flash('An error occured while trying to update Venue')
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  artist_form = ArtistForm()
  return render_template('forms/new_artist.html', form=artist_form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  try:
    artist_form = ArtistForm()

    artist = Artist(name=artist_form.name.data, city=artist_form.city.data, state=artist_form.city.data,
                    phone=artist_form.phone.data, genres=artist_form.genres.data, 
                    image_link=artist_form.image_link.data, facebook_link=artist_form.facebook_link.data)
    
    db.session.add(artist)
    db.session.commit()

    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('There is an error. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')


@app.route('/artist/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  try:

    artist = Artist.query.get(artist_id)
    ArtistName = artist.name

    db.session.delete(artist)
    db.session.commit()

    flash('Artist ' + ArtistName + ' was deleted')
  except:
    flash('There is an error and Artist ' + ArtistName + ' was not deleted')
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('index'))

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.order_by(db.desc(Show.start_time))

  ShowData = []

  for show in shows:
    ShowData.append({
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": format_datetime(str(show.start_time))
    })

  return render_template('pages/shows.html', shows=ShowData)

@app.route('/shows/create')
def create_shows():
  show_form = ShowForm()
  return render_template('forms/new_show.html', form=show_form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    show = Show(artist_id=request.form['artist_id'], venue_id=request.form['venue_id'],
                start_time=request.form['start_time'])

    db.session.add(show)
    db.session.commit()

    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('There ia an error. Show could not be listed.')
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
