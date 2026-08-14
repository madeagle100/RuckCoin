(function () {
  var state = null;

  function $(id) { return document.getElementById(id); }
  function toast(msg, bad) {
    var el = $("toast");
    el.textContent = msg;
    el.className = "toast on" + (bad ? " bad" : "");
    setTimeout(function () { el.className = "toast"; }, 4200);
  }
  function money(n) {
    var x = Number(n || 0);
    return x.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 8 }) + " RUCK";
  }
  function show(name) {
    document.querySelectorAll(".panel").forEach(function (p) { p.classList.toggle("on", p.id === name); });
    document.querySelectorAll(".nav [data-go]").forEach(function (b) {
      b.setAttribute("aria-current", b.getAttribute("data-go") === name ? "true" : "false");
    });
  }
  function setAddr(id, addr) {
    var el = $(id);
    if (el) el.textContent = addr || "—";
  }
  function copyText(id) {
    var t = $(id) && $(id).textContent;
    if (!t || t === "—" || t === "…") return toast("Nothing to copy yet.", true);
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(t).then(function () { toast("Address copied."); }).catch(function () { toast("Copy failed. Select the address and copy it yourself.", true); });
    } else {
      toast("Select the address and press Ctrl+C.", true);
    }
  }
  function kind(tx) {
    if (tx.generated) return "Mined (new coins)";
    if (tx.category === "send") return "You sent";
    if (tx.category === "receive") return "You received";
    if (tx.category === "immature") return "Mined, still waiting";
    if (tx.category === "orphan") return "Orphaned block";
    return tx.category || "Move";
  }
  function when(tx) {
    if (!tx.time) return "";
    try { return new Date(tx.time * 1000).toLocaleString(); } catch (e) { return ""; }
  }

  function paint(data) {
    state = data;
    $("no-node").hidden = true;
    $("home-ok").hidden = false;
    var net = data.network || {};
    var offline = net.active === false;
    var peers = net.connections || 0;
    if (offline) {
      $("tape").textContent = "Offline mode · height " + data.height + " · this computer only, no other peers";
      $("net-note").className = "note";
      $("net-copy").innerHTML = "<strong>Offline.</strong> This computer is not talking to other RuckCoin computers. You can still see your address and the last balance it knows. New incoming payments wait until you go back online.";
    } else {
      $("tape").textContent = "Local wallet · height " + data.height + " · " + peers + " other computer" + (peers === 1 ? "" : "s") + " connected";
      $("net-note").className = "note";
      $("net-copy").innerHTML = "<strong>Local only for this window.</strong> The wallet itself never uses a website. The node on this PC is allowed to talk to " + peers + " other RuckCoin computer" + (peers === 1 ? "" : "s") + ". Use Settings if you want that off too.";
    }
    setAddr("home-addr", data.address);
    setAddr("recv-addr", data.address);
    setAddr("mine-addr", data.address);
    $("bal").textContent = money(data.balance);
    $("imm").textContent = money(data.immature);
    $("hgt").textContent = String(data.height);
    var m = data.mining || {};
    $("diff").textContent = m.difficulty != null ? Number(m.difficulty).toPrecision(4) : "—";
    $("pool").textContent = m.pooledtx != null ? String(m.pooledtx) : "—";

    var tb = $("tx-body");
    tb.innerHTML = "";
    (data.txs || []).slice().reverse().forEach(function (tx) {
      var tr = document.createElement("tr");
      var id = (tx.txid || "").slice(0, 10);
      tr.innerHTML = "<td>" + when(tx) + "</td><td>" + kind(tx) + "</td><td>" + money(tx.amount) + "</td><td><code>" + id + (id ? "…" : "") + "</code></td>";
      tb.appendChild(tr);
    });
    if (!(data.txs || []).length) {
      tb.innerHTML = '<tr><td colspan="4" class="empty">Nothing yet. Receive some RUCK or mine a test block.</td></tr>';
    }

    var assets = data.assets || {};
    var names = Object.keys(assets);
    var box = $("asset-list");
    if (!names.length) {
      box.className = "empty";
      box.textContent = "No assets in this wallet yet.";
    } else {
      box.className = "";
      box.innerHTML = "<ul>" + names.map(function (n) {
        return "<li><code>" + n + "</code> — " + assets[n] + "</li>";
      }).join("") + "</ul>";
    }
    if (data.veterans_address) $("vets").value = data.veterans_address;
    var sendWarn = $("send-offline-warn");
    if (sendWarn) sendWarn.hidden = !offline;
  }

  function load() {
    return fetch("/api/overview").then(function (r) { return r.json(); }).then(function (data) {
      if (!data.ok) throw new Error(data.error || "Could not load wallet.");
      paint(data);
    }).catch(function (err) {
      $("no-node").hidden = false;
      $("home-ok").hidden = true;
      $("tape").textContent = "Waiting for the node on this computer.";
      toast(err.message || String(err), true);
    });
  }

  function post(url, obj) {
    return fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(obj || {})
    }).then(function (r) { return r.json(); });
  }

  document.querySelectorAll("[data-go]").forEach(function (el) {
    el.addEventListener("click", function () { show(el.getAttribute("data-go")); });
  });
  document.querySelectorAll("[data-copy]").forEach(function (el) {
    el.addEventListener("click", function () { copyText(el.getAttribute("data-copy")); });
  });
  $("retry").addEventListener("click", load);
  function setNet(offline) {
    post("/api/offline", { offline: offline }).then(function (res) {
      var box = $("offline-result");
      box.hidden = false;
      if (!res.ok) {
        box.className = "note warn";
        box.textContent = res.error;
        return toast(res.error, true);
      }
      box.className = "note";
      box.textContent = res.message;
      toast(offline ? "Offline." : "Other computers allowed.");
      load();
    });
  }
  $("go-offline").addEventListener("click", function () { setNet(true); });
  $("go-online").addEventListener("click", function () { setNet(false); });
  $("donate").addEventListener("change", function () {
    $("donate-extra").hidden = !$("donate").checked;
  });
  $("new-addr").addEventListener("click", function () {
    post("/api/new-address", { label: "My address" }).then(function (res) {
      if (!res.ok) return toast(res.error, true);
      toast("New address ready. Old ones still work.");
      load();
    });
  });
  $("send-form").addEventListener("submit", function (e) {
    e.preventDefault();
    var payload = {
      to: $("to").value.trim(),
      amount: $("amount").value,
      donate: $("donate").checked,
      donate_amount: $("donate-amt").value
    };
    post("/api/send", payload).then(function (res) {
      var box = $("send-result");
      box.hidden = false;
      if (!res.ok) {
        box.className = "note warn";
        box.textContent = res.error;
        return toast(res.error, true);
      }
      box.className = "note";
      box.textContent = "Sent. Payment id: " + res.txid;
      toast("Payment sent.");
      $("send-form").reset();
      $("donate-extra").hidden = true;
      load();
    });
  });
  $("look-form").addEventListener("submit", function (e) {
    e.preventDefault();
    var q = $("look-q").value.trim();
    var box = $("look-out");
    box.hidden = false;
    box.innerHTML = "<p class='empty'>Looking…</p>";
    fetch("/api/lookup?q=" + encodeURIComponent(q)).then(function (r) { return r.json(); }).then(function (res) {
      if (!res.ok) {
        box.innerHTML = "<div class='note warn'><p>" + (res.error || "Not found.") + "</p></div>";
        return;
      }
      if (res.kind === "block") {
        box.innerHTML = "<div class='plate'><div class='lab'>Block</div><div class='val'>" + res.height + "</div><div class='addr'>" + res.hash + "</div><p>" + (res.txcount || 0) + " payment(s) in this page.</p></div>";
        return;
      }
      if (res.kind === "address") {
        box.innerHTML = "<div class='plate'><div class='lab'>Address</div><div class='addr'>" + res.address + "</div><p>Can spend: <strong>" + money(res.balance) + "</strong></p><p>Ever received: " + money(res.received) + "</p></div>";
        return;
      }
      if (res.kind === "tx") {
        var outs = (res.vout || []).length;
        box.innerHTML = "<div class='plate'><div class='lab'>Payment</div><div class='addr'>" + res.txid + "</div><p>Confirmations: <strong>" + (res.confirmations || 0) + "</strong></p><p>Outputs: " + outs + "</p></div>";
      }
    }).catch(function (err) {
      box.innerHTML = "<div class='note warn'><p>" + (err.message || err) + "</p></div>";
    });
  });
  $("issue-form").addEventListener("submit", function (e) {
    e.preventDefault();
    var box = $("issue-result");
    box.hidden = false;
    box.className = "note";
    box.textContent = "Creating… this spends 500 RUCK.";
    post("/api/issue", { name: $("issue-name").value, qty: $("issue-qty").value }).then(function (res) {
      if (!res.ok) {
        box.className = "note warn";
        box.textContent = res.error;
        return toast(res.error, true);
      }
      box.className = "note";
      box.textContent = res.message + " Payment id: " + res.txid;
      toast("Asset created.");
      load();
    });
  });
  $("xfer-form").addEventListener("submit", function (e) {
    e.preventDefault();
    post("/api/transfer", {
      asset: $("asset-name").value.trim(),
      qty: $("asset-qty").value,
      to: $("asset-to").value.trim()
    }).then(function (res) {
      if (!res.ok) return toast(res.error, true);
      toast("Asset sent.");
      load();
    });
  });
  $("try-mine").addEventListener("click", function () {
    $("try-mine").disabled = true;
    $("mine-result").hidden = false;
    $("mine-result").className = "note";
    $("mine-result").textContent = "Trying… this can take a minute. You can leave this page open.";
    post("/api/mine", { tries: 200000 }).then(function (res) {
      $("try-mine").disabled = false;
      if (!res.ok) {
        $("mine-result").className = "note warn";
        $("mine-result").textContent = res.error;
        return;
      }
      if (res.found && res.blocks && res.blocks.length) {
        $("mine-result").textContent = "You found a block. The reward will show as “still waiting” until more blocks are added. Block: " + res.blocks[0];
        toast("Block found.");
      } else {
        $("mine-result").textContent = "No block this round. That is normal on a CPU. Mining is a lottery. Try again, or use a GPU miner later.";
      }
      load();
    }).catch(function (err) {
      $("try-mine").disabled = false;
      $("mine-result").className = "note warn";
      $("mine-result").textContent = err.message || String(err);
    });
  });
  $("conn-form").addEventListener("submit", function (e) {
    e.preventDefault();
    var body = {
      host: $("host").value.trim(),
      port: $("port").value,
      user: $("user").value.trim(),
      veterans_address: $("vets").value.trim()
    };
    var pw = $("password").value;
    if (pw) body.password = pw;
    post("/api/connect", body).then(function (res) {
      var box = $("conn-result");
      box.hidden = false;
      if (!res.ok) {
        box.className = "note warn";
        box.textContent = res.error;
        return toast(res.error, true);
      }
      box.className = "note";
      box.textContent = res.message + " Height " + res.height + ".";
      toast("Connected.");
      $("password").value = "";
      load();
    });
  });

  fetch("/api/settings").then(function (r) { return r.json(); }).then(function (s) {
    if (!s.ok) return;
    $("host").value = s.host || "127.0.0.1";
    $("port").value = s.port || 8866;
    $("user").value = s.user || "";
    $("vets").value = s.veterans_address || "";
  });
  load();
  setInterval(function () {
    if ($("home-ok") && !$("home-ok").hidden) load();
  }, 15000);
})();
