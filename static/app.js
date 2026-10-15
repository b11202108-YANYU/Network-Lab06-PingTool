const form = document.querySelector("#ping-form");
const button = document.querySelector("#submit-button");
const buttonLabel = document.querySelector("#button-label");
const resultPanel = document.querySelector("#result");
const errorPanel = document.querySelector("#error");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  resultPanel.hidden = true;
  errorPanel.hidden = true;
  button.disabled = true;
  buttonLabel.textContent = "測試中…";

  try {
    const response = await fetch("/api/ping", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        host: document.querySelector("#host").value.trim(),
        count: Number(document.querySelector("#count").value),
      }),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Ping 請求失敗。");
    }

    document.querySelector("#result-target").textContent =
      `${data.host} · ${data.count} 次測試`;
    document.querySelector("#rtt").textContent =
      data.rtt_avg_ms === null ? "無回應" : `${data.rtt_avg_ms} ms`;
    document.querySelector("#loss").textContent =
      data.loss_percent === null ? "未知" : `${data.loss_percent}%`;

    const status = document.querySelector("#status");
    status.textContent = data.success ? "連線成功" : "連線失敗";
    status.className = `status ${data.success ? "ok" : "fail"}`;
    resultPanel.hidden = false;
  } catch (error) {
    errorPanel.textContent = error.message || "無法連線至伺服器。";
    errorPanel.hidden = false;
  } finally {
    button.disabled = false;
    buttonLabel.textContent = "開始 Ping";
  }
});
