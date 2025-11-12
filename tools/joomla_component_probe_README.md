Joomla Components Probe
=======================

Small Python tool to recursively probe a Joomla `administrator/components` directory and report which URLs return meaningful content vs blank pages.

Requirements
------------
- Python 3.7+
- Install deps:

```powershell
python -m pip install -r tools\requirements.txt
```

Usage
-----

PowerShell example:

```powershell
python tools\joomla_component_probe.py --base-url "http://192.168.195.79/joomla/administrator/components/" --max-depth 2 --concurrency 8 --insecure --output results.json
```

Options:
- --base-url: (required) base URL to start crawling
- --max-depth: recursion depth (default 2)
- --concurrency: number of concurrent requests (default 8)
- --insecure: skip SSL cert verification
- --output: output JSON file (default joomla_probe_results.json)

What it does
------------
- Fetches pages from the base path
- Marks pages as "blank" when the content is very small and doesn't contain alphanumeric characters
- Extracts local links (same path prefix) and recurses up to depth
- Saves a JSON report and prints a short summary to console

Next steps
----------
- If an endpoint returns OK and non-blank, you can try targeted upload tests (the tool does not perform uploads).
- If you want deeper parsing or custom filters (e.g., only .php endpoints), open a PR or edit `tools/joomla_component_probe.py`.

License
-------
MIT - for your personal lab use only.
