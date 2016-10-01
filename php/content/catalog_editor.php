        <script type="text/javascript" src="js/catalog.js"></script>
        <table>
          <tr>
            <th>
              name
            </th>
            <th>
              path
            </th>
            <th colspan="3">
              &nbsp;
            </th>
          </tr>
          <tr>
            <form id="add_catalog_frm" method="POST" action="catalog_editor.php">
              <td>
                <input type="hidden" name="cmd" value="add" />
                <input type="text" id="new_catalog_name" name="name" value="new catalog" onfocus="clear_txt(document.getElementById('new_catalog_name'), 'new catalog');" onblur="add_txt(document.getElementById('new_catalog_name'), 'new catalog');" size="40" maxlenth="128" />
              </td>
              <td>
                <input type="text" id="new_catalog_path" name="path" value="/" onfocus="clear_txt(document.getElementById('new_catalog_path'), '/');" onblur="add_txt(document.getElementById('new_catalog_path'), '/');" size="40" maxlenth="256" />
              </td>
              <td colspan="3">
                <button type="submit">add it</button>
              </td>
            </form>
          </tr>
          <tr>
            <td colspan="5" class="separator">
              &nbsp;
            </td>
          </tr>
<?php // >

$query        = 'SELECT id, name, base_path FROM catalogs;';
$sql_catalogs = $sql_link->query($query);
if ($sql_catalogs === false)
  die('query "' . $query . '" died:<br />' . mysql_error());

$num_catalogs = $sql_catalogs->num_rows;

for ($i = 0; $i < $num_catalogs; ++$i)
{
  $catalog = $sql_catalogs->fetch_array(MYSQL_ASSOC);
  
?>
          <tr>
            <form id="catalog_<?=$i?>_frm" method="POST" onsubmit="var r = catalog_on_submit(<?=$i?>); if (r === false) return false;" action="catalog_editor.php">
              <td>
                <input type="hidden" name="cat_id"  id="catalog_id_<?=$i?>" value="<?=$catalog['id']?>" />
                <input type="hidden" name="cmd" id="cat_<?=$i?>_cmd" value="update" />
                <input type="text" id="catalog_name_<?=$i?>" name="name" value="<?=$catalog['name']?>" size="40" maxlenth="128" />
              </td>
              <td>
                <input type="text" id="catalog_path_<?=$i?>" name="path" value="<?=$catalog['base_path']?>" size="40" maxlenth="256" />
              </td>
              <td>
                <button type="button" onclick="load_scan_data(<?=$i?>);">scan</button>
              </td>
              <td>
                <button type="submit">update</button>
              </td>
              <td>
                <button type="button" onclick="document.getElementById('cat_<?=$i?>_cmd').value='delete'; document.getElementById('catalog_<?=$i?>_frm').submit();">delete</button>
              </td>
            </form>
          </tr>
<?php
}
?>
        </table>
        
        <div id="scan_steps"></div>
        <div id="scan_feedback"></div>