(() => {
    $('body').append('<div id="layout-center"><main></main></div>');
    $('main:first-of-type').append($('body > :not(#layout-center)'));
    $('<div id="layout-start"></div>').insertBefore($('#layout-center'));
    $('#layout-start').append($('[data-type=toc]:first'));

    ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'].forEach(tag => {
        for (var element of document.getElementsByTagName(tag)) {
            var id = element.parentElement.getAttribute('id');
            if (id) {
                var anchor = document.createElement('a')
                anchor.setAttribute('href', `#${id}`);
                anchor.className = 'section-mark';
                anchor.innerHTML = '&sect;';
                element.appendChild(anchor)
            }
        }
    });
})();
