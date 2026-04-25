// SVG icons used in the table action buttons
const SVG_EDIT = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>`;
const SVG_DEL  = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4h6v2"/></svg>`;

// ── State ──────────────────────────────────────────────────────────────────
let chartInstance = null;

// ── DOM refs ───────────────────────────────────────────────────────────────
const form          = document.getElementById("expenseForm");
const editIdInput   = document.getElementById("editId");
const titleInput    = document.getElementById("title");
const amountInput   = document.getElementById("amount");
const dateInput     = document.getElementById("date");
const categoryInput = document.getElementById("category");
const submitBtn     = document.getElementById("submitBtn");
const cancelBtn     = document.getElementById("cancelEdit");
const formTitle     = document.getElementById("formTitle");
const tableBody     = document.getElementById("expenseTableBody");
const emptyMsg      = document.getElementById("emptyMsg");
const searchInput   = document.getElementById("searchInput");
const filterCat     = document.getElementById("filterCategory");
const sortBy        = document.getElementById("sortBy");
const sortOrder     = document.getElementById("sortOrder");

// ── Init ───────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  dateInput.value = new Date().toISOString().split("T")[0];
  loadExpenses();
  loadStats();

  document.getElementById("navToggle").addEventListener("click", () => {
    document.getElementById("navLinks").classList.toggle("open");
  });
});

// ── Toast ──────────────────────────────────────────────────────────────────
function showToast(msg, type = "success") {
  const toast = document.getElementById("toast");
  toast.textContent = msg;
  toast.className = `toast ${type} show`;
  setTimeout(() => { toast.className = "toast"; }, 3000);
}

// ── Validation ─────────────────────────────────────────────────────────────
function validate() {
  let ok = true;
  document.querySelectorAll(".err").forEach(e => e.textContent = "");

  if (!titleInput.value.trim()) {
    document.getElementById("titleErr").textContent = "Title is required.";
    ok = false;
  }
  const amt = parseFloat(amountInput.value);
  if (!amountInput.value || isNaN(amt) || amt <= 0) {
    document.getElementById("amountErr").textContent = "Enter a valid positive amount.";
    ok = false;
  }
  if (!categoryInput.value) {
    document.getElementById("categoryErr").textContent = "Please select a category.";
    ok = false;
  }
  return ok;
}

// ── Load Expenses ──────────────────────────────────────────────────────────
async function loadExpenses() {
  const params = new URLSearchParams({
    search:   searchInput.value.trim(),
    category: filterCat.value,
    sort_by:  sortBy.value,
    order:    sortOrder.value
  });
  try {
    const res  = await fetch(`/api/expenses?${params}`);
    const data = await res.json();
    renderTable(data);
  } catch {
    showToast("Failed to load expenses.", "error");
  }
}

// ── Render Table ───────────────────────────────────────────────────────────
function renderTable(expenses) {
  tableBody.innerHTML = "";

  if (!expenses.length) {
    emptyMsg.style.display = "block";
    return;
  }
  emptyMsg.style.display = "none";

  expenses.forEach(exp => {
    const tr = document.createElement("tr");
    tr.innerHTML =
      "<td>" + escHtml(exp.title) + "</td>" +
      "<td><span class='badge'>" + exp.category + "</span></td>" +
      "<td>" + formatDate(exp.date) + "</td>" +
      "<td><strong>Rs." + parseFloat(exp.amount).toFixed(2) + "</strong></td>" +
      "<td class='actions-cell'>" +
        "<button class='btn btn-sm btn-edit' onclick='startEdit(" + exp.id + ")'>" + SVG_EDIT + " Edit</button>" +
        "<button class='btn btn-sm btn-delete' onclick='deleteExpense(" + exp.id + ")'>" + SVG_DEL + " Delete</button>" +
      "</td>";
    tableBody.appendChild(tr);
  });
}

// ── Load Stats ─────────────────────────────────────────────────────────────
async function loadStats() {
  try {
    const res  = await fetch("/api/stats");
    const data = await res.json();
    document.getElementById("totalSpent").textContent   = "Rs." + data.total.toFixed(2);
    document.getElementById("monthlySpent").textContent = "Rs." + data.monthly.toFixed(2);
    document.getElementById("txnCount").textContent     = data.count;
    renderChart(data.by_category);
  } catch {
    // silently fail
  }
}

// ── Chart ──────────────────────────────────────────────────────────────────
function renderChart(byCategory) {
  const ctx    = document.getElementById("categoryChart").getContext("2d");
  const labels = byCategory.map(c => c.category);
  const values = byCategory.map(c => parseFloat(c.total));
  const colors = ["#0d0d0d", "#333", "#555", "#777", "#999", "#bbb"];

  if (chartInstance) chartInstance.destroy();

  chartInstance = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: colors.slice(0, labels.length),
        borderWidth: 2,
        borderColor: "#fff"
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: "bottom", labels: { font: { size: 12 } } }
      }
    }
  });
}

// ── Add / Edit Submit ──────────────────────────────────────────────────────
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  if (!validate()) return;

  const id      = editIdInput.value;
  const payload = {
    title:    titleInput.value.trim(),
    amount:   parseFloat(amountInput.value),
    category: categoryInput.value,
    date:     dateInput.value
  };

  const url    = id ? "/api/expenses/" + id : "/api/expenses";
  const method = id ? "PUT" : "POST";

  try {
    const res = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const err = await res.json();
      showToast(err.error || "Something went wrong.", "error");
      return;
    }

    showToast(id ? "Expense updated!" : "Expense added!");
    resetForm();
    loadExpenses();
    loadStats();
  } catch {
    showToast("Network error.", "error");
  }
});

// ── Start Edit ─────────────────────────────────────────────────────────────
async function startEdit(id) {
  try {
    const res  = await fetch("/api/expenses/" + id);
    const data = await res.json();

    editIdInput.value   = data.id;
    titleInput.value    = data.title;
    amountInput.value   = data.amount;
    categoryInput.value = data.category;
    dateInput.value     = data.date ? data.date.split("T")[0] : "";

    formTitle.textContent   = "Edit Expense";
    submitBtn.textContent   = "Update Expense";
    cancelBtn.style.display = "inline-block";

    document.getElementById("add-section").scrollIntoView({ behavior: "smooth" });
  } catch {
    showToast("Could not load expense.", "error");
  }
}

// ── Delete ─────────────────────────────────────────────────────────────────
async function deleteExpense(id) {
  if (!confirm("Delete this expense?")) return;
  try {
    const res = await fetch("/api/expenses/" + id, { method: "DELETE" });
    if (!res.ok) { showToast("Delete failed.", "error"); return; }
    showToast("Expense deleted.");
    loadExpenses();
    loadStats();
  } catch {
    showToast("Network error.", "error");
  }
}

// ── Reset Form ─────────────────────────────────────────────────────────────
function resetForm() {
  form.reset();
  editIdInput.value       = "";
  dateInput.value         = new Date().toISOString().split("T")[0];
  formTitle.textContent   = "Add Expense";
  submitBtn.textContent   = "Add Expense";
  cancelBtn.style.display = "none";
  document.querySelectorAll(".err").forEach(e => e.textContent = "");
}

cancelBtn.addEventListener("click", resetForm);

// ── Search / Filter / Sort listeners ──────────────────────────────────────
let searchTimer;
searchInput.addEventListener("input", () => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(loadExpenses, 350);
});
filterCat.addEventListener("change",  loadExpenses);
sortBy.addEventListener("change",     loadExpenses);
sortOrder.addEventListener("change",  loadExpenses);

// ── Helpers ────────────────────────────────────────────────────────────────
function escHtml(str) {
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function formatDate(dateStr) {
  if (!dateStr) return "-";
  const d = new Date(dateStr);
  return d.toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });
}
