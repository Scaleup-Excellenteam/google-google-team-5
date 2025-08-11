document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("searchInput");
  const resultsBox = document.getElementById("resultsBox");
  const loading = document.getElementById("loading");
  const button = document.getElementById("searchButton");

  function showLoading(show) {
    loading.style.display = show ? "block" : "none";
  }

  async function performSearch() {
    const query = input.value.trim();
    if (!query) {
      resultsBox.innerHTML = "";
      return;
    }

    // Loading
    button.disabled = true;
    const originalText = button.textContent;
    button.textContent = "Loading...";

    showLoading(true);
    try {
      const res = await fetch(`/search?q=${encodeURIComponent(query)}`);
      const data = await res.json();

      showLoading(false);

      if (data.length === 0) {
        resultsBox.innerHTML = "No results found.";
        return;
      }

      resultsBox.innerHTML = "";
      data.forEach(item => {
        const div = document.createElement("div");
        div.classList.add("result-item");
        div.innerHTML = `${item.completed_sentence} <div class="result-file">[File: ${item.file}, Line: ${item.line}, Score: ${item.score}]</div>`;
        resultsBox.appendChild(div);
      });
    } catch (e) {
      showLoading(false);
      resultsBox.innerHTML = "Error fetching results.";
    } finally {
      button.disabled = false;
      button.textContent = originalText;
    }
  }

  button.addEventListener("click", performSearch);

  // Enter for search
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      performSearch();
    }
  });

});
