from api.logic.songs import get_song, get_song_for_streaming
from api.models.db_models import FileTypes
from api.util.audioid.songs import DownloadSongPathParams
from api.util.http import HTTPHeaders, HTTPStatusCodes, HTTPMIMETypes, Response
from api.util.http_path import AvailablePath

_mime_type_to_file_type = \
{
  HTTPMIMETypes.MEDIA_FLAC: FileTypes.FLAC,
  HTTPMIMETypes.MEDIA_MPEG: FileTypes.MP3
}
def get(environment:dict, headers:dict, path_params:dict, query_params:dict, body) -> Response:
  grievances = []
  
  song_id, song_id_error = DownloadSongPathParams.SONG_ID.get_value(path_params, True)
  if song_id_error is not None:
    grievances.append(str(song_id_error))
  
  accept = headers.get(HTTPHeaders.ACCEPT, HTTPMIMETypes.MEDIA_MPEG)
  file_type = _mime_type_to_file_type.get(accept, None)
  if file_type is None:
    grievances.append('the "accept" header must be set to one of %s.' % (', '.join([str(x) for x in _mime_type_to_file_type]), ))
  
  if len(grievances) > 0:
    return Response('\n'.join(grievances), HTTPStatusCodes.HTTP400)
  
  content = get_song_for_streaming(song_id, file_type)
  if content is None:
    song = get_song(song_id, False, False, False, False)
    message = 'that track doesn\'t have a %s file.' % (str(file_type), )
    if song is None:
      message = 'no track with the id %s was found.' % (song_id, )
    
    return Response(message, HTTPStatusCodes.HTTP404, mime_type=HTTPMIMETypes.APPLICATION_JSON)
  
  return Response(content, HTTPStatusCodes.HTTP200, data_is_raw=True)

def get_help():
  return AvailablePath(path_params=tuple(param for param in DownloadSongPathParams), description='this endpoint provides the content of a particular song.  it uses the accept header to figure out what format the audio contents should be provided in; use "media/flac" for flac or "media/mpeg" for mp3.')