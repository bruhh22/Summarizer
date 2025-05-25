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
    const response = await fetch("https://summarizer-x8o5.onrender.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ url: youtubeLink })
    });

    if (!response.ok) {
      throw new Error("Failed to fetch summary.");
    }

    const data = await response.json();

    // Hide loading
    loading.classList.add("hidden");

    // Show result
    summaryText.textContent = data.summary || "No summary available.";
    resultContainer.classList.remove("hidden");

  } catch (error) {
    loading.classList.add("hidden");
    summaryText.textContent = "⚠️ Error: " + error.message;
    resultContainer.classList.remove("hidden");
  }
});
