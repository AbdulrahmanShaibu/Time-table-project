/* ===========================================================
   Timetable Editor — Interactive Drag & Drop / Click Swap
   Used in admin_generate.html and editor.html
   =========================================================== */

document.addEventListener("DOMContentLoaded", () => {
  console.log("Timetable editor loaded.");

  const grid = document.querySelector(".timetable-grid");
  if (!grid) return;

  let selectedCell = null;

  // Allow selecting two cells to swap lessons
  grid.addEventListener("click", (event) => {
    const cell = event.target.closest(".timetable-cell.editable");
    if (!cell) return;

    if (!selectedCell) {
      // first selection
      selectedCell = cell;
      cell.classList.add("selected");
    } else {
      // second selection — perform swap
      swapLessons(selectedCell, cell);
      selectedCell.classList.remove("selected");
      selectedCell = null;
    }
  });

  // Swap lessons visually and via backend
  async function swapLessons(cell1, cell2) {
    const lesson1 = cell1.dataset.lessonId;
    const lesson2 = cell2.dataset.lessonId;

    const endpoint = grid.dataset.swapEndpoint;
    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ lesson1, lesson2 }),
      });
      const data = await response.json();
      if (data.success) {
        const tempHTML = cell1.innerHTML;
        cell1.innerHTML = cell2.innerHTML;
        cell2.innerHTML = tempHTML;
      } else {
        alert(data.message || "Swap failed due to conflict.");
      }
    } catch (err) {
      console.error(err);
      alert("Server error during swap.");
    }
  }

  // Save final timetable to server
  document.querySelector("#btn-save-timetable")?.addEventListener("click", async () => {
    const endpoint = grid.dataset.saveEndpoint;
    try {
      const response = await fetch(endpoint, { method: "POST" });
      const data = await response.json();
      if (data.success) alert("Timetable saved successfully!");
      else alert("Failed to save timetable.");
    } catch (err) {
      console.error(err);
    }
  });
});
