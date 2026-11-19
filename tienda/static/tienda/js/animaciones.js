/*
 * Animaciones de Perfumundo.
 * Los elementos aparecen con un difuminado suave cuando entran en pantalla.
 * Si el visitante pidió "reducir movimiento" en su sistema, no se anima nada.
 */
(function () {
    'use strict';

    const SELECTORES = [
        '.section-heading',
        '.hero-content',
        '.hero-image',
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
        '.promo-strip'
    ];

    const reducirMovimiento = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const elementos = document.querySelectorAll(SELECTORES.join(','));

    if (reducirMovimiento || !('IntersectionObserver' in window)) {
        return;
    }

    // Escalona los elementos que aparecen juntos (tarjetas de una misma fila).
    const contadorPorPadre = new Map();
    elementos.forEach(function (el) {
        const padre = el.parentElement;
        const n = contadorPorPadre.get(padre) || 0;
        contadorPorPadre.set(padre, n + 1);
        el.style.setProperty('--reveal-delay', Math.min(n, 6) * 90 + 'ms');
        el.classList.add('reveal');
    });

    const observador = new IntersectionObserver(function (entradas) {
        entradas.forEach(function (entrada) {
            if (entrada.isIntersecting) {
                entrada.target.classList.add('is-visible');
                observador.unobserve(entrada.target);
            }
        });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

    elementos.forEach(function (el) { observador.observe(el); });
})();
