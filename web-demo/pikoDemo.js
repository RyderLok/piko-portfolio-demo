/**
 * Portfolio demo bootstrap.
 * Marks the UI as DEMO (no ESP32 / no cloud keys required) and
 * pulls the synthetic sound library from the local Python service.
 */
(function () {
  'use strict';

  window.PIKO_DEMO_MODE = true;

  function banner() {
    if (document.getElementById('pikoDemoBanner')) return;
    var el = document.createElement('div');
    el.id = 'pikoDemoBanner';
    el.setAttribute('role', 'status');
    el.innerHTML =
      '<strong>Portfolio demo</strong> — local mocks only. ' +
      'No API keys, database, or ESP32 required. ' +
      'Qwen labels and cloud storage are simulated.';
    document.body.insertBefore(el, document.body.firstChild);
  }

  function markCollect() {
    var target = document.getElementById('collectStatus');
    if (!target) return;
    target.classList.add('is-ready');
    target.textContent = 'Demo mode: tap Input to load sample sounds (no recorder)';
  }

  function pythonBase() {
    if (window.PikoServiceEndpoints && typeof window.PikoServiceEndpoints.resolvePythonEndpoints === 'function') {
      var ep = window.PikoServiceEndpoints.resolvePythonEndpoints();
      if (ep && ep.http) return ep.http.replace(/\/$/, '');
    }
    return 'http://127.0.0.1:8001';
  }

  async function syncHealthAndLibrary() {
    try {
      var res = await fetch(pythonBase() + '/health', { cache: 'no-store' });
      if (!res.ok) throw new Error('health ' + res.status);
      var data = await res.json();
      window.PIKO_DEMO_MODE = data.demoMode !== false;
      window.PIKO_DEMO_HEALTH = data;
    } catch (err) {
      console.warn('[piko-demo] Python not reachable yet; UI still runs in local demo mode.', err);
    }
    markCollect();
    var app = window.App;
    var client = window.SoundsApiClient;
    if (app && client && typeof client.syncIntoApp === 'function') {
      try {
        await client.syncIntoApp(app, { incremental: false });
      } catch (err) {
        console.warn('[piko-demo] library sync skipped:', err);
      }
    }
  }

  function boot() {
    banner();
    markCollect();
    syncHealthAndLibrary();
    setTimeout(syncHealthAndLibrary, 2500);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
