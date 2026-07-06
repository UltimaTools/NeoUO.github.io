document.addEventListener("DOMContentLoaded", function () {
    var tocLinks = document.querySelectorAll(".wiki-toc a");
    tocLinks.forEach(function (link) {
        link.addEventListener("click", function (e) {
            e.preventDefault();
            var targetId = this.getAttribute("href").substring(1);
            var target = document.getElementById(targetId);
            if (target) {
                target.scrollIntoView({ behavior: "smooth", block: "start" });
            }
        });
    });
});