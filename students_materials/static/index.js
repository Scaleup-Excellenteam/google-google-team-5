document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("searchInput");
  const resultsBox = document.getElementById("resultsBox");
  const loading = document.getElementById("loading");
  const button = document.getElementById("searchButton");

  function showLoading(show) {
    loading.style.display = show ? "block" : "none";
  }

  function performSearch() {
    const query = input.value.trim();
    if (!query) {
      resultsBox.innerHTML = "";
      return;
    }

    showLoading(true);
    fetch(`/search?q=${encodeURIComponent(query)}`)
      .then(res => res.json())
      .then(data => {
        showLoading(false);
        if (data.length === 0) {
          resultsBox.innerHTML = "No results found.";
          return;
        }
        resultsBox.innerHTML = "";
        data.forEach(item => {
          const div = document.createElement("div");
          div.classList.add("result-item");
          div.innerHTML = `${item.original} <div class="result-file">[File: ${item.file}, Line: ${item.line}]</div>`;
          resultsBox.appendChild(div);
        });
      })
      .catch(() => {
        showLoading(false);
        resultsBox.innerHTML = "Error fetching results.";
      });
  }

  button.addEventListener("click", performSearch);

  // אם רוצים גם חיפוש אוטומטי אחרי הקלדה, אפשר להוסיף כאן debounce וכו.
});
