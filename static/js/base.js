document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.querySelector('.nav-toggle');
    const menu = document.querySelector('.nav-menu');
    const header = document.querySelector('.site-header');
    const accountMenu = document.querySelector('.account-menu');
    const accountTrigger = document.querySelector('.account-trigger');
    const accountDropdown = document.querySelector('.account-dropdown');

    const closeAccountMenu = () => {
        if (!accountMenu || !accountTrigger) {
            return;
        }

        accountMenu.classList.remove('is-open');
        accountTrigger.setAttribute('aria-expanded', 'false');
    };

    const closeMenu = () => {
        if (!toggle || !menu) {
            return;
        }
        toggle.setAttribute('aria-expanded', 'false');
        toggle.setAttribute('aria-label', 'Open navigation menu');
        menu.classList.remove('open');
        document.body.classList.remove('nav-open');
        closeAccountMenu();
    };

    toggle?.addEventListener('click', () => {
        const open = toggle.getAttribute('aria-expanded') === 'true';
        toggle.setAttribute('aria-expanded', String(!open));
        toggle.setAttribute(
            'aria-label',
            open ? 'Open navigation menu' : 'Close navigation menu',
        );
        menu?.classList.toggle('open', !open);
        document.body.classList.toggle('nav-open', !open);
    });

    menu?.querySelectorAll('a').forEach((link) => {
        link.addEventListener('click', closeMenu);
    });

    accountTrigger?.addEventListener('click', (event) => {
        event.stopPropagation();
        const open = accountMenu?.classList.toggle('is-open');
        accountTrigger.setAttribute('aria-expanded', String(Boolean(open)));
    });

    accountDropdown?.addEventListener('click', (event) => {
        event.stopPropagation();
    });

    document.addEventListener('click', (event) => {
        if (!accountMenu?.contains(event.target)) {
            closeAccountMenu();
        }
    });

    window.addEventListener('resize', () => {
        if (window.innerWidth > 980) {
            closeMenu();
        }
    });

    const updateHeader = () => {
        header?.classList.toggle('is-scrolled', window.scrollY > 12);
    };

    updateHeader();
    window.addEventListener('scroll', updateHeader, { passive: true });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            closeMenu();
            closeAccountMenu();
        }
    });

    const dismissMessage = (message) => {
        if (!message || message.classList.contains('is-hiding')) {
            return;
        }

        message.classList.add('is-hiding');
        message.addEventListener('transitionend', () => message.remove(), { once: true });

        window.setTimeout(() => {
            message.remove();
        }, 350);
    };

    document.querySelectorAll('.message').forEach((message) => {
        window.setTimeout(() => dismissMessage(message), 5000);
    });

    document.querySelectorAll('.message-close').forEach((button) => {
        button.addEventListener('click', () => {
            dismissMessage(button.closest('.message'));
        });
    });
});
