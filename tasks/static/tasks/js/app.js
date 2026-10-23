
document.addEventListener("DOMContentLoaded", () => {
    const taskCards = Array.from(document.querySelectorAll("[data-task-card]"));
    const searchInput = document.getElementById("task-search");
    const filterButtons = document.querySelectorAll("[data-filter]");

    const totalCount = document.getElementById("total-count");
    const pendingCount = document.getElementById("pending-count");
    const completedCount = document.getElementById("completed-count");
    const visibleCount = document.getElementById("visible-count");

    const searchEmpty = document.getElementById("search-empty");
    const emptyState = document.getElementById("empty-state");
    const taskList = document.getElementById("task-list");

    let activeFilter = "all";

    function getStatusCounts() {
        const completed = taskCards.filter(
            card => card.dataset.status === "completed"
        ).length;

        return {
            total: taskCards.length,
            completed,
            pending: taskCards.length - completed
        };
    }

    function updateCounters() {
    const counts = getStatusCounts();

    if (totalCount) totalCount.textContent = counts.total;
    if (pendingCount) pendingCount.textContent = counts.pending;
    if (completedCount) completedCount.textContent = counts.completed;
    }

    function filterTasks() {
        const query = (searchInput?.value || "").trim().toLowerCase();
        let visible = 0;

        taskCards.forEach(card => {
            const text = card.dataset.search.toLowerCase();
            const matchesSearch = text.includes(query);
            const matchesFilter =
                activeFilter === "all" ||
                card.dataset.status === activeFilter;

            const shouldShow = matchesSearch && matchesFilter;

            card.hidden = !shouldShow;

            if (shouldShow) {
                visible++;
            }
        });

        if (visibleCount) {
        visibleCount.textContent =
        `Showing ${visible} of ${taskCards.length} tasks`;
        }

        if (searchEmpty) {
            searchEmpty.hidden = taskCards.length === 0 || visible > 0;
        }

        if (emptyState) {
            emptyState.hidden = taskCards.length !== 0;
        }

        if (taskList) {
            taskList.hidden = taskCards.length === 0;
        }

        updateCounters();
    }

    searchInput?.addEventListener("input", filterTasks);

    filterButtons.forEach(button => {
        button.addEventListener("click", () => {
            activeFilter = button.dataset.filter;

            filterButtons.forEach(item => {
                const isActive = item === button;
                item.classList.toggle("active", isActive);
                item.setAttribute("aria-pressed", String(isActive));
            });

            filterTasks();
        });
    });

    function showToast(message, type = "success") {
        let container = document.getElementById("toast-container");

        if (!container) {
            container = document.createElement("div");
            container.id = "toast-container";
            container.className = "toast-container";
            container.setAttribute("aria-live", "polite");
            container.setAttribute("aria-atomic", "false");
            document.body.appendChild(container);
        }

        const toast = document.createElement("div");
        toast.className = `toast toast-${type}`;

        const text = document.createElement("span");
        text.textContent = message;

        const close = document.createElement("button");
        close.type = "button";
        close.className = "toast-close";
        close.textContent = "×";
        close.setAttribute("aria-label", "Dismiss notification");
        close.addEventListener("click", () => toast.remove());

        toast.append(text, close);
        container.appendChild(toast);

        window.setTimeout(() => {
            toast.classList.add("toast-hiding");
            window.setTimeout(() => toast.remove(), 250);
        }, 3500);
    }

    document.querySelectorAll(".toggle-form").forEach(form => {
        form.addEventListener("submit", async event => {
            event.preventDefault();

            const card = form.closest("[data-task-card]");
            const button = form.querySelector(".completion-button");

            if (!card || !button || button.disabled) return;

            button.disabled = true;
            card.classList.add("is-saving");

            try {
                const response = await fetch(form.action, {
                    method: "POST",
                    headers: {
                        "X-Requested-With": "XMLHttpRequest",
                        "Accept": "application/json"
                    },
                    body: new FormData(form),
                    credentials: "same-origin"
                });

                const data = await response.json();

                if (!response.ok || !data.success) {
                    throw new Error(data.message || "Could not update task.");
                }

                card.dataset.status = data.is_completed
                    ? "completed"
                    : "pending";

                card.classList.toggle("is-completed", data.is_completed);

                button.textContent = data.is_completed ? "✓" : "";
                button.setAttribute(
                    "aria-label",
                    data.is_completed
                        ? `Mark ${data.title} as pending`
                        : `Mark ${data.title} as completed`
                );

                const badge = card.querySelector(".status-badge");
                if (badge) {
                    badge.textContent = data.is_completed
                        ? "Completed"
                        : "Pending";
                }

                showToast(data.message);
                filterTasks();
            } catch (error) {
                showToast(
                    error.message || "Something went wrong. Please try again.",
                    "error"
                );
            } finally {
                button.disabled = false;
                card.classList.remove("is-saving");
            }
        });
    });

    document.querySelectorAll(".delete-form").forEach(form => {
        form.addEventListener("submit", event => {
            if (!window.confirm("Are you sure you want to delete this task?")) {
                event.preventDefault();
            }
        });
    });

    filterTasks();
});
