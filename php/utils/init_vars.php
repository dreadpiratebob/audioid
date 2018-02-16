<?php

if (!isset($page) || !file_exists('php/content/' . $page . '.php'))
  $page = '';

if (!isset($cmd)  && array_key_exists('cmd', $_POST));
  $cmd = $_POST['cmd'];

if (isset($cmd))
{
  $cmd_fn = 'php/commands/' . (strlen($page) == 0 ? 'home' : $page) . '/' . $cmd . '.php';
  if (!file_exists($cmd_fn))
  {
    unset($cmd);
    unset($cmd_fn);
  }
}

include_once('php/utils/init_db_vars.php');

$topnav_sayings = array
                  (
                    'do stuff',       'hear here',      'now playing music!', 'O.o',       'splash text here!',              'LISTEN',
                    'do things',      'hear here',      'now with music!',    'C.C',       'hey look - splash text',         '<a target="tab" class="a_topnav" href="http://www.badgerbadgerbadger.com/">LISTEN</a>',
                    'do stuff',       'hear here',      'with music.',        'o.O',       '&ltsplash text&gt',              '<a target="tab" class="a_topnav" href="https://www.youtube.com/watch?v=wCDIYvFmgW8">LISTEN</a>',
                    'do something',   'hear here',      'now with music',     'BD',        '&lt;random splash&gt;',          '<a target="tab" class="a_topnav" href="https://www.youtube.com/watch?v=K2cYWfq--Nw">LISTEN</a>',
                    'do stuff',       'bear here',      'music?',             'o.O',       '&lt;random splash /&gt;',        '<a target="tab" class="a_topnav" href="https://www.youtube.com/watch?v=7MzhpZ5tVQU">LISTEN</a>',
                    'does stuff',     'hear there',     'music get',          'XD',        'playing music',                  '<a target="tab" class="a_topnav" href="https://www.youtube.com/watch?v=dQw4w9WgXcQ">LISTEN</a>',
                    'do stuff',       'hear here',      'now playing',        'D8',        'music sold separately',          '<a target="tab" class="a_topnav" href="https://www.youtube.com/watch?v=b93-qaYLsC8">LISTEN</a>',
                    'do stuff',       'hear here',      'has text here.',     '@.@',       '&lt;random sploosh&gt;',         '<a target="tab" class="a_topnav" href="https://www.youtube.com/watch?v=FavUpD_IjVY">LISTEN</a>',
                    'make stuff',     'hear here',      'now with music!',    'O.o',       '&lt;random splash text&gt;',     '<a target="tab" class="a_topnav" href="https://www.youtube.com/watch?v=FP-1WVDT4L8">LISTEN</a>',
                    'make something', 'hear music',     'now with music!',    '^.^',       '&lt;random splash text&gt;',     '<a target="tab" class="a_topnav" href="https://www.youtube.com/watch?v=hMeHFsEK8n0">LISTEN</a>',
                    'do stuff',       'hear sounds',    'loud.',              'O.x',       'warning: may cause sound',       '<a target="tab" class="a_topnav" href="https://www.youtube.com/watch?v=F0odBpvBAYM">LISTEN</a>',
                    'do something',   'hear stuff',     'now with music!',    ':P',        'side effects may include music', '<a target="tab" class="a_topnav" href="https://www.youtube.com/watch?v=GYjY98wMWkE">LISTEN</a>',
                    '_do_ something', 'hear here',      'now playing',        '&lt;.&lt;', 'don\'t forget about reality.',   '<a target="tab" class="a_topnav" href="https://www.youtube.com/watch?v=tVqPx5mUj0g">LISTEN</a>',
                    'do stuff',       'now playing',    'loud?',              'd(o.o)b',   'side effects may include noise', '<a target="tab" class="a_topnav" href="https://www.youtube.com/watch?v=VznAYy5yL2A">LISTEN</a>',
                    'do stuff',       'hear something', 'music recommended',  '8D',        'headphones recommended',         '<a target="tab" class="a_topnav" href="https://www.youtube.com/watch?v=bG-bK8e0agQ">LISTEN</a>'
                  );
$topnav_index   = rand(0, count($topnav_sayings) - 1);
$topnav_txt     = $topnav_sayings[$topnav_index];

?>