document.getElementById("linkForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const youtubeLink = document.getElementById("youtubeLink").value;
  const loading = document.getElementById("loading");
  const resultContainer = document.getElementById("resultContainer");
  const summaryText = document.getElementById("summaryText");

  // Reset previous output
  summaryText.textContent = '';
  resultContainer.classList.add("hidden");

  // Show loading
  loading.classList.remove("hidden");

  try {
    const response = await fetch("https://backend-461001.el.r.appspot.com", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ url: youtubeLink })
    });

    let data;
    try {
      data = await response.json();
    } catch {
      data = {};
    }

    // Hide loading
    loading.classList.add("hidden");
    
    if (!response.ok) {
      // Show a friendly error message for 500 errors
      if (response.status === 500) {
        summaryText.textContent = "⚠️ Sorry, this video cannot be downloaded. It may be unavailable or YouTube is blocking downloads. Try a different video or try again later.";
      } else if (data.error) {
        summaryText.textContent = "⚠️ Error: " + data.error;
      } else {
        summaryText.textContent = "⚠️ Error: Failed to fetch summary.";
      }
      resultContainer.classList.remove("hidden");
      return;
    }

    // Show result
    summaryText.textContent = data.summary || "No summary available.";
    resultContainer.classList.remove("hidden");

  } catch (error) {
    loading.classList.add("hidden");
    summaryText.textContent = "⚠️ Error: " + error.message;
    resultContainer.classList.remove("hidden");
  }
});
