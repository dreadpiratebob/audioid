<?php

$what = $_GET['what'];
if (!isset($what))
  $what = $_POST['what'];

$page  = "browse";
$title = "browsing " . (strlen($what) == 0 ? 'everything' : $what);

include("index.php");