/**
 * api.js — All API calls in one place.
 *
 * READ endpoints (getGuests, getTables, getUnseatedMembers) return
 * parsed JSON directly ([] on failure) so updateAppState() can
 * safely destructure them from Promise.all without extra .json() calls.
 *
 * WRITE endpoints still return the raw Response so callers can check
 * .ok and read error bodies when needed.
 *
 * Depends on: weddingId, weddingToken (globals injected from template)
 */

async function apiFetch(url, options = {}) {
    options.headers = {
        ...(options.headers || {}),
        'X-Wedding-Token': weddingToken,
    };
    return fetch(url, options);
}

const API = {
    // ── Wedding ──────────────────────────────────────────────────────────────
    /** @returns {Response} */
    getWedding: () =>
        apiFetch(`/api/v1/weddings/${weddingId}`),

    // ── Guests  (READ → returns parsed array) ────────────────────────────────
    /** @returns {Promise<Guest[]>} */
    getGuests: async () => {
        const res = await apiFetch(`/api/v1/guests/wedding/${weddingId}`);
        return res.ok ? res.json() : [];
    },

    /** @returns {Response} */
    createGuest: (display_name, total_count, side) =>
        apiFetch(`/api/v1/guests/?wedding_id=${weddingId}`, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ wedding_id: weddingId, display_name, total_count, side, status: 'confirmed' }),
        }),

    /** @returns {Response} */
    deleteGuest: (guestId) =>
        apiFetch(`/api/v1/guests/${guestId}?wedding_id=${weddingId}`, { method: 'DELETE' }),

    /** @returns {Response} */
    mergeGuests: (guest_ids, new_display_name) =>
        apiFetch(`/api/v1/guests/wedding/${weddingId}/merge`, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ guest_ids, new_display_name }),
        }),

    // ── Tables  (READ → returns parsed array) ────────────────────────────────
    /** @returns {Promise<Table[]>} */
    getTables: async () => {
        const res = await apiFetch(`/api/v1/tables/wedding/${weddingId}`);
        return res.ok ? res.json() : [];
    },

    /** @returns {Response} */
    createTable: (table_number, category, capacity, side) =>
        apiFetch(`/api/v1/tables/?wedding_id=${weddingId}`, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ wedding_id: weddingId, table_number, category, capacity, side }),
        }),

    /** @returns {Response} */
    deleteTable: (tableId) =>
        apiFetch(`/api/v1/tables/${tableId}?wedding_id=${weddingId}`, { method: 'DELETE' }),

    /** @returns {Response} */
    updateTableCapacity: (tableId, capacity) =>
        apiFetch(`/api/v1/tables/${tableId}/capacity?wedding_id=${weddingId}&capacity=${capacity}`, { method: 'PUT' }),

    /** @returns {Response} */
    updateTablePosition: (tableId, x_pos, y_pos) =>
        apiFetch(`/api/v1/tables/${tableId}/position?wedding_id=${weddingId}`, {
            method:  'PUT',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ x_pos, y_pos }),
        }),

    /** @returns {Response} */
    bulkUpdatePositions: (positions) =>
        apiFetch(`/api/v1/tables/bulk-position?wedding_id=${weddingId}`, {
            method:  'PUT',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ positions }),
        }),

    // ── Guest Members  (READ → returns parsed array) ─────────────────────────
    /** @returns {Promise<GuestMember[]>} */
    getAllMembers: async () => {
        const res = await apiFetch(`/api/v1/guest-members/wedding/${weddingId}`);
        return res.ok ? res.json() : [];
    },

    /** @returns {Promise<GuestMember[]>} */
    getUnseatedMembers: async () => {
        const res = await apiFetch(`/api/v1/guest-members/wedding/${weddingId}/unseated`);
        return res.ok ? res.json() : [];
    },

    /** @returns {Response} */
    seatMember: (memberId, tableId, seatIndex) => {
        let url = `/api/v1/guest-members/${memberId}/seat?wedding_id=${weddingId}`;
        if (tableId   != null) url += `&table_id=${tableId}`;
        if (seatIndex != null) url += `&seat_index=${seatIndex}`;
        return apiFetch(url, { method: 'PUT' });
    },

    /** @returns {Response} */
    unseatMember: (memberId) =>
        apiFetch(`/api/v1/guest-members/${memberId}/seat?wedding_id=${weddingId}`, { method: 'PUT' }),

    /** @returns {Response} */
    renameMember: (memberId, first_name) =>
        apiFetch(
            `/api/v1/guest-members/${memberId}/name?wedding_id=${weddingId}&first_name=${encodeURIComponent(first_name)}`,
            { method: 'PUT' },
        ),
};

// ── Seating helpers ───────────────────────────────────────────────────────────

/**
 * Find the next free seat_index for a table using State (no extra fetch).
 * State.allTables and State.allGuests must already be populated.
 */
function findNextFreeSeatFromState(tableId) {
    const table = State.allTables.find(t => t.id === tableId);
    if (!table) return null;

    const allMembers = State.allGuests.flatMap(g => g.members);
    const occupied   = new Set(
        allMembers
            .filter(m => m.table_id === tableId && m.seat_index != null)
            .map(m => m.seat_index),
    );
    for (let i = 0; i < table.capacity; i++) {
        if (!occupied.has(i)) return i;
    }
    return null;
}

/**
 * Seat a member on a table, auto-assigning the next free seat_index.
 * Does NOT trigger a state refresh — callers must await updateAppState() after.
 *
 * @returns {boolean} true on success
 */
async function seatMemberOnTable(memberId, tableId) {
    const seatIndex = findNextFreeSeatFromState(tableId);
    if (seatIndex === null) {
        alert('Ազատ տեղ չկա։');
        return false;
    }
    const res = await API.seatMember(memberId, tableId, seatIndex);
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        alert(err.detail || 'Սխալ');
        return false;
    }
    return true;
}