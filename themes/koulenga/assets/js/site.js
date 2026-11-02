/*
 * themes/koulenga/assets/js/site.js — JS vanilla du thème Koulenga.
 * Portage sans jQuery de js/site.js + js/jquery.treemenu.js du thème Quark
 * (§6.3 du plan v2) :
 *   - header « scrolled » au défilement (> 75 px) ;
 *   - menu burger plein écran (overlay #overlay, toggle #toggle) avec
 *     accessibilité (§6.4) : aria-expanded/aria-label, aria-hidden sur l'overlay,
 *     gestion du focus (focus sur le 1er lien à l'ouverture, retour au burger à
 *     la fermeture), fermeture par Escape ;
 *   - tree menu du mobile (togglers +/- de jquery.treemenu.js, classes tree-closed/
 *     tree-opened/tree-empty du CSS Quark) avec support clavier ;
 *   - défilement doux #to-start → #start (respecté si prefers-reduced-motion).
 * Les libellés aria viennent d'i18n (attributs data-menu-open/data-menu-close sur
 * #toggle et data-tree-toggle-label sur <html>) — aucune chaîne en dur.
 */
(function () {
  'use strict';

  var reduceMotion = false;
  try {
    reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  } catch (e) { /* media query non supportée : comportement par défaut */ }

  /* --- Header « scrolled » au défilement (port de site.js de Quark) --- */
  var header = document.getElementById('header');

  function scrollTop() {
    return window.pageYOffset || document.documentElement.scrollTop || 0;
  }

  function scrollHeader() {
    if (!header) { return; }
    if (scrollTop() > 75) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
  }

  scrollHeader();
  window.addEventListener('scroll', scrollHeader, { passive: true });

  /* --- Menu burger plein écran + overlay (port de site.js de Quark, + a11y §6.4) --- */
  var toggle = document.getElementById('toggle');
  var overlay = document.getElementById('overlay');

  function setMenu(open) {
    if (!toggle || !overlay) { return; }
    var openLabel = toggle.getAttribute('data-menu-open') || '';
    var closeLabel = toggle.getAttribute('data-menu-close') || openLabel;
    toggle.classList.toggle('active', open);
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    toggle.setAttribute('aria-label', open ? closeLabel : openLabel);
    overlay.classList.toggle('open', open);
    overlay.setAttribute('aria-hidden', open ? 'false' : 'true');
    document.body.classList.toggle('mobile-nav-open', open);
    if (open) {
      var firstLink = overlay.querySelector('a');
      if (firstLink) { firstLink.focus(); }
    } else {
      toggle.focus();
    }
  }

  function menuIsOpen() {
    return !!(toggle && toggle.classList.contains('active'));
  }

  function toggleMenu() {
    setMenu(!menuIsOpen());
  }

  if (toggle && overlay) {
    toggle.addEventListener('click', toggleMenu);
    toggle.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        toggleMenu();
      }
    });
    /* Escape ferme le menu où que soit le focus (§6.4) */
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { setMenu(false); }
    });
  }

  /* --- Tree menu du mobile (port de jquery.treemenu.js 0.6, © 2014 Stepan Krapivin) --- */
  var TREE_LABEL = document.documentElement.getAttribute('data-tree-toggle-label') || '';

  function firstChildUl(li) {
    var children = li.children;
    for (var i = 0; i < children.length; i++) {
      if (children[i].tagName === 'UL') { return children[i]; }
    }
    return null;
  }

  function makeToggler(li, subtree) {
    var button = document.createElement('span');
    button.className = 'toggler';
    button.setAttribute('role', 'button');
    button.setAttribute('tabindex', '0');
    if (TREE_LABEL) { button.setAttribute('aria-label', TREE_LABEL); }
    if (subtree) {
      button.setAttribute('aria-expanded', 'false');
    }
    li.insertBefore(button, li.firstChild);
    return button;
  }

  function onToggle() {
    var li = this.parentNode;
    var subtree = firstChildUl(li);
    var closed = li.classList.contains('tree-closed');
    li.classList.toggle('tree-opened', closed);
    li.classList.toggle('tree-closed', !closed);
    this.setAttribute('aria-expanded', closed ? 'true' : 'false');
    if (subtree) {
      subtree.style.display = closed ? 'block' : 'none';
    }
  }

  function walk(ul) {
    var items = ul.children;
    for (var i = 0; i < items.length; i++) {
      var li = items[i];
      if (li.tagName !== 'LI') { continue; }
      var subtree = firstChildUl(li);
      var button = li.querySelector('.toggler');
      if (!button) {
        button = makeToggler(li, subtree);
      }
      if (subtree) {
        li.classList.add('tree-closed');
        subtree.style.display = 'none';
        button.addEventListener('click', onToggle);
        button.addEventListener('keydown', function (e) {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            onToggle.call(this);
          }
        });
        walk(subtree);
      } else {
        li.classList.add('tree-empty');
      }
    }
  }

  function treeMenu(root) {
    root.classList.add('treemenu');
    if (!root.classList.contains('treemenu-root')) {
      root.classList.add('treemenu-root');
    }
    walk(root);
  }

  var trees = document.querySelectorAll('ul.tree');
  for (var t = 0; t < trees.length; t++) {
    treeMenu(trees[t]);
  }

  /* --- #to-start : défilement doux vers #start (port de site.js de Quark) --- */
  var toStart = document.getElementById('to-start');
  if (toStart) {
    toStart.addEventListener('click', function () {
      var start = document.getElementById('start');
      if (!start) { return; }
      var y = start.getBoundingClientRect().top + scrollTop() - 45;
      window.scrollTo({ top: y, left: 0, behavior: reduceMotion ? 'auto' : 'smooth' });
    });
  }
}());