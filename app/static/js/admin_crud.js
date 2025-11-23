/* ===========================================================
   Admin CRUD Logic (Improved UI Feedback, Fetch API, UX updates)
   Author: Abdulrahman Shaibu Kheir
=========================================================== */

document.addEventListener("DOMContentLoaded", () => {
  console.log("Enhanced Admin CRUD script initialized.");

  const form = document.querySelector("form#crud-form");
  const tableBody = document.querySelector("tbody#crud-table-body");
  const toast = createToast(); // Create a toast notification container

  if (!form || !tableBody) return;

  // --- CREATE / UPDATE HANDLER ---
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const submitBtn = form.querySelector("button[type='submit']");
    const formData = new FormData(form);
    const endpoint = form.dataset.endpoint;
    const method = form.dataset.method || "POST";

    showLoading(submitBtn);

    try {
      const response = await fetch(endpoint, {
        method,
        body: formData,
      });

      const data = await response.json();

      if (data.success) {
        showToast("Saved successfully!", "success");
        if (data.redirect) {
          setTimeout(() => (window.location.href = data.redirect), 1500);
        } else {
          setTimeout(() => location.reload(), 1000);
        }
      } else {
        showToast(data.message || "Error occurred while saving.", "error");
      }
    } catch (error) {
      console.error(error);
      showToast("Network or Server error. Try again.", "error");
    } finally {
      hideLoading(submitBtn);
    }
  });

  // --- DELETE HANDLER ---
  // tableBody.addEventListener("click", async (e) => {
  //   if (!e.target.classList.contains("btn-delete")) return;

  //   const btn = e.target;
  //   if (!confirm("⚠️ Do you really want to delete this record?")) return;

  //   const id = btn.dataset.id;
  //   const endpoint = btn.dataset.endpoint;

  //   try {
  //     showInlineLoading(btn);
  //     const response = await fetch(`${endpoint}/${id}`, { method: "DELETE" });
  //     const data = await response.json();

  //     if (data.success) {
  //       showToast("Deleted successfully!", "success");
  //       btn.closest("tr").remove();
  //     } else {
  //       showToast("Deletion failed. Try again.", "error");
  //     }
  //   } catch (error) {
  //     console.error(error);
  //     showToast("Something went wrong. Check your network.", "error");
  //   } finally {
  //     hideInlineLoading(btn);
  //   }
  // });


  tableBody.addEventListener("click", async (e) => {
  if (!e.target.classList.contains("btn-delete")) return;

  const btn = e.target;
  if (!confirm("⚠️ Do you really want to delete this record?")) return;

  const endpoint = btn.dataset.endpoint;

  try {
    showInlineLoading(btn);
    const response = await fetch(endpoint, { method: "DELETE" });
    const data = await response.json();

    if (data.success) {
      showToast("Deleted successfully!", "success");
      btn.closest("tr").remove();
    } else {
      showToast("Deletion failed. Try again.", "error");
    }
  } catch (error) {
    console.error(error);
    showToast("Something went wrong. Check your network.", "error");
  } finally {
    hideInlineLoading(btn);
  }
});


  // --- Helper UI Functions ---
  function showToast(message, type = "info") {
    const toastItem = document.createElement("div");
    toastItem.className = `toast toast-${type}`;
    toastItem.textContent = message;
    toast.appendChild(toastItem);

    setTimeout(() => {
      toastItem.classList.add("fade-out");
      setTimeout(() => toastItem.remove(), 300);
    }, 2500);
  }

  function createToast() {
    const container = document.createElement("div");
    container.className = "toast-container";
    document.body.appendChild(container);
    return container;
  }

  function showLoading(button) {
    button.disabled = true;
    button.dataset.originalText = button.innerHTML;
    button.innerHTML = "Processing...";
  }

  function hideLoading(button) {
    button.disabled = false;
    button.innerHTML = button.dataset.originalText;
  }

  function showInlineLoading(button) {
    button.dataset.originalText = button.innerHTML;
    button.innerHTML = "Deleting...";
    button.disabled = true;
  }

  function hideInlineLoading(button) {
    button.innerHTML = button.dataset.originalText;
    button.disabled = false;
  }
});



// Sidebar Toggle
document.querySelector('.sidebar-toggle-btn')?.addEventListener('click', () => {
  document.querySelector('.sidebar').classList.toggle('collapsed');
  document.querySelector('.main-content').classList.toggle('collapsed');
});

// Dark Mode Toggle (optional button)
function toggleDarkMode() {
  document.body.classList.toggle('dark-mode');
}

// Tabs
document.querySelectorAll('.tabs .tab').forEach((tab, index) => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));

    tab.classList.add('active');
    document.querySelectorAll('.tab-content')[index].classList.add('active');
  });
});

// Modals
function openModal(id) {
  document.getElementById(id).classList.add('active');
}
function closeModal(id) {
  document.getElementById(id).classList.remove('active');
}