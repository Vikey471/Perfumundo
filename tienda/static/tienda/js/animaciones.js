/*
 * Animaciones de Perfumundo.
 *  1. Difuminado: los elementos aparecen desenfocados y se aclaran al entrar
 *     en pantalla (al cargar y al hacer scroll).
 *  2. Promociones: fila horizontal que se recorre con flechas.
 *  3. Contador del carrito: da un pequeño salto cuando aumenta.
 *  4. Carrusel de banners de la portada (cambia solo con difuminado).
 *  5. Menú para celular (botón de tres rayas).
 */
(function () {
    'use strict';

    /* ---------- 1. Difuminado al aparecer ---------- */

    const SELECTORES = [
        '.hero-small',
        '.hero h1',
        '.hero-description',
        '.hero-button',
        '.hero-image',
        '.section-heading',
        '.promo-header',
        '.promo-card',
        '.category-card',
        '.product-card',
        '.category-filters',
        '.catalog-filter-form',
        '.product-detail-image',
        '.product-detail-info',
        '.cart-item',
        '.cart-total',
        '.account-form',
        '.account-status',
        '.order-summary',
        '.order-card',
        '.contact-card',
        '.visit-info',
        '.visit-map'
    ];

    const elementos = document.querySelectorAll(SELECTORES.join(','));

    if ('IntersectionObserver' in window) {
        // Escalona los elementos hermanos (tarjetas de una misma fila).
        const contadorPorPadre = new Map();
        elementos.forEach(function (el) {
            const padre = el.parentElement;
            const n = contadorPorPadre.get(padre) || 0;
            contadorPorPadre.set(padre, n + 1);
            el.style.setProperty('--reveal-delay', Math.min(n, 6) * 120 + 'ms');
            el.classList.add('reveal');
        });

        const observador = new IntersectionObserver(function (entradas) {
            entradas.forEach(function (entrada) {
                if (entrada.isIntersecting) {
                    entrada.target.classList.add('is-visible');
                    observador.unobserve(entrada.target);
                }
            });
        }, { threshold: 0.15, rootMargin: '0px 0px -60px 0px' });

        elementos.forEach(function (el) { observador.observe(el); });
    }

    /* ---------- 2. Promociones con flechas ---------- */

    document.querySelectorAll('.promo-section').forEach(function (seccion) {
        const fila = seccion.querySelector('[data-promo-row]');
        const anterior = seccion.querySelector('[data-promo-prev]');
        const siguiente = seccion.querySelector('[data-promo-next]');
        if (!fila || !anterior || !siguiente) { return; }

        function paso() {
            const tarjeta = fila.querySelector('.promo-card');
            if (!tarjeta) { return fila.clientWidth; }
            const gap = parseFloat(getComputedStyle(fila).columnGap) || 0;
            const visibles = Math.max(1, Math.floor(fila.clientWidth / (tarjeta.offsetWidth + gap)));
            return visibles * (tarjeta.offsetWidth + gap);
        }

        function actualizarFlechas() {
            const max = fila.scrollWidth - fila.clientWidth - 2;
            anterior.disabled = fila.scrollLeft <= 2;
            siguiente.disabled = fila.scrollLeft >= max;
        }

        anterior.addEventListener('click', function () {
            fila.scrollBy({ left: -paso(), behavior: 'smooth' });
        });
        siguiente.addEventListener('click', function () {
            fila.scrollBy({ left: paso(), behavior: 'smooth' });
        });

        fila.addEventListener('scroll', actualizarFlechas, { passive: true });
        window.addEventListener('resize', actualizarFlechas);
        actualizarFlechas();
    });
    /* ---------- 3. Salto del contador del carrito ---------- */

    (function () {
        const contador = document.querySelector('[data-cart-count]');
        const actual = contador ? parseInt(contador.dataset.cartCount, 10) : 0;
        let anterior = null;

        try {
            anterior = parseInt(sessionStorage.getItem('perfumundo-carrito'), 10);
            sessionStorage.setItem('perfumundo-carrito', String(actual));
        } catch (e) { /* sin almacenamiento: no pasa nada */ }

        if (contador && !isNaN(anterior) && actual > anterior) {
            contador.classList.add('is-bumping');
            contador.addEventListener('animationend', function () {
                contador.classList.remove('is-bumping');
            }, { once: true });
        }
    })();
    /* ---------- 4. Carrusel de banners (automático) ---------- */

    document.querySelectorAll('[data-carousel]').forEach(function (carrusel) {
        const slides = carrusel.querySelectorAll('.banner-slide');
        const intervalo = parseInt(carrusel.dataset.intervalo, 10) || 5000;
        if (slides.length < 2) { return; }

        let actual = 0;

        setInterval(function () {
            // No avanza mientras la pestaña está oculta.
            if (document.hidden) { return; }

            slides[actual].classList.remove('is-active');
            slides[actual].setAttribute('aria-hidden', 'true');
            const enlaceAnterior = slides[actual].querySelector('a');
            if (enlaceAnterior) { enlaceAnterior.tabIndex = -1; }

            actual = (actual + 1) % slides.length;

            slides[actual].classList.add('is-active');
            slides[actual].setAttribute('aria-hidden', 'false');
            const enlace = slides[actual].querySelector('a');
            if (enlace) { enlace.tabIndex = 0; }
        }, intervalo);
    });
    /* ---------- 5. Menú para celular ---------- */

    (function () {
        const menu = document.getElementById('menu-movil');
        const fondo = document.querySelector('.mobile-overlay');
        const abrir = document.querySelector('[data-menu-open]');
        if (!menu || !fondo || !abrir) { return; }

        function abrirMenu() {
            fondo.hidden = false;
            // Espera un cuadro para que la transición se vea.
            requestAnimationFrame(function () {
                document.documentElement.classList.add('menu-abierto');
            });
            menu.setAttribute('aria-hidden', 'false');
            abrir.setAttribute('aria-expanded', 'true');
        }

        function cerrarMenu() {
            document.documentElement.classList.remove('menu-abierto');
            menu.setAttribute('aria-hidden', 'true');
            abrir.setAttribute('aria-expanded', 'false');
            setTimeout(function () { fondo.hidden = true; }, 300);
        }

        abrir.addEventListener('click', abrirMenu);
        document.querySelectorAll('[data-menu-close]').forEach(function (el) {
            el.addEventListener('click', cerrarMenu);
        });
        menu.querySelectorAll('a').forEach(function (enlace) {
            enlace.addEventListener('click', cerrarMenu);
        });
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && document.documentElement.classList.contains('menu-abierto')) {
                cerrarMenu();
            }
        });
        // Si la pantalla se agranda (girar el teléfono o tablet), se cierra.
        window.matchMedia('(min-width: 901px)').addEventListener('change', function (m) {
            if (m.matches) { cerrarMenu(); }
        });
    })();
})();
