(() => {
    const host = document.querySelector("[data-fire-text]");
    const layer = host?.querySelector(".fire-layer");
    if (!host || !layer) return;

    const svgNS = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(svgNS, "svg");
    svg.setAttribute("viewBox", "0 0 120 34");
    svg.setAttribute("preserveAspectRatio", "none");

    const colors = ["#e13d2d", "#ff8a1f", "#ffd04a"];
    const scales = [1, 0.7, 0.43];
    const lobeCount = 9;
    const lobes = [];

    for (let index = 0; index < lobeCount; index += 1) {
        const center = (120 / lobeCount) * (index + 0.5);
        const paths = colors.map((color) => {
            const path = document.createElementNS(svgNS, "path");
            path.setAttribute("fill", color);
            svg.appendChild(path);
            return path;
        });

        lobes.push({
            center,
            width: 16.5 + (index % 3) * 1.2,
            height: 25 + ((index * 7) % 10),
            phase: index * 0.91,
            speed: 1.55 + (index % 4) * 0.17,
            paths,
        });
    }

    layer.appendChild(svg);

    const shape = (center, width, height, sway) => {
        const base = 34;
        const half = width / 2;
        const tipX = center + sway;
        const tipY = base - height;

        return [
            `M ${center - half} ${base}`,
            `C ${center - half * 1.05} ${base - height * 0.28}, ${center - half * 0.58} ${base - height * 0.72}, ${tipX} ${tipY}`,
            `C ${center + half * 0.18} ${base - height * 0.67}, ${center + half * 0.32} ${base - height * 0.48}, ${center + half * 0.64} ${base - height * 0.31}`,
            `C ${center + half} ${base - height * 0.14}, ${center + half} ${base - height * 0.05}, ${center + half} ${base}`,
            `Q ${center} ${base + 1.4} ${center - half} ${base} Z`,
        ].join(" ");
    };

    const draw = (milliseconds = 0) => {
        const seconds = milliseconds / 1000;

        lobes.forEach((lobe, index) => {
            const pulse = 1
                + Math.sin(seconds * lobe.speed * 2.2 + lobe.phase) * 0.075
                + Math.sin(seconds * lobe.speed * 3.7 + lobe.phase * 1.6) * 0.035;
            const sway = Math.sin(seconds * lobe.speed + lobe.phase) * (1.4 + (index % 2) * 0.5);

            lobe.paths.forEach((path, layerIndex) => {
                path.setAttribute("d", shape(
                    lobe.center,
                    lobe.width * scales[layerIndex],
                    lobe.height * scales[layerIndex] * pulse,
                    sway * (1 - layerIndex * 0.2),
                ));
            });
        });
    };

    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
        draw();
        return;
    }

    let animationFrame = null;
    let active = false;

    const animate = (milliseconds) => {
        if (!active) return;
        draw(milliseconds);
        animationFrame = window.requestAnimationFrame(animate);
    };

    const start = () => {
        if (active || document.hidden) return;
        active = true;
        animationFrame = window.requestAnimationFrame(animate);
    };

    const stop = () => {
        active = false;
        if (animationFrame !== null) window.cancelAnimationFrame(animationFrame);
        animationFrame = null;
    };

    const observer = new IntersectionObserver(([entry]) => {
        if (entry.isIntersecting) start();
        else stop();
    });

    observer.observe(host);
    document.addEventListener("visibilitychange", () => {
        if (document.hidden) stop();
        else if (host.getBoundingClientRect().bottom > 0) start();
    });
})();
