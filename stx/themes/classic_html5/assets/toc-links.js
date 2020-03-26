(() => {
    function isElementInViewport(el) {
        var rect = el.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.top <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.left <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }

    var references = [];

    $('[data-type=toc]:first a[data-type=xref]').each((index, source) => {
        var href = $(source).attr('href');

        if (href && href.startsWith('#')) {
            var id = href.substring(1);
            var target = document.getElementById(id);

            if (target) {
                references.push({source, target});
            }
        }
    });

    $(window).on('DOMContentLoaded load resize scroll', () => {
        var visibleTarget = null;

        for (var ref of references) {
            if(isElementInViewport(ref.target)) {
                visibleTarget = ref.target
                break;
            }
        }

        for (var ref of references) {
            if (ref.target === visibleTarget) {
                $(ref.source).addClass('active')
            }
            else {
                $(ref.source).removeClass('active');
            }
        }
    });
})();