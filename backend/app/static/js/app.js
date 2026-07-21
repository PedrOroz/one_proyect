/**
 * FinTech Multi-Agent Support System — Frontend Application
 * ==========================================================
 * Handles chat sessions, message rendering, API calls,
 * localStorage persistence, sidebar navigation, and UI interactions.
 */

(function () {
  'use strict';

  /* ── Constants ──────────────────────────────────────────── */
  const API_BASE = '';  // same origin
  const STORAGE_KEY = 'fintech_sessions';
  const MAX_TEXTAREA_HEIGHT = 120;

  /* ── DOM References ─────────────────────────────────────── */
  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => document.querySelectorAll(sel);

  const DOM = {
    sidebar: $('#sidebar'),
    sidebarOverlay: $('#sidebarOverlay'),
    btnHamburger: $('#btnHamburger'),
    btnNewChat: $('#btnNewChat'),
    sessionsList: $('#sessionsList'),
    emptyState: $('#emptyState'),
    chatMessages: $('#chatMessages'),
    chatWelcome: $('#chatWelcome'),
    typingIndicator: $('#typingIndicator'),
    chatInput: $('#chatInput'),
    btnSend: $('#btnSend'),
    toastError: $('#toastError'),
    toastSuccess: $('#toastSuccess'),
  };

  /* ── State ──────────────────────────────────────────────── */
  let state = {
    sessions: [],        // Array of { id, title, messages[], createdAt }
    activeSessionId: null,
    isLoading: false,
  };

  /* ── Initialization ─────────────────────────────────────── */
  function init() {
    loadState();
    bindEvents();
    renderSidebar();

    // If there are sessions, load the most recent. Otherwise show welcome.
    if (state.sessions.length > 0) {
      setActiveSession(state.sessions[0].id);
    } else {
      renderMessages();
    }
  }

  /* ── Local Storage ──────────────────────────────────────── */
  function loadState() {
    try {
      const data = localStorage.getItem(STORAGE_KEY);
      if (data) {
        const parsed = JSON.parse(data);
        if (Array.isArray(parsed)) {
          state.sessions = parsed;
        }
      }
    } catch (e) {
      console.warn('Failed to load sessions from localStorage', e);
      state.sessions = [];
    }
  }

  function saveState() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state.sessions));
    } catch (e) {
      console.warn('Failed to save sessions to localStorage', e);
    }
  }

  /* ── Session Management ─────────────────────────────────── */
  function createSession(firstMessage) {
    const session = {
      id: generateId(),
      title: truncate(firstMessage, 40),
      messages: [],
      createdAt: new Date().toISOString(),
    };
    state.sessions.unshift(session);
    state.activeSessionId = session.id;
    saveState();
    renderSidebar();
    return session;
  }

  function getActiveSession() {
    return state.sessions.find((s) => s.id === state.activeSessionId) || null;
  }

  function setActiveSession(sessionId) {
    state.activeSessionId = sessionId;
    renderSidebar();
    renderMessages();
    scrollToBottom();
  }

  function deleteSession(sessionId) {
    state.sessions = state.sessions.filter((s) => s.id !== sessionId);

    if (state.activeSessionId === sessionId) {
      state.activeSessionId = state.sessions.length > 0 ? state.sessions[0].id : null;
    }

    saveState();
    renderSidebar();
    renderMessages();
  }

  /* ── Event Bindings ─────────────────────────────────────── */
  function bindEvents() {
    // New Chat
    DOM.btnNewChat.addEventListener('click', () => {
      state.activeSessionId = null;
      renderSidebar();
      renderMessages();
      DOM.chatInput.focus();
      closeSidebar();
    });

    // Send message
    DOM.btnSend.addEventListener('click', handleSend);

    // Input handling
    DOM.chatInput.addEventListener('input', handleInputChange);
    DOM.chatInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    });

    // Sidebar mobile toggle
    DOM.btnHamburger.addEventListener('click', toggleSidebar);
    DOM.sidebarOverlay.addEventListener('click', closeSidebar);

    // Suggestion chips
    $$('.suggestion-chip').forEach((chip) => {
      chip.addEventListener('click', () => {
        const text = chip.getAttribute('data-suggestion');
        DOM.chatInput.value = text;
        handleInputChange();
        handleSend();
      });
    });

    // Keyboard shortcut: Escape closes sidebar on mobile
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') closeSidebar();
    });
  }

  /* ── Input Handling ─────────────────────────────────────── */
  function handleInputChange() {
    const input = DOM.chatInput;
    // Auto-resize
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, MAX_TEXTAREA_HEIGHT) + 'px';
    // Enable/disable send
    DOM.btnSend.disabled = input.value.trim().length === 0;
  }

  /* ── Send Message ───────────────────────────────────────── */
  async function handleSend() {
    const text = DOM.chatInput.value.trim();
    if (!text || state.isLoading) return;

    // Reset input
    DOM.chatInput.value = '';
    DOM.chatInput.style.height = 'auto';
    DOM.btnSend.disabled = true;

    // Create session if needed
    let session = getActiveSession();
    if (!session) {
      session = createSession(text);
    }

    // Add user message
    const userMsg = {
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    };
    session.messages.push(userMsg);
    saveState();
    renderMessages();
    scrollToBottom();

    // Show typing indicator
    state.isLoading = true;
    showTypingIndicator();

    try {
      const response = await sendChatMessage(text, session.id);

      // Build AI message
      const aiMsg = {
        role: 'ai',
        content: response.response || response.message || 'Sin respuesta del servidor.',
        timestamp: new Date().toISOString(),
        routing: response.routing_info || null,
        sources: response.sources || [],
        messageIndex: session.messages.length, // index of this AI message
      };

      session.messages.push(aiMsg);

      // Update session title from first user message if still default
      if (session.messages.filter((m) => m.role === 'user').length === 1) {
        session.title = truncate(text, 40);
      }

      // Update session id if backend provided one
      if (response.session_id && response.session_id !== session.id) {
        session.id = response.session_id;
        state.activeSessionId = session.id;
      }

      saveState();
    } catch (err) {
      console.error('Chat API error:', err);
      const errorMsg = {
        role: 'ai',
        content: 'Lo siento, ocurrió un error al procesar tu solicitud. Por favor, intenta de nuevo.',
        timestamp: new Date().toISOString(),
        isError: true,
        messageIndex: session.messages.length,
      };
      session.messages.push(errorMsg);
      saveState();
      showToast('Error al enviar el mensaje. Verifica tu conexión.', 'error');
    } finally {
      state.isLoading = false;
      hideTypingIndicator();
      renderMessages();
      renderSidebar();
      scrollToBottom();
    }
  }

  /* ── API Calls ──────────────────────────────────────────── */
  async function sendChatMessage(message, sessionId) {
    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: message,
        session_id: sessionId || null,
      }),
    });

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    }

    return await res.json();
  }

  async function sendFeedback(sessionId, messageIndex, feedback) {
    try {
      const res = await fetch(`${API_BASE}/chat/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          message_index: messageIndex,
          feedback: feedback,
        }),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      showToast('¡Gracias por tu feedback!', 'success');
    } catch (e) {
      console.error('Feedback error:', e);
      showToast('No se pudo enviar el feedback.', 'error');
    }
  }

  /* ── Rendering: Sidebar ─────────────────────────────────── */
  function renderSidebar() {
    const list = DOM.sessionsList;
    list.innerHTML = '';

    if (state.sessions.length === 0) {
      DOM.emptyState.style.display = 'block';
      return;
    }

    DOM.emptyState.style.display = 'none';

    state.sessions.forEach((session) => {
      const isActive = session.id === state.activeSessionId;
      const el = document.createElement('div');
      el.className = `session-item${isActive ? ' active' : ''}`;
      el.setAttribute('data-session-id', session.id);

      el.innerHTML = `
        <svg class="session-item__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
        </svg>
        <span class="session-item__text" title="${escapeHtml(session.title)}">${escapeHtml(session.title)}</span>
        <button class="session-item__delete" title="Eliminar sesión" data-delete-session="${session.id}">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="3 6 5 6 21 6"></polyline>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
          </svg>
        </button>
      `;

      // Click to switch session
      el.addEventListener('click', (e) => {
        if (e.target.closest('.session-item__delete')) return;
        setActiveSession(session.id);
        closeSidebar();
      });

      // Delete button
      const deleteBtn = el.querySelector('.session-item__delete');
      deleteBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        deleteSession(session.id);
      });

      list.appendChild(el);
    });
  }

  /* ── Rendering: Messages ────────────────────────────────── */
  function renderMessages() {
    const container = DOM.chatMessages;
    const session = getActiveSession();

    // Remove all message rows (keep welcome + typing indicator)
    container.querySelectorAll('.message-row').forEach((el) => el.remove());

    if (!session || session.messages.length === 0) {
      DOM.chatWelcome.style.display = 'flex';
      DOM.typingIndicator.style.display = 'none';
      return;
    }

    DOM.chatWelcome.style.display = 'none';

    session.messages.forEach((msg, idx) => {
      const row = createMessageElement(msg, idx, session);
      container.insertBefore(row, DOM.typingIndicator);
    });
  }

  function createMessageElement(msg, index, session) {
    const row = document.createElement('div');
    row.className = `message-row message-row--${msg.role === 'user' ? 'user' : 'ai'}`;
    row.style.animationDelay = '0ms'; // already rendered, no stagger needed

    if (msg.role === 'user') {
      row.innerHTML = `
        <div class="message-bubble message-bubble--user">
          <div class="message-bubble__content">${formatMessageContent(msg.content)}</div>
          <div class="message-time">${formatTime(msg.timestamp)}</div>
        </div>
      `;
    } else {
      const sourcesHtml = buildSourcesHtml(msg);
      const routingHtml = buildRoutingHtml(msg);
      const feedbackHtml = buildFeedbackHtml(msg, index, session);

      row.innerHTML = `
        <div class="message-bubble message-bubble--ai${msg.isError ? ' message-bubble--error' : ''}">
          <div class="message-bubble__ai-label">[🤖 IA]:</div>
          <div class="message-bubble__content">${formatMessageContent(msg.content)}</div>
          ${routingHtml}
          ${sourcesHtml}
          ${feedbackHtml}
          <div class="message-time">${formatTime(msg.timestamp)}</div>
        </div>
      `;

      // Bind sources toggle
      const sourcesToggle = row.querySelector('.message-sources__toggle');
      if (sourcesToggle) {
        sourcesToggle.addEventListener('click', () => {
          const sourcesEl = sourcesToggle.closest('.message-sources');
          sourcesEl.classList.toggle('open');
        });
      }

      // Bind feedback buttons
      bindFeedbackButtons(row, msg, index, session);
    }

    return row;
  }

  function buildSourcesHtml(msg) {
    const sources = msg.sources || [];
    // Also try to extract sources from routing info if present
    if (sources.length === 0 && msg.routing && msg.routing.explanation) {
      sources.push(msg.routing.explanation);
    }

    if (sources.length === 0) {
      // Still show the accordion but with a generic message
      return `
        <div class="message-sources">
          <button class="message-sources__toggle">
            <span class="message-sources__toggle-icon">▶</span>
            Ver fuentes utilizadas (0)
          </button>
          <div class="message-sources__list">
            <div class="message-sources__item">
              <span class="message-sources__item-icon">📄</span>
              <span>No se utilizaron fuentes externas para esta respuesta.</span>
            </div>
          </div>
        </div>
      `;
    }

    const itemsHtml = sources
      .map(
        (src) => `
        <div class="message-sources__item">
          <span class="message-sources__item-icon">📄</span>
          <span>${escapeHtml(typeof src === 'string' ? src : src.title || src.name || JSON.stringify(src))}</span>
        </div>
      `
      )
      .join('');

    return `
      <div class="message-sources">
        <button class="message-sources__toggle">
          <span class="message-sources__toggle-icon">▶</span>
          Ver fuentes utilizadas (${sources.length})
        </button>
        <div class="message-sources__list">
          ${itemsHtml}
        </div>
      </div>
    `;
  }

  function buildRoutingHtml(msg) {
    if (!msg.routing || !msg.routing.routed_to) return '';

    const confidence = msg.routing.confidence != null
      ? `${Math.round(msg.routing.confidence * 100)}%`
      : '';

    return `
      <div class="message-routing">
        <span class="message-routing__dot"></span>
        Agente: ${escapeHtml(msg.routing.routed_to)}${confidence ? ` • ${confidence} confianza` : ''}
      </div>
    `;
  }

  function buildFeedbackHtml(msg, index, session) {
    if (msg.role === 'user') return '';

    const positive = msg.feedback === 'positive';
    const negative = msg.feedback === 'negative';
    const hasFeedback = positive || negative;

    return `
      <div class="message-feedback">
        <button class="message-feedback__btn${positive ? ' active-positive' : ''}${hasFeedback && !positive ? ' disabled' : ''}"
                data-feedback="positive" title="Útil">
          👍
        </button>
        <button class="message-feedback__btn${negative ? ' active-negative' : ''}${hasFeedback && !negative ? ' disabled' : ''}"
                data-feedback="negative" title="No útil">
          👎
        </button>
      </div>
    `;
  }

  function bindFeedbackButtons(row, msg, index, session) {
    const feedbackBtns = row.querySelectorAll('.message-feedback__btn');
    feedbackBtns.forEach((btn) => {
      btn.addEventListener('click', () => {
        if (msg.feedback) return; // already submitted

        const feedback = btn.getAttribute('data-feedback');
        msg.feedback = feedback;
        saveState();

        // Update UI
        feedbackBtns.forEach((b) => {
          const fb = b.getAttribute('data-feedback');
          if (fb === feedback) {
            b.classList.add(feedback === 'positive' ? 'active-positive' : 'active-negative');
          } else {
            b.classList.add('disabled');
          }
        });

        // Send to API
        sendFeedback(session.id, msg.messageIndex ?? index, feedback);
      });
    });
  }

  /* ── Content Formatting ─────────────────────────────────── */
  function formatMessageContent(text) {
    if (!text) return '';

    // Escape HTML first
    let html = escapeHtml(text);

    // Bold: **text**
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Inline code: `text`
    html = html.replace(/`(.*?)`/g, '<code>$1</code>');

    // Line breaks to paragraphs
    const paragraphs = html.split(/\n\n+/);
    if (paragraphs.length > 1) {
      html = paragraphs.map((p) => `<p>${p.replace(/\n/g, '<br/>')}</p>`).join('');
    } else {
      html = html.replace(/\n/g, '<br/>');
    }

    return html;
  }

  /* ── Typing Indicator ───────────────────────────────────── */
  function showTypingIndicator() {
    DOM.typingIndicator.classList.add('visible');
    scrollToBottom();
  }

  function hideTypingIndicator() {
    DOM.typingIndicator.classList.remove('visible');
  }

  /* ── Sidebar Toggle (Mobile) ────────────────────────────── */
  function toggleSidebar() {
    const isOpen = DOM.sidebar.classList.contains('open');
    if (isOpen) {
      closeSidebar();
    } else {
      openSidebar();
    }
  }

  function openSidebar() {
    DOM.sidebar.classList.add('open');
    DOM.sidebarOverlay.classList.add('visible');
    DOM.sidebarOverlay.style.display = 'block';
  }

  function closeSidebar() {
    DOM.sidebar.classList.remove('open');
    DOM.sidebarOverlay.classList.remove('visible');
    // Delay hiding to allow transition
    setTimeout(() => {
      if (!DOM.sidebar.classList.contains('open')) {
        DOM.sidebarOverlay.style.display = '';
      }
    }, 300);
  }

  /* ── Scroll ─────────────────────────────────────────────── */
  function scrollToBottom() {
    requestAnimationFrame(() => {
      DOM.chatMessages.scrollTop = DOM.chatMessages.scrollHeight;
    });
  }

  /* ── Toast Notifications ────────────────────────────────── */
  function showToast(message, type = 'error') {
    const el = type === 'error' ? DOM.toastError : DOM.toastSuccess;
    el.textContent = message;
    el.classList.add('visible');

    setTimeout(() => {
      el.classList.remove('visible');
    }, 3500);
  }

  /* ── Utilities ──────────────────────────────────────────── */
  function generateId() {
    return 'session_' + Date.now().toString(36) + '_' + Math.random().toString(36).substr(2, 6);
  }

  function truncate(str, len) {
    if (!str) return 'Nueva conversación';
    return str.length > len ? str.substring(0, len) + '…' : str;
  }

  function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  function formatTime(isoString) {
    if (!isoString) return '';
    try {
      const date = new Date(isoString);
      return date.toLocaleTimeString('es-MX', {
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return '';
    }
  }

  /* ── Boot ───────────────────────────────────────────────── */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
