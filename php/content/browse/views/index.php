<? // yay fake 404s
   // just in case anyone stumbles across the right subfolder, this'll (hopefully) throw 'em off.
  $sn = $_SERVER['REQUEST_URI'];
?><!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<HTML><HEAD>
<TITLE>404 Not Found</TITLE>
</HEAD><BODY>
<H1>Not Found</H1>
The requested URL <?=$sn?> was not found on this server.<P>
<P>Additionally, a 404 Not Found
error was encountered while trying to use an ErrorDocument to handle the request.
<HR>
<ADDRESS>Apache/1.3.41 Server at hoza.us Port 80</ADDRESS>
</BODY></HTML>
