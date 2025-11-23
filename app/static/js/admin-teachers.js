/* admin-teachers.js — unified script for Manage Teachers page (modal, AJAX, search, pagination) */

document.addEventListener("DOMContentLoaded", () => {
    // Elements
    const openAddModalBtn = document.getElementById("openAddModal");
    const teacherModal = document.getElementById("teacherModal");
    const crudForm = document.getElementById("crud-form");
    const table = document.getElementById("teachersTable");
    const tableBody = document.getElementById("crud-table-body");
    const searchInput = document.getElementById("tableSearch");
    const prevBtn = document.getElementById("prevPage");
    const nextBtn = document.getElementById("nextPage");
    const pageInfo = document.getElementById("pageInfo");
    const rowsPerPageSelect = document.getElementById("rowsPerPage");
    const sidebarToggle = document.getElementById("sidebarToggle");
    const toastContainer = createToastContainer();

    // Pagination state
    let currentPage = 1;
    let rowsPerPage = parseInt(rowsPerPageSelect.value || 10);
    let filteredRows = Array.from(tableBody.querySelectorAll("tr"));

    // Open / close modal
    openAddModalBtn?.addEventListener("click", () => {
        openModal("teacherModal");
        // reset form fields (progressive)
        crudForm.reset();
    });

    function openModal(id) {
        const m = document.getElementById(id);
        if (!m) return;
        m.classList.add("active");
        m.setAttribute("aria-hidden", "false");
    }
    window.openModal = openModal;

    function closeModal(id) {
        const m = document.getElementById(id);
        if (!m) return;
        m.classList.remove("active");
        m.setAttribute("aria-hidden", "true");
    }
    window.closeModal = closeModal;

    // Toasts
    function createToastContainer() {
        let cont = document.querySelector(".toast-container");
        if (!cont) {
            cont = document.createElement("div");
            cont.className = "toast-container";
            document.body.appendChild(cont);
        }
        return cont;
    }

    function showToast(msg, kind = "info") {
        const el = document.createElement("div");
        el.className = `toast toast-${kind}`;
        el.innerText = msg;
        toastContainer.appendChild(el);
        setTimeout(() => { el.classList.add("fade-out"); setTimeout(() => el.remove(), 300); }, 2500);
    }

    // Sidebar toggle
    sidebarToggle?.addEventListener("click", () => {
        document.querySelector(".sidebar").classList.toggle("collapsed");
        document.querySelector(".main-content").classList.toggle("collapsed");
    });

    // Dark mode persists in localStorage
    const darkKey = "school_ui_dark";
    if (localStorage.getItem(darkKey) === "1") document.body.classList.add("dark-mode");
    window.toggleDarkMode = function () {
        document.body.classList.toggle("dark-mode");
        localStorage.setItem(darkKey, document.body.classList.contains("dark-mode") ? "1" : "0");
    };

    // --- AJAX form submit (progressive enhancement) ---
    if (crudForm) {
        crudForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const btn = crudForm.querySelector("button[type='submit']");
            const origText = btn.innerHTML;
            btn.disabled = true;
            btn.innerHTML = "Saving...";

            const fd = new FormData(crudForm);
            const endpoint = crudForm.dataset.endpoint || crudForm.action;
            const method = crudForm.dataset.method || crudForm.method || "POST";

            try {
                const resp = await fetch(endpoint, { method: method.toUpperCase(), body: fd });
                // If server returns HTML (normal POST), fallback to full reload.
                const contentType = resp.headers.get("content-type") || "";
                if (contentType.includes("application/json")) {
                    const data = await resp.json();
                    if (data.success) {
                        showToast("Saved successfully", "success");
                        closeModal("teacherModal");
                        setTimeout(() => location.reload(), 800);
                    } else {
                        showToast(data.message || "Failed to save", "error");
                    }
                } else {
                    // fallback: server returned HTML (regular form submit)
                    const txt = await resp.text();
                    // safe fallback: reload page so server-side flash appears
                    location.reload();
                }
            } catch (err) {
                console.error(err);
                showToast("Network or server error", "error");
            } finally {
                btn.disabled = false;
                btn.innerHTML = origText;
            }
        });
    }

    // --- Delete handler (delegated) ---
    tableBody.addEventListener("click", async (e) => {
        if (!e.target.classList.contains("btn-delete")) return;
        const btn = e.target;
        const id = btn.dataset.id;
        const endpointBase = btn.dataset.endpoint || (crudForm ? crudForm.dataset.endpoint : null);

        if (!id || !endpointBase) {
            showToast("Delete endpoint not configured", "error");
            return;
        }
        if (!confirm("Delete this teacher?")) return;

        try {
            btn.disabled = true;
            btn.innerText = "Deleting...";
            const resp = await fetch(`${endpointBase}/${id}`, { method: "DELETE" });
            const data = await resp.json();
            if (data.success) {
                showToast("Deleted", "success");
                btn.closest("tr").remove();
                // refresh filtered rows and UI
                filteredRows = Array.from(tableBody.querySelectorAll("tr"));
                renderPage();
            } else {
                showToast(data.message || "Deletion failed", "error");
            }
        } catch (err) {
            console.error(err);
            showToast("Network error", "error");
        } finally {
            btn.disabled = false;
            btn.innerText = "Delete";
        }
    });

    // --- Search (client-side) ---
    searchInput?.addEventListener("input", (e) => {
        const q = (e.target.value || "").trim().toLowerCase();
        filteredRows = Array.from(tableBody.querySelectorAll("tr")).filter(tr => {
            const name = tr.dataset.name || "";
            const email = tr.dataset.email || "";
            const edu = tr.dataset.edu || "";
            return name.includes(q) || email.includes(q) || edu.includes(q);
        });
        currentPage = 1;
        renderPage();
    });

    // --- Pagination ---
    rowsPerPageSelect?.addEventListener("change", (e) => {
        rowsPerPage = parseInt(e.target.value, 10) || 10;
        currentPage = 1;
        renderPage();
    });

    prevBtn?.addEventListener("click", () => {
        if (currentPage > 1) { currentPage--; renderPage(); }
    });
    nextBtn?.addEventListener("click", () => {
        const max = Math.ceil(filteredRows.length / rowsPerPage) || 1;
        if (currentPage < max) { currentPage++; renderPage(); }
    });

    function renderPage() {
        // hide all then show slice
        filteredRows.forEach(r => r.style.display = "none");
        const total = filteredRows.length;
        const maxPage = Math.max(1, Math.ceil(total / rowsPerPage));
        if (currentPage > maxPage) currentPage = maxPage;

        const start = (currentPage - 1) * rowsPerPage;
        const slice = filteredRows.slice(start, start + rowsPerPage);
        slice.forEach(r => r.style.display = "");
        pageInfo.innerText = `Page ${currentPage} / ${maxPage} (${total} rows)`;

        // disable/enable nav
        prevBtn.disabled = currentPage <= 1;
        nextBtn.disabled = currentPage >= maxPage;
    }

    // initial setup
    filteredRows = Array.from(tableBody.querySelectorAll("tr"));
    renderPage();
});
