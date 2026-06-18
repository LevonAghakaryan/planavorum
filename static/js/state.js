/**
 * state.js — Shared mutable state + Central Orchestrator
 *
 * ARCHITECTURE: Unidirectional Data Flow
 * ─────────────────────────────────────
 *  User Action
 *      │
 *      ▼
 *  Mutation (API write)
 *      │
 *      ▼
 *  updateAppState()          ← single entry point for ALL refreshes
 *      │  fetches exactly 1× per endpoint via Promise.all
 *      ▼
 *  State.*  (updated)
 *      │
 *      ▼
 *  render*Panel() functions  ← pure UI, read State only, never fetch
 *
 * Rule: NO module other than this file may call API.getGuests(),
 *       API.getTables(), or API.getUnseatedMembers().
 */

// ── Shared mutable state ──────────────────────────────────────────────────────
const State = {
    // ── Data cache (owned by updateAppState) ──────────────────────────────
    allGuests:        [],   // Guest[]        — source of truth for all panels
    allTables:        [],   // Table[]        — source of truth for hall
    unseatedMembers:  [],   // GuestMember[]  — pre-filtered for unseated panel

    // ── Hall / canvas ─────────────────────────────────────────────────────
    zoomScale:        1.0,
    isPanning:        false,
    panStart:         { x: 0, y: 0 },
    panOffset:        { x: 0, y: 0 },
    activeMovingTable: null,
    dragOffset:       { x: 0, y: 0 },
    tablePositions:   {},   // { [tableId]: { x, y } }
    tableRotations:   {},   // { [tableId]: degrees }
    currentHallFilter: 'all',

    // ── Guest panel ───────────────────────────────────────────────────────
    selectedGuestIds:  [],
    currentMainFilter: 'all',

    // ── Unseated panel ────────────────────────────────────────────────────
    currentUnseatedFilter: 'all',
    openedGroupIds: new Set(),

    // ── Pending flows ─────────────────────────────────────────────────────
    pendingSeatGuest:   null,
    pendingSeatCount:   1,
    pendingSeatTableId: null,
    pendingSeatIndex:   null,

    // ── Add-table flow ────────────────────────────────────────────────────
    pendingNewCategory: null,
    pendingNewCapacity: 10,
    pendingNewSide:     'mutual',

    // ── Edit capacity flow ────────────────────────────────────────────────
    pendingEditTableId:    null,
    pendingEditCapacityVal: 10,
};

// ── Table geometry constants ──────────────────────────────────────────────────
const TABLE_DEFAULTS = {
    capacity: { round: 12, rectangle: 8, double_rectangle: 16, presidium: 6 },
    label:    { round: 'Կլոր', rectangle: 'Ուղղ.', double_rectangle: 'Կրկ. Ուղղ.', presidium: 'Պրեզիդիում' },
};

// ── Central Orchestrator ──────────────────────────────────────────────────────
/**
 * updateAppState()
 *
 * The ONLY function allowed to call data-fetching API endpoints.
 * Fires exactly one request per endpoint, updates State, then
 * re-renders every panel.  Always await this after any mutation.
 *
 * @param {Object} [opts]
 * @param {boolean} [opts.skipHall=false]  — skip hall re-render (e.g. rename-only actions)
 */
async function updateAppState({ skipHall = false } = {}) {
    // ── 1. Fetch all fresh data in parallel (1 request per endpoint) ──────
    const [guests, tables, unseated] = await Promise.all([
        API.getGuests(),
        API.getTables(),
        API.getUnseatedMembers(),
    ]);

    // ── 2. Commit to State ────────────────────────────────────────────────
    State.allGuests       = guests;
    State.allTables       = tables;
    State.unseatedMembers = unseated;

    // ── 3. Drive all UI panels from the now-consistent State ──────────────
    renderGuestsPanel();
    renderUnseatedPanel();
    if (!skipHall) renderHall();
}