from api.dao.mysql_utils import get_cursor
from api.util.functions import get_type_name

query = \
"""SELECT
  s.id AS song_id,
  s.title AS song_title,
  ar.id AS artist_id,
  GROUP_CONCAT(ar.id ORDER BY s_ar.list_order SEPARATOR ", ") AS artist_ids,
  ar.name AS artist_name,
  GROUP_CONCAT(CONCAT(ar.name, s_ar.conjunction) ORDER BY s_ar.list_order SEPARATOR "") AS artist_names
FROM songs AS s
  LEFT JOIN songs_artists AS s_ar ON s_ar.song_id = s.id
    LEFT JOIN artists AS ar ON ar.id = s_ar.artist_id
WHERE s.id = 24
GROUP BY s.id
;"""

print('query:\n' + query)
with get_cursor() as cursor:
  ct = cursor.execute(query)
  for i in range(ct):
    print()
    result = cursor.fetchone()
    for key in result:
      print('%s: (%s) %s' % (key, get_type_name(result[key]), str(result[key])))