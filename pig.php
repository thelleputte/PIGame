<?php
header('Content-Type: text/event-stream');
header('Cache-Control: no-cache');
header("Connection: keep-alive");


// #############################################################################
// GLOBAL VARs SECTION 
// ############################################################################# 

$question = "";
$answer = "";
$player = "";

// fclose(STDIN);
// fclose(STDOUT);
// fclose(STDERR);
// $STDIN = fopen('/dev/null', 'r');
// $STDOUT = fopen('pig.log', 'wb');
// $STDERR = fopen('pig.err', 'wb');


// #############################################################################
// FUNCTIONS SECTION 
// ############################################################################# 


function sendMessage($id, $event, $data) {
    echo "id: $id" . PHP_EOL;
    echo "event: $event" . PHP_EOL;
    echo "data: $data" . PHP_EOL;
    echo PHP_EOL;
    ob_flush();
    flush();
}

function getQuestionJson() {
    error_log("check 1");
    $string = file_get_contents("pig.json");
    error_log("check 2");
    $json_a = json_decode($string, true);
    error_log("check 3");
    echo "". print_r($json_a, true);
    error_log("check 4");
    error_log ("". print_r($json_a, true));
    echo $json_a['id'];
    error_log("check 5");
    error_log ($json_a['id']);
    echo $json_a['question'];
    error_log("check 6");
    error_log ($json_a['question']);
    echo $json_a['answer'];
    error_log("check 7");
    error_log ($json_a['answer']);
    return array($json_a['id'],$json_a['question'],$json_a['answer']);
    error_log("check 8");
}

function getQuestion() {

    //by declaring var global, we then refer to the global var (not local to the function) 
    // no need to return any value(s) in this case
    //global $question, $answer;

    //The var containing the question IDs already used must be declared static 
    //so that we don't lose it's content from one function call to another.
    //Alternatively, we can decide the number of questions in advance and fetch all of them from start of play.
    //static qIdUsed = ...;

    $questionID = rand(1,10);

    switch ($questionID) {
        case 1:
        $question = "En quelle année fût détruit le bar pi ?";
        $answer = "2014?";
        break;
        case 2:
        $question = "Dans quelle village a eu lieu le camp pi 2001 ?";
        $answer = "Bhein justement, je ne sais plus.. Roumanie, près de Sibiu?";
        break;
        case 3:
        $question = "Quel est le code secret de la 16ème ?";
        $answer = "####";
        break;
        case 4:
        $question = "M'enfiiiin Benoît !";
        $answer = "TGC !";
        break;
        case 5:
        $question = "Yassu, Yassas.. ";
        $answer = "YASSU YASSAS !";
        break;
        case 6:
        $question = "Combien de chansons compte le répertoire des Enroules ?";
        $answer = "Au moins 283601847";
        break;
        case 7:
        $question = "Qui a dit: \\\"si tu continues je te jette ma pelle dans ton parebrise\\\" ?";
        $answer = "Thibault (mais l'autre)";
        break;
        case 8:
        $question = "Où se situe le \\\"Au Chez Victor\\\" ?";
        $answer = "Av. Albertine #1, Rixensart";
        break;
        case 9:
        $question = "Quel est le menu principal au \\\"Chez Victor\\\" ?";
        $answer = "Croque-Monsieur KETCHUP";
        break;
        case 10:
        $question = "Quel est le nom des 2 kits de diagnostic vendu par DNAlytics ?";
        $answer = "RheumaKit et ColonoKit";
        break;
        case 11:
        $question = "Quel est le nom du progiciel vendu par Sopra Banking Software ?";
        $answer = "Thaler";
        break;                      
        default:
        $question = "Ca, ça n'existe pas";
        $answer = "Jupiler NA()";

    }

    return array($question,$answer);
}


// #############################################################################
// MAIN SECTION 
// ############################################################################# 


echo "salut\n";

$lastId = $_SERVER["HTTP_LAST_EVENT_ID"];
if (isset($lastId) && !empty($lastId) && is_numeric($lastId)) {
    $lastId = intval($lastId);
    $lastId++;
}

//Ajax handling for buttons click
if (isset($_POST['action'])) {
    switch ($_POST['action']) {
        case 'startStop':
            //foo();
            break;
        case 'next':
            //bar();
            break;
    }
}


// SSE section
//while (true) {

    $lastId++;
    $time = date('r');
        //$data = "{$lastId}) The server time is: {$time}";

        //$question = getQuestion()[0];
        //$answer = getQuestion()[1];
    list($id, $question, $answer) = getQuestionJson();

    echo "id: $id\n";
    echo "event: question\n";
    //echo "data: $question\n\n";
    echo "data: {\"question\": \"$question\", \"answer\": \"$answer\"}\n\n";    
    ob_flush();
    flush();

    sleep(3);

    $player = rand(1,6);
        //sendMessage($lastId, "player", $data);
        //!not the same behavior as: 
    echo "id: $id\n";
    echo "event: player\n";
    echo "data: $player\n\n";
    //Using JSON format for multiple data values
    //echo "data: {\"player\": \"$player\", \"answer\": \"$answer\"}\n\n";
    ob_flush();
    flush();


        //if ($lastId > 3 ){
        //    echo "die";
        //    die();      
        //}   




//}


?>
