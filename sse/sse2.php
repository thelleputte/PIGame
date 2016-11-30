<?php
header('Content-Type: text/event-stream');
header('Cache-Control: no-cache');
header("Connection: keep-alive");

$lastId = $_SERVER["HTTP_LAST_EVENT_ID"];
if (isset($lastId) && !empty($lastId) && is_numeric($lastId)) {
    $lastId = intval($lastId);
    $lastId++;
}

while (true) {

    $time = date('r');
    $lastId++;
    echo "data: {$lastId}) The server time is: {$time}\n\n";
    ob_flush();
    flush();
    sleep(1);

    if ($lastId > 3 ){
    echo "die";
    die();      
    }   

}


?>