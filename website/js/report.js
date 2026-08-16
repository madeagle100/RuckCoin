(function () {
  var form = document.getElementById("report-form");
  var out = document.getElementById("report-out");
  var btn = document.getElementById("report-btn");
  if (!form || !out) return;

  function say(text, ok) {
    out.hidden = false;
    out.className = ok ? "note" : "note alert";
    out.textContent = text;
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var key = window.RUCK_REPORT_KEY || "";
    if (!key) {
      say("This box is on the site, but the inbox is not connected yet. Try again in a bit, or open an issue on the GitHub repo.");
      return;
    }
    var msg = (form.message.value || "").trim();
    if (msg.length < 8) {
      say("Write a little more so we can tell what broke.");
      return;
    }
    if (form.company && form.company.value) {
      say("Sent. Thanks.");
      return;
    }
    btn.disabled = true;
    var body = {
      access_key: key,
      subject: "RuckCoin report",
      from_name: (form.who.value || "").trim() || "site visitor",
      message: msg,
      page: (form.page.value || "").trim() || location.href
    };
    fetch("https://api.web3forms.com/submit", {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(body)
    })
      .then(function (r) { return r.json(); })
      .then(function (res) {
        if (res.success) {
          form.reset();
          say("Got it. If you left a way to reach you, we may write back. Do not send seed words or a wallet password.", true);
        } else {
          say(res.message || "Could not send. Try again later.");
        }
      })
      .catch(function () {
        say("Could not reach the inbox. Check your connection and try again.");
      })
      .then(function () {
        btn.disabled = false;
      });
  });
})();
