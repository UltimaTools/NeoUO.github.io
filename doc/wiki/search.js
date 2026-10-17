(function () {
    "use strict";

    var MAX_RESULTS = 20;
    var input = document.getElementById("wiki-search-input");
    var panel = document.getElementById("wiki-search-results");
    if (!input || !panel) return;

    var entries = null;
    var loadPromise = null;
    var indexError = false;
    var results = [];
    var activeIndex = -1;
    var searchTimer = null;
    var searchSeq = 0;

    var version = (input.parentElement && input.parentElement.getAttribute("data-version")) || "";
    var indexUrl = "./search-index.json" + (version ? "?v=" + encodeURIComponent(version) : "");

    function loadIndex() {
        if (entries) return Promise.resolve(entries);
        if (loadPromise) return loadPromise;
        loadPromise = fetch(indexUrl, { credentials: "same-origin" })
            .then(function (response) {
                if (!response.ok) throw new Error("HTTP " + response.status);
                return response.json();
            })
            .then(function (data) {
                entries = Array.isArray(data.entries) ? data.entries : [];
                return entries;
            })
            .catch(function (error) {
                indexError = true;
                entries = [];
                console.error("API search index failed to load:", error);
                return entries;
            });
        return loadPromise;
    }

    function tokenize(query) {
        return (query || "").toLowerCase().split(/\s+/).filter(Boolean);
    }

    function scoreEntry(entry, tokens, query) {
        var name = (entry.n || "").toLowerCase();
        var cls = (entry.c || "").toLowerCase();
        var desc = (entry.d || "").toLowerCase();
        var extra = (entry.s || "").toLowerCase();
        var last = name.split(".").pop() || name;
        var total = 0;

        for (var i = 0; i < tokens.length; i++) {
            var token = tokens[i];
            var points;
            if (name === token) points = 1200;
            else if (last === token) points = 1000;
            else if (name.indexOf(token) === 0) points = 800;
            else if (last.indexOf(token) === 0) points = 700;
            else if (name.indexOf(token) !== -1) points = 500;
            else if (cls === token) points = 450;
            else if (cls.indexOf(token) !== -1) points = 250;
            else if (extra.indexOf(token) !== -1) points = 150;
            else if (desc.indexOf(token) !== -1) points = 100;
            else return -1;
            total += points;
        }

        if (name.indexOf(query) !== -1) total += 300;
        return total - name.length * 0.5;
    }

    function search(query) {
        if (!entries) return;

        var tokens = tokenize(query);
        if (!tokens.length) {
            results = [];
            hidePanel();
            return;
        }

        var normalized = query.trim().toLowerCase();
        var scored = [];
        for (var i = 0; i < entries.length; i++) {
            var score = scoreEntry(entries[i], tokens, normalized);
            if (score >= 0) scored.push({ entry: entries[i], score: score });
        }
        scored.sort(function (a, b) {
            return b.score - a.score || a.entry.n.localeCompare(b.entry.n);
        });

        results = scored.slice(0, MAX_RESULTS).map(function (item) { return item.entry; });
        renderResults(query);
    }

    function snippet(entry, query) {
        var text = entry.d || entry.s || "";
        if (!text) return "";

        var tokens = tokenize(query);
        var lower = text.toLowerCase();
        var match = -1;
        for (var i = 0; i < tokens.length; i++) {
            var index = lower.indexOf(tokens[i]);
            if (index !== -1 && (match === -1 || index < match)) match = index;
        }

        if (match > 70) text = "..." + text.slice(match - 50).trim();
        if (text.length > 170) text = text.slice(0, 170).trim() + "...";
        return text;
    }

    function appendHighlighted(element, text, query) {
        var tokens = tokenize(query);
        var lower = text.toLowerCase();
        var ranges = [];
        for (var i = 0; i < tokens.length; i++) {
            var from = 0;
            var index;
            while ((index = lower.indexOf(tokens[i], from)) !== -1) {
                ranges.push([index, index + tokens[i].length]);
                from = index + tokens[i].length;
            }
        }

        if (!ranges.length) {
            element.appendChild(document.createTextNode(text));
            return;
        }

        ranges.sort(function (a, b) { return a[0] - b[0] || a[1] - b[1]; });
        var merged = [];
        for (var r = 0; r < ranges.length; r++) {
            var last = merged[merged.length - 1];
            if (last && ranges[r][0] <= last[1]) last[1] = Math.max(last[1], ranges[r][1]);
            else merged.push([ranges[r][0], ranges[r][1]]);
        }

        var position = 0;
        for (var m = 0; m < merged.length; m++) {
            if (merged[m][0] > position) {
                element.appendChild(document.createTextNode(text.slice(position, merged[m][0])));
            }
            var mark = document.createElement("mark");
            mark.textContent = text.slice(merged[m][0], merged[m][1]);
            element.appendChild(mark);
            position = merged[m][1];
        }
        if (position < text.length) {
            element.appendChild(document.createTextNode(text.slice(position)));
        }
    }

    function renderResults(query) {
        panel.textContent = "";
        activeIndex = -1;
        input.removeAttribute("aria-activedescendant");

        if (!results.length) {
            var empty = document.createElement("div");
            empty.className = "wiki-search-empty";
            empty.textContent = indexError ? "Search unavailable" : "No matches";
            panel.appendChild(empty);
            showPanel();
            return;
        }

        results.forEach(function (entry, index) {
            var item = document.createElement("a");
            item.className = "wiki-search-result";
            item.href = entry.u;
            item.id = "wiki-search-result-" + index;
            item.setAttribute("role", "option");
            item.addEventListener("mouseenter", function () { setActive(index); });
            item.addEventListener("click", function () { hidePanel(); });

            var kind = document.createElement("span");
            kind.className = "wiki-search-kind wiki-search-kind-" + entry.k;
            kind.textContent = entry.k === "class" ? "C" : (entry.k === "property" ? "P" : "M");
            kind.title = entry.k.charAt(0).toUpperCase() + entry.k.slice(1);

            var main = document.createElement("span");
            main.className = "wiki-search-main";

            var name = document.createElement("span");
            name.className = "wiki-search-name";
            appendHighlighted(name, entry.n || "", query);
            main.appendChild(name);

            var subText = snippet(entry, query);
            if (subText) {
                var sub = document.createElement("span");
                sub.className = "wiki-search-snippet";
                sub.textContent = subText;
                main.appendChild(sub);
            }

            item.appendChild(kind);
            item.appendChild(main);
            panel.appendChild(item);
        });

        showPanel();
    }

    function setActive(index) {
        if (index === activeIndex) return;
        var items = panel.querySelectorAll(".wiki-search-result");
        for (var i = 0; i < items.length; i++) {
            items[i].classList.toggle("active", i === index);
        }
        activeIndex = index;
        if (index >= 0 && items[index]) {
            input.setAttribute("aria-activedescendant", items[index].id);
            items[index].scrollIntoView({ block: "nearest" });
        } else {
            input.removeAttribute("aria-activedescendant");
        }
    }

    function positionPanel() {
        var rect = input.getBoundingClientRect();
        var viewportWidth = document.documentElement.clientWidth || window.innerWidth;
        var width = Math.min(560, Math.max(300, viewportWidth - 24));
        var left = Math.min(Math.max(12, rect.left), viewportWidth - width - 12);
        var available = window.innerHeight - rect.bottom - 24;

        panel.style.left = left + "px";
        panel.style.top = (rect.bottom + 6) + "px";
        panel.style.width = width + "px";
        panel.style.maxHeight = Math.max(180, Math.min(480, available)) + "px";
    }

    function showPanel() {
        if (!panel.hidden) {
            positionPanel();
            return;
        }
        panel.hidden = false;
        input.setAttribute("aria-expanded", "true");
        positionPanel();
    }

    function hidePanel() {
        if (panel.hidden) return;
        panel.hidden = true;
        input.setAttribute("aria-expanded", "false");
        input.removeAttribute("aria-activedescendant");
        activeIndex = -1;
    }

    function scheduleSearch() {
        var query = input.value;
        var seq = ++searchSeq;
        clearTimeout(searchTimer);
        searchTimer = setTimeout(function () {
            loadIndex().then(function () {
                if (seq === searchSeq) search(query);
            });
        }, 60);
    }

    input.addEventListener("input", scheduleSearch);
    input.addEventListener("focus", function () {
        if (input.value.trim()) scheduleSearch();
    });

    input.addEventListener("keydown", function (event) {
        if (event.key === "ArrowDown") {
            if (!results.length) return;
            event.preventDefault();
            setActive(Math.min(activeIndex + 1, results.length - 1));
        } else if (event.key === "ArrowUp") {
            if (!results.length) return;
            event.preventDefault();
            setActive(activeIndex <= 0 ? 0 : activeIndex - 1);
        } else if (event.key === "Enter") {
            if (panel.hidden || !results.length) return;
            event.preventDefault();
            var index = activeIndex >= 0 ? activeIndex : 0;
            window.location.assign(results[index].u);
        } else if (event.key === "Escape") {
            if (!panel.hidden) {
                event.preventDefault();
                hidePanel();
            }
        } else if (event.key === "Tab") {
            hidePanel();
        }
    });

    document.addEventListener("mousedown", function (event) {
        if (event.target === input || panel.contains(event.target)) return;
        hidePanel();
    });

    document.addEventListener("keydown", function (event) {
        if ((event.ctrlKey || event.metaKey) && (event.key === "k" || event.key === "K")) {
            event.preventDefault();
            input.focus();
            input.select();
        }
    });

    window.addEventListener("resize", function () {
        if (!panel.hidden) positionPanel();
    });
    window.addEventListener("scroll", function () {
        if (!panel.hidden) positionPanel();
    }, true);

    function preload() { loadIndex(); }
    if (typeof window.requestIdleCallback === "function") {
        window.requestIdleCallback(preload, { timeout: 2500 });
    } else {
        setTimeout(preload, 1500);
    }
})();
