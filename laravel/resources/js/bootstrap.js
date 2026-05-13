import * as Popper from '@popperjs/core';
import $ from 'jquery';
import * as bootstrap from 'bootstrap';

window.Popper = Popper;
window.$ = window.jQuery = $;
window.bootstrap = bootstrap;

// Bootstrap 5 dropped its jQuery plugin layer. Existing call sites use the
// `$('#x').modal('show')` style, so map each component back onto $.fn via
// the BS5 vanilla API. Calls like `.tooltip()` (no args) create an instance;
// `.modal('show')` invokes the method on the cached instance.
['Alert', 'Carousel', 'Collapse', 'Dropdown', 'Modal', 'Offcanvas',
 'Popover', 'ScrollSpy', 'Tab', 'Toast', 'Tooltip'].forEach((name) => {
    const Component = bootstrap[name];
    if (!Component) return;
    $.fn[name.toLowerCase()] = function (action, ...args) {
        return this.each(function () {
            const instance = Component.getOrCreateInstance(this);
            if (typeof action === 'string' && typeof instance[action] === 'function') {
                instance[action](...args);
            }
        });
    };
});

/**
 * We'll load the axios HTTP library which allows us to easily issue requests
 * to our Laravel back-end. This library automatically handles sending the
 * CSRF token as a header based on the value of the "XSRF" token cookie.
 */

import axios from 'axios';
window.axios = axios;

window.axios.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';

/**
 * Echo exposes an expressive API for subscribing to channels and listening
 * for events that are broadcast by Laravel. Echo and event broadcasting
 * allows your team to easily build robust real-time web applications.
 */

// import Echo from 'laravel-echo';

// window.Pusher = require('pusher-js');

// window.Echo = new Echo({
//     broadcaster: 'pusher',
//     key: process.env.VITE_PUSHER_APP_KEY,
//     cluster: process.env.VITE_PUSHER_APP_CLUSTER,
//     forceTLS: true
// });
