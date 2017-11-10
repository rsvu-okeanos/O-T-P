<?php
	$url = "http://192.168.3.244/media/output/export_purchases.php?start_time=".$argv[1]."&end_time=".$argv[2];
    $contents = file_get_contents($url);

	echo preg_replace('/[\x00-\x1F\x80-\xFF]/', '', $decoded);

?>
