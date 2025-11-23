document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.table-wrap').forEach(setupTableWrap);
});

function setupTableWrap(wrapper) {
  const table = wrapper.querySelector('table.data-table');
  if (!table) return;

  const rows = Array.from(table.querySelectorAll('tbody tr'));
  const perPageSelect = wrapper.querySelector('.select-page');
  const searchInput = wrapper.querySelector('.search-input');
  const pager = wrapper.querySelector('.pager');
  const noResultsMsg = wrapper.querySelector('.no-results');

  let perPage = perPageSelect ? parseInt(perPageSelect.value) : 10;
  let page = 1;
  let filtered = rows.slice();

  // Debounce helper for search input to reduce lag on large tables
  function debounce(fn, delay) {
    let timer;
    return function (...args) {
      clearTimeout(timer);
      timer = setTimeout(() => fn.apply(this, args), delay);
    };
  }

  function render() {
    const total = Math.max(1, Math.ceil(filtered.length / perPage));
    if (page > total) page = total;

    const start = (page - 1) * perPage,
      end = start + perPage;

    rows.forEach(r => (r.style.display = 'none'));
    filtered.slice(start, end).forEach(r => (r.style.display = 'table-row'));

    if (noResultsMsg) {
      noResultsMsg.style.display = filtered.length === 0 ? 'block' : 'none';
    }

    renderPager(total);
  }

  function renderPager(total) {
    if (!pager) return;

    pager.innerHTML = '';

    const info = document.createElement('span');
    info.className = 'small-muted';
    info.textContent = `Page ${page} of ${total} — ${filtered.length} item${filtered.length !== 1 ? 's' : ''}`;
    pager.appendChild(info);

    // First button
    const first = createPagerButton('First', page === 1, () => {
      page = 1;
      render();
    });
    pager.appendChild(first);

    // Prev button
    const prev = createPagerButton('Prev', page === 1, () => {
      if (page > 1) {
        page--;
        render();
      }
    });
    pager.appendChild(prev);

    // Page buttons with ellipsis for larger page sets
    const maxButtons = 7;
    let startPage = Math.max(1, page - Math.floor(maxButtons / 2));
    let endPage = Math.min(total, startPage + maxButtons - 1);

    if (endPage - startPage < maxButtons - 1) {
      startPage = Math.max(1, endPage - maxButtons + 1);
    }

    if (startPage > 1) {
      pager.appendChild(createPagerButton('1', false, () => { page = 1; render(); }));
      if (startPage > 2) {
        const dots = document.createElement('span');
        dots.textContent = '...';
        dots.className = 'dots';
        pager.appendChild(dots);
      }
    }

    for (let p = startPage; p <= endPage; p++) {
      pager.appendChild(createPagerButton(p, p === page, () => {
        page = p;
        render();
      }));
    }

    if (endPage < total) {
      if (endPage < total - 1) {
        const dots = document.createElement('span');
        dots.textContent = '...';
        dots.className = 'dots';
        pager.appendChild(dots);
      }
      pager.appendChild(createPagerButton(total, false, () => { page = total; render(); }));
    }

    // Next button
    const next = createPagerButton('Next', page === total, () => {
      if (page < total) {
        page++;
        render();
      }
    });
    pager.appendChild(next);

    // Last button
    const last = createPagerButton('Last', page === total, () => {
      page = total;
      render();
    });
    pager.appendChild(last);
  }

  function createPagerButton(text, disabled, onClick) {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.textContent = text;
    btn.disabled = disabled;
    btn.className = disabled ? 'disabled' : '';
    btn.setAttribute('aria-disabled', disabled);
    btn.addEventListener('click', onClick);
    return btn;
  }

  if (perPageSelect) {
    perPageSelect.addEventListener('change', function () {
      perPage = parseInt(this.value);
      page = 1;
      render();
    });
  }

  if (searchInput) {
    searchInput.addEventListener(
      'input',
      debounce(function () {
        const q = this.value.trim().toLowerCase();
        filtered = rows.filter((r) => r.textContent.toLowerCase().includes(q));
        page = 1;
        render();
      }, 300)
    );
  }

  render();
}

// helper for delete confirm; call from delete form buttons
function confirmDelete(formId, message) {
  const ok = confirm(message || 'Are you sure? This action cannot be undone.');
  if (ok) {
    document.getElementById(formId).submit();
  }
}
