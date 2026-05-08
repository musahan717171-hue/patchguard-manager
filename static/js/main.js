(function () {
    const root = document.documentElement;
    const savedTheme = localStorage.getItem("patchguard_theme") || "dark";
    root.setAttribute("data-theme", savedTheme);

    document.querySelectorAll("[data-theme-switcher]").forEach((select) => {
        select.value = savedTheme;
        select.addEventListener("change", () => {
            localStorage.setItem("patchguard_theme", select.value);
            root.setAttribute("data-theme", select.value);
            document.querySelectorAll("[data-theme-switcher]").forEach((other) => {
                other.value = select.value;
            });
        });
    });

    document.querySelectorAll("[data-language-switcher]").forEach((select) => {
        select.addEventListener("change", () => {
            const currentPath = window.location.pathname + window.location.search;
            const next = encodeURIComponent(currentPath);
            window.location.href = `/set-language/?lang=${select.value}&next=${next}`;
        });
    });

    document.querySelectorAll("form[data-confirm]").forEach((form) => {
        form.addEventListener("submit", (event) => {
            const message = form.getAttribute("data-confirm") || "Are you sure?";
            if (!confirm(message)) {
                event.preventDefault();
            }
        });
    });
})();
