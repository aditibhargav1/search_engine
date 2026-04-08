/**
 * script.js — NEXUS Search Engine Frontend
 * Handles search API calls, result rendering, keyboard events, and index stats
 */

"use strict";

const input          = document.getElementById("searchInput");
const btn            = document.getElementById("searchBtn");
const resultsSection = document.getElementById("resultsSection");
const headerStats    = document.getElementById("headerStats");

/* ── Load index stats on page ready ────────────────────────────────────────── */
window.addEventListener("DOMContentLoaded", () => {
  loadStats();
  input.focus();
});

async function loadStats() {
  try {
    const res  = await fetch("/stats");
    const data = await res.json();
    if (data.index_loaded) {
      headerStats.innerHTML = `
        <span class="stat-pill live">● INDEX ACTIVE</span>
        <span class="stat-pill">${data.total_words.toLocaleString()} WORDS INDEXED</span>
      `;
    } else {
      headerStats.innerHTML = `<span class="stat-pill">⚠ INDEX NOT LOADED — run pyspark_index.py</span>`;
    }
  } catch {
    headerStats.innerHTML = `<span class="stat-pill">⚠ SERVER UNREACHABLE</span>`;
  }
}

/* ── Enter-key shortcut ─────────────────────────────────────────────────────── */
input.addEventListener("keydown", (e) => {
  if (e.key === "Enter") runSearch();
});

/* ── Quick search from hint chips ──────────────────────────────────────────── */
function quickSearch(word) {
  input.value = word;
  runSearch();
}

/* ── Main search function ───────────────────────────────────────────────────── */
async function runSearch() {
  const query = input.value.trim();
  if (!query) {
    showError("Please enter a search term.");
    return;
  }

  showLoader(query);
  setButtonLoading(true);

  try {
    const res  = await fetch(`/search?word=${encodeURIComponent(query)}`);
    const data = await res.json();

    if (!res.ok) {
      showError(data.error || "An unexpected error occurred.");
      return;
    }

    renderResults(data);
  } catch (err) {
    showError("Could not reach the server. Is Flask running?");
  } finally {
    setButtonLoading(false);
  }
}

/* ── Render results ─────────────────────────────────────────────────────────── */
function renderResults({ word, documents, count }) {
  if (count === 0) {
    resultsSection.innerHTML = `
      <div class="result-meta">
        <div class="query-echo">
          <span>Results for</span>
          <span class="keyword">"${escHtml(word)}"</span>
        </div>
        <span class="result-count">0 matches</span>
      </div>
      <div class="no-results">
        <div class="no-results-icon">◌</div>
        <div class="no-results-title">No documents found</div>
        <div class="no-results-sub">The word "<strong>${escHtml(word)}</strong>" isn't in the index. Try a different term.</div>
      </div>
    `;
    return;
  }

  const cards = documents
    .map(
      (doc, i) => `
        <div class="doc-card" style="animation-delay:${i * 0.06}s">
          <div class="doc-icon">📄</div>
          <div class="doc-info">
            <div class="doc-name">${escHtml(doc)}</div>
            <div class="doc-label">Text Document</div>
          </div>
        </div>
      `
    )
    .join("");

  resultsSection.innerHTML = `
    <div class="result-meta">
      <div class="query-echo">
        <span>Results for</span>
        <span class="keyword">"${escHtml(word)}"</span>
      </div>
      <span class="result-count found">${count} match${count !== 1 ? "es" : ""}</span>
    </div>
    <div class="doc-grid">${cards}</div>
  `;
}

/* ── UI state helpers ────────────────────────────────────────────────────────── */
function showLoader(query) {
  resultsSection.innerHTML = `
    <div class="loader">
      <div class="loader-dots">
        <span></span><span></span><span></span>
      </div>
      <span>Searching index for "<strong>${escHtml(query)}</strong>"…</span>
    </div>
  `;
}

function showError(msg) {
  resultsSection.innerHTML = `
    <div class="error-box">⚠ ${escHtml(msg)}</div>
  `;
}

function setButtonLoading(loading) {
  btn.classList.toggle("loading", loading);
  btn.disabled = loading;
  btn.querySelector(".btn-label").textContent = loading ? "SEARCHING" : "SEARCH";
  btn.querySelector(".btn-icon").textContent  = loading ? "…" : "→";
}

/* ── XSS-safe HTML escape ─────────────────────────────────────────────────── */
function escHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
