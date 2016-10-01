<?php

session_start();

$dsn = "mysql:dbname=audioid;host=127.0.0.1";

try
{
  $sql_link = new PDO($dsn, $db_username, $db_password);
}
catch (PDOException $pdoe)
{
  echo "db connection error: " . $pdoe->GetMessage();
}

?>