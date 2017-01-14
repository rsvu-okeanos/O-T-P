<?php
	$url = "http://villa.okeanos.nl:2408/media/output/export_purchases.php?start_time=".$argv[1]."&end_time=".$argv[2];
    $contents = file_get_contents($url);

	$iv_size = mcrypt_get_iv_size(MCRYPT_RIJNDAEL_256, MCRYPT_MODE_CBC);
	$iv = substr($contents,0,$iv_size);
	$contents = substr($contents,$iv_size);
	$decoded = mcrypt_decrypt(MCRYPT_RIJNDAEL_256, "cecfdd6e7bdccbaf6dff1a4436510b85", $contents, MCRYPT_MODE_CBC, $iv);

	echo preg_replace('/[\x00-\x1F\x80-\xFF]/', '', $decoded);

?>
