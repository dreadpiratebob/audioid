<?php

class id3_tag_reader
{
  // variables
  var $sys_tags = array
  ( // array of possible sys tags (for last version of ID3)
    'TIT2',
    'TALB',
    'TPE1',
    'TPE2',
    'TRCK',
    'TYER',
    'TLEN',
    'USLT',
    'TPOS',
    'TCON',
    'TENC',
    'TCOP',
    'TPUB',
    'TOPE',
    'WXXX',
    'COMM',
    'TCOM'
  );
  var $tag_names = array
  ( // array of titles for sys tags
    'title',
    'album',
    'artist',
    'album_artist',
    'track',
    'year',
    'length',
    'lyrics',
    'desc',
    'genre',
    'encoded',
    'copyright',
    'publisher',
    'original_artist',
    'url',
    'comments',
    'composer'
  );
  var $old_sys_tags = array
  ( // array of possible sys tags (for old version of ID3)
    'TT2',
    'TAL',
    'TP1',
    'TRK',
    'TYE',
    'TLE',
    'ULT'
  );
  var $old_tag_names = array
  ( // array of titles for sys tags
    'title',
    'album',
    'author',
    'track',
    'year',
    'length',
    'lyrics'
  );
  
  // constructor
  function id3_tags_reader() {}
  
  // functions
  function get_tag_info($filename)
  {
    // read source file
    $file_size = filesize($filename);
    $file_ref  = fopen($filename, 'r');
    $sSrc    = fread($file_ref, $file_size);
    fclose($file_ref);
    
    // obtain base info
    if (substr($sSrc,0,3) == 'ID3')
    {
      $aInfo['filename'] = $filename;
      $aInfo['version']  = hexdec(bin2hex(substr($sSrc,3,1))).'.'.hexdec(bin2hex(substr($sSrc,4,1)));
    }
    
    // passing through possible tags of idv2 (v3 and v4)
    if ($aInfo['version'] == '4.0' || $aInfo['version'] == '3.0')
    {
      for ($i = 0; $i < count($this->sys_tags); $i++)
      {
        if (strpos($sSrc, $this->sys_tags[$i].chr(0)) != FALSE)
        {
          $s = '';
          $iPos = strpos($sSrc, $this->sys_tags[$i].chr(0));
          $iLen = hexdec(bin2hex(substr($sSrc,($iPos + 5),3)));
          
          $data = substr($sSrc, $iPos, 10 + $iLen);
          for ($a = 0; $a < strlen($data); $a++)
          {
            $char = substr($data, $a, 1);
            if ($char >= ' ' && $char <= '~')
            {
              $s .= $char;
            }
          }
          
          if (substr($s, 0, 4) == $this->sys_tags[$i])
          {
            $iSL = 4;
            if ($this->sys_tags[$i] == 'USLT')
            {
              $iSL = 7;
            }
            elseif ($this->sys_tags[$i] == 'TPE1')
            {
              $iSL = 5;
            }
            elseif ($this->sys_tags[$i] == 'TENC')
            {
              $iSL = 6;
            }
            $aInfo[$this->tag_names[$i]] = substr($s, $iSL);
          }
        }
      }
    }
    
    // passing through possible tags of idv2 (v2)
    if($aInfo['version'] == '2.0')
    {
      for ($i = 0; $i < count($this->old_sys_tags); $i++)
      {
        if (strpos($sSrc, $this->old_sys_tags[$i].chr(0)) != FALSE)
        {
          $s = '';
          $iPos = strpos($sSrc, $this->old_sys_tags[$i].chr(0));
          $iLen = hexdec(bin2hex(substr($sSrc,($iPos + 3),3)));
          
          $data = substr($sSrc, $iPos, 6 + $iLen);
          for ($a = 0; $a < strlen($data); $a++)
          {
            $char = substr($data, $a, 1);
            if ($char >= ' ' && $char <= '~')
            {
              $s .= $char;
            }
          }
          
          if (substr($s, 0, 3) == $this->old_sys_tags[$i])
          {
            $iSL = 3;
            if ($this->old_sys_tags[$i] == 'ULT')
            {
              $iSL = 6;
            }
            $aInfo[$this->old_tag_names[$i]] = substr($s, $iSL);
          }
        }
      }
    }
    return $aInfo;
  }
}

$id3_tag_reader = new id3_tag_reader()

?>