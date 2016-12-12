<?php
/* Crée un socket TCP/IP. */
header( 'Content-type: text/plain; charset=utf-8' );
header( 'Content-Encoding: none; ' ); //disable apache compressed
ob_end_flush();
ob_start();
$address = "127.0.0.1";
$service_port = 10000;

function sendMessage($id, $event, $data) {
    echo "id: $id" . PHP_EOL;
    echo "event: $event" . PHP_EOL;
    echo "data: $data" . PHP_EOL;
    echo PHP_EOL;
    ob_flush();
    flush();
}


$socket = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
if ($socket === false) {
    echo "socket_create() a échoué : raison :  " . socket_strerror(socket_last_error()) . "\n";
} else {
    echo "OK.\n";
}

echo "Essai de connexion à ".$address." sur le port ".$service_port." ..." .PHP_EOL;
$result = socket_connect($socket, $address, $service_port);
error_log("result = ".$result);
if ($socket === false || $result="" || !$result) {
    echo "socket_connect() a échoué : raison : ($result) " . socket_strerror(socket_last_error($socket)) . "\n";
	$socket = null;
} else {
	echo $socket . " ";
    echo "OK.".PHP_EOL;
}

$in = "HEAD / HTTP/1.0\r\n\r\n";
$in .= "Host: www.example.com\r\n";
$in .= "Connection: Close\r\n\r\n";
$out = '';

echo "Envoi de la requête HTTP HEAD...".PHP_EOL;
socket_write($socket, $in, strlen($in));
echo "OK.\n";

/* Prépare le tableau read (socket surveillées en lecture) */
$read   = array($socket);
$write  = null;//array($socket);
$except = array($socket);
//socket_set_nonblock($socket);
//while (True){	
$num_changed_sockets = socket_select($read, $write, $except, 5);
echo "Number of changed sockets: " . $num_change_sockets . PHP_EOL;
while ($num_changed_sockets){
	$timeout = 5;
	if ($num_changed_sockets === false) {
	  /* Gestion des erreurs */
	  error_log("errors we should break\n");
	  for ($i=0 ; $i<count($read) ; $i++){
		  echo socket_last_error($read($i));
		  flush();
		  ob_flush();
		  socket_close($read($i));
		  break;// un peu rude mais à tester
	  }
	} else if ($num_changed_sockets > 0) {
	  /* Au moins une des sockets a été modifiée */
	  error_log("socket has changed = ".$num_changed_sockets.' r w e = ['.count($read).' '.count($write).' '.count($except).']');
	  for ($i=0 ; $i<count($read) ; $i++){
		  error_log("i read= ".$i);
		  $data=socket_read($read[$i],1024);
		  error_log("data : " .$data."\n");
		  echo $data;
		  echo 'rand  '.rand(0,100).PHP_EOL;
		  
		  ob_flush();
		  flush();
	  }
	  for ($i=0 ; $i<count($write) ; $i++){
		  error_log("i_write = ".$i);
		  //$data=socket_read($read[$i],1024);
		  //error_log($data."\n");
		  //echo $data;
		  flush();
		  ob_flush();
	  }
	  for ($i=0 ; $i<count($except) ; $i++){
		  error_log("i except= ".$i);
		  //$data=socket_read($read[$i],1024);
		  //error_log($data."\n");
		  //echo $data;
		  flush();
		  ob_flush();
	  }
	$read   = array($socket);
	$write  = null;//array($socket);
	$except = array($socket);
	$num_changed_sockets = socket_select($read, $write, $except,(int) $timeout);
	}
	
}
/* socket_set_nonblock($socket);
//stream_set_timeout($socket,3);
echo "Lire la réponse : \n\n";
sleep(3);
while ($out = socket_read($socket, 2048)) {
    if ($out =='' or $out == False){
		echo 'out empty\n';
		break;
	} 
	echo $out;
	flush();
	sleep(3);
} */

echo "Fermeture du socket...";
socket_close($socket);
echo "OK.\n\n";
?>
