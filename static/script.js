const $ = (id) => document.getElementById(id);
const btn = $("check");

async function checkSentence() {
  const sentence = $("sentence").value.trim();
  $("error").hidden = true;
  if (!sentence) { showError("Please type a sentence first."); return; }

  btn.disabled = true;
  btn.textContent = "Thinking…";
  try {
    const res = await fetch("/check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sentence }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Something went wrong.");
    render(data);
  } catch (e) {
    $("result").hidden = true;
    showError(e.message);
  } finally {
    btn.disabled = false;
    btn.textContent = "Check Sentence";
  }
}

function render(d) {
  const status = $("status");
  status.className = "status " + (d.is_correct ? "ok" : "bad");
  status.textContent = d.is_correct ? "✅ Your sentence is correct!" : "❌ Your sentence needs correction.";
  $("corrected").textContent = d.corrected;
  $("explanation").textContent = d.explanation;
  $("better").textContent = d.better;
  $("example").textContent = d.example;
  $("better-block").hidden = !d.better;
  $("result").hidden = false;
}

function showError(msg) { $("error").textContent = msg; $("error").hidden = false; }

btn.addEventListener("click", checkSentence);
$("sentence").addEventListener("keydown", (e) => {
  if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) checkSentence();
});
