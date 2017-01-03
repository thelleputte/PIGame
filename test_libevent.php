<?php
	function read_cb($buffer){
		echo event_buffer_read($buffer, 4096);
	}
	function write_cb($buffer){
		
	}
	function error_cb($buffer){
		echo "error";
	}
	
	/* Active le vidage implicite des buffers de sortie, pour que nous
	* puissions voir ce que nous lisons au fur et à mesure. */
	ob_implicit_flush();
	$address = '127.0.0.1';
	$port = 10000;
	if (($sock = socket_create(AF_INET, SOCK_STREAM, SOL_TCP)) === false) {
		echo "socket_create() a échoué : raison : " . socket_strerror(socket_last_error()) . "\n";
	}
	$result = socket_connect($sock, $address, $port);
	if ($sock === false) {//est ce sock ou result qu'il faut tester ?
		echo "socket_connect() a échoué : raison : ($result) " . socket_strerror(socket_last_error($socket)) . "\n";
	}
	
	
	$base = event_base_new();
	$eb = event_buffer_new($sock, "read_cb", "write_cb",  "error_cb", $base);
	event_buffer_base_set($eb,  $base);
	event_buffer_enable($eb,  EV_READ);
	event_base_loop($base);

?>