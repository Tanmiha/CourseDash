const API_URL = "http://localhost:5000/api/courses";

      const STATUS_CLASS = {
        "Not Started": "not-started",
        "In Progress": "in-progress",
        "Completed": "completed",
      };

      // ---- State ----
      let courses = [];
      let loading = false;

      // ---- DOM refs ----
      const listEl = document.getElementById("course-list");
      const countBadge = document.getElementById("count-badge");
      const refreshBtn = document.getElementById("refresh-btn");
      const form = document.getElementById("course-form");
      const resetBtn = document.getElementById("reset-btn");
      const submitBtn = document.getElementById("submit-btn");

      const modal = document.getElementById("edit-modal");
      const modalClose = document.getElementById("modal-close");
      const editCancel = document.getElementById("edit-cancel");
      const editForm = document.getElementById("edit-form");
      const editSave = document.getElementById("edit-save");

      // ---- Toasts ----
      const toastContainer = document.getElementById("toast-container");
      function toast(message, type = "success", duration = 3500) {
        const el = document.createElement("div");
        el.className = `toast ${type}`;
        el.textContent = message;
        toastContainer.appendChild(el);
        setTimeout(() => {
          el.classList.add("fade-out");
          el.addEventListener("animationend", () => el.remove());
        }, duration);
      }

      // ---- API helpers ----
      async function apiFetch(path, options = {}) {
        const res = await fetch(`${API_URL}${path}`, {
          headers: { "Content-Type": "application/json" },
          ...options,
        });
        let data = null;
        const text = await res.text();
        if (text) {
          try { data = JSON.parse(text); } catch { data = text; }
        }
        if (!res.ok) {
          const msg = (data && (data.message || data.error)) || `Request failed (${res.status})`;
          throw new Error(msg);
        }
        return data;
      }

      // ---- Rendering ----
      function render() {
        if (loading) {
          listEl.innerHTML = `
            <div class="state-box">
              <div class="spinner"></div>
              <p>Loading courses…</p>
            </div>`;
          countBadge.textContent = "";
          return;
        }

        if (!courses.length) {
          listEl.innerHTML = `
            <div class="state-box">
              <div class="empty-illustration">📚</div>
              <p>No courses yet. Add your first course using the form above.</p>
            </div>`;
          countBadge.textContent = "";
          return;
        }

        countBadge.innerHTML = `<strong>${courses.length}</strong> course${courses.length === 1 ? "" : "s"}`;

        listEl.innerHTML = `<div class="course-grid">${courses.map(cardHtml).join("")}</div>`;

        listEl.querySelectorAll("[data-edit]").forEach((b) =>
          b.addEventListener("click", () => openEdit(b.dataset.edit))
        );
        listEl.querySelectorAll("[data-delete]").forEach((b) =>
          b.addEventListener("click", () => removeCourse(b.dataset.delete, b.dataset.name))
        );
      }

      function escapeHtml(str) {
        return String(str ?? "").replace(/[&<>"']/g, (c) => ({
          "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
        }[c]));
      }

      function formatDate(value) {
        if (!value) return "—";
        const d = new Date(value);
        if (isNaN(d.getTime())) return escapeHtml(value);
        return d.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
      }

      function statusClass(status) {
        return STATUS_CLASS[status] || "not-started";
      }

      function cardHtml(c) {
        const cls = statusClass(c.status);
        const label = c.status || "Not Started";
        return `
          <article class="course-card">
            <div class="card-top">
              <h3>${escapeHtml(c.name)}</h3>
              <span class="badge ${cls}">${escapeHtml(label)}</span>
            </div>
            <p class="desc">${escapeHtml(c.description)}</p>
            <div class="course-meta">
              <span>🎯 ${formatDate(c.target_date)}</span>
              <span>🕒 Added ${formatDate(c.created_at)}</span>
            </div>
            <div class="card-actions">
              <button class="btn btn-sm btn-ghost" data-edit="${c.id}">Edit</button>
              <button class="btn btn-sm btn-danger" data-delete="${c.id}" data-name="${escapeHtml(c.name)}">Remove</button>
            </div>
          </article>`;
      }

      // ---- Validation ----
      function validateForm(formEl) {
        let ok = true;
        const required = ["name", "description", "target_date", "status"];
        required.forEach((name) => {
          const field = formEl.querySelector(`[name="${name}"]`).closest(".field");
          const value = formEl.querySelector(`[name="${name}"]`).value.trim();
          if (!value) {
            field.classList.add("invalid");
            ok = false;
          } else {
            field.classList.remove("invalid");
          }
        });
        return ok;
      }

      function clearErrors(formEl) {
        formEl.querySelectorAll(".field.invalid").forEach((f) => f.classList.remove("invalid"));
      }

      function getFormData(formEl) {
        const data = new FormData(formEl);
        const obj = {};
        data.forEach((v, k) => { obj[k] = v.trim(); });
        return obj;
      }

      // ---- CRUD ----
      async function loadCourses() {
        loading = true;
        render();
        try {
          const data = await apiFetch("");
          courses = Array.isArray(data) ? data : (data.courses || data.data || []);
          toast("Courses loaded.", "success", 2000);
        } catch (err) {
          toast(`Failed to load courses: ${err.message}`, "error", 5000);
          courses = [];
        } finally {
          loading = false;
          render();
        }
      }

      async function createCourse(payload) {
        submitBtn.disabled = true;
        submitBtn.textContent = "Saving…";
        try {
          const created = await apiFetch("", {
            method: "POST",
            body: JSON.stringify(payload),
          });
          courses.push(created);
          render();
          toast("Course added successfully!", "success");
          form.reset();
        } catch (err) {
          toast(`Could not add course: ${err.message}`, "error", 5000);
        } finally {
          submitBtn.disabled = false;
          submitBtn.textContent = "Add Course";
        }
      }

      async function updateCourse(id, payload) {
        editSave.disabled = true;
        editSave.textContent = "Saving…";
        try {
          const updated = await apiFetch(`/${id}`, {
            method: "PUT",
            body: JSON.stringify(payload),
          });
          const idx = courses.findIndex((c) => String(c.id) === String(id));
          if (idx !== -1) courses[idx] = updated || { ...courses[idx], ...payload };
          render();
          closeEdit();
          toast("Course updated successfully!", "success");
        } catch (err) {
          toast(`Could not update course: ${err.message}`, "error", 5000);
        } finally {
          editSave.disabled = false;
          editSave.textContent = "Save Changes";
        }
      }

      async function removeCourse(id, name) {
        if (!confirm(`Remove "${name}"? This cannot be undone.`)) return;
        const card = listEl.querySelector(`[data-delete="${id}"]`).closest(".course-card");
        if (card) card.style.opacity = "0.5";
        try {
          await apiFetch(`/${id}`, { method: "DELETE" });
          courses = courses.filter((c) => String(c.id) !== String(id));
          render();
          toast("Course removed.", "success");
        } catch (err) {
          toast(`Could not remove course: ${err.message}`, "error", 5000);
          if (card) card.style.opacity = "1";
        }
      }

      // ---- Modal ----
      function openEdit(id) {
        const course = courses.find((c) => String(c.id) === String(id));
        if (!course) return;
        clearErrors(editForm);
        document.getElementById("e-id").value = course.id;
        document.getElementById("e-name").value = course.name || "";
        document.getElementById("e-description").value = course.description || "";
        document.getElementById("e-target_date").value = (course.target_date || "").slice(0, 10);
        document.getElementById("e-status").value = course.status || "Not Started";
        modal.classList.add("open");
        document.getElementById("e-name").focus();
      }

      function closeEdit() {
        modal.classList.remove("open");
      }

      // ---- Events ----
      form.addEventListener("submit", (e) => {
        e.preventDefault();
        clearErrors(form);
        if (!validateForm(form)) {
          toast("Please fill in all required fields.", "error");
          return;
        }
        createCourse(getFormData(form));
      });

      resetBtn.addEventListener("click", () => {
        form.reset();
        clearErrors(form);
      });

      editForm.addEventListener("submit", (e) => {
        e.preventDefault();
        clearErrors(editForm);
        if (!validateForm(editForm)) {
          toast("Please fill in all required fields.", "error");
          return;
        }
        const payload = getFormData(editForm);
        const id = document.getElementById("e-id").value;
        updateCourse(id, payload);
      });

      modalClose.addEventListener("click", closeEdit);
      editCancel.addEventListener("click", closeEdit);
      modal.addEventListener("click", (e) => { if (e.target === modal) closeEdit(); });
      document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeEdit(); });

      refreshBtn.addEventListener("click", loadCourses);

      // ---- Init ----
      loadCourses();