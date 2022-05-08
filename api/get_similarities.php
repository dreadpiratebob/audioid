<?php

$song_id = $_GET['song_id'];
if (!isset($song_id) || !is_numeric(!$song_id))
{
  http_response_code(400);
  echo "a parsable song id wasn't found.";
  die();
}

$song_id = (int)floor($song_id); // i'm gonna trust the floor function to clean out any weird values in the number and to give me a clean int.

include("../php/utils/init_db_vars.php");

$query = "SELECT song2 AS song_id, similarity AS similarity FROM song_similarity WHERE song1 = {$song_id};";
$sql_similarities = $sql_link->query($query);

header("Content-Type: text/json");

echo "{\n  similarities:\n  [\n";

for ($i = 0; $i < )
{
  $sim = $sql_similarities->fetch(PDO::FETCH_ASSOC);
  echo "    {\n";
  echo "      id: {$sim['id']},\n";
  echo "      similarity: {$sim['similarity']}\n";
  echo "    }\n";
}

echo "  ]\n}";

?>