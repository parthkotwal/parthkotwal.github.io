(() => {
    const THEME_KEY = "portfolio-theme";
    const root = document.documentElement;
    const themeToggle = document.getElementById("theme-toggle");
    const nav = document.querySelector("nav");
    const mobileMenuToggle = document.getElementById("mobile-menu-toggle");
    const mobileMenu = document.getElementById("mobile-menu");
    const mobileMenuIcon = mobileMenuToggle.querySelector("i");

    const applyTheme = (theme) => {
        const blueActive = theme === "blue";
        root.classList.toggle("theme-blue", blueActive);
        themeToggle.textContent = blueActive ? "Red" : "Blue";
        themeToggle.setAttribute("aria-pressed", String(blueActive));
    };

    const setMobileMenuState = (open) => {
        mobileMenu.classList.toggle("hidden", !open);
        mobileMenuToggle.setAttribute("aria-expanded", String(open));
        mobileMenuIcon.classList.toggle("fa-bars", !open);
        mobileMenuIcon.classList.toggle("fa-xmark", open);
    };

    const savedTheme = localStorage.getItem(THEME_KEY);
    applyTheme(savedTheme === "red" ? "red" : "blue");

    themeToggle.addEventListener("click", () => {
        const nextTheme = root.classList.contains("theme-blue") ? "red" : "blue";
        applyTheme(nextTheme);
        localStorage.setItem(THEME_KEY, nextTheme);
    });

    mobileMenuToggle.addEventListener("click", () => {
        setMobileMenuState(mobileMenu.classList.contains("hidden"));
    });

    mobileMenu.querySelectorAll("a").forEach((link) => {
        link.addEventListener("click", () => setMobileMenuState(false));
    });

    window.addEventListener("resize", () => {
        if (window.innerWidth >= 768) setMobileMenuState(false);
    });

    window.addEventListener(
        "scroll",
        () => nav.classList.toggle("shadow-sm", window.scrollY > 50),
        { passive: true }
    );
})();
