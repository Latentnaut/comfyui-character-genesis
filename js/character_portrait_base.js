/**
 * Character Portrait Base — Frontend Extension
 * Adds a single unified "Trait Browser" button that opens a modern modal 
 * with a sidebar to navigate and configure all probabilistic traits.
 */

import { app } from "../../scripts/app.js";

// ─── Config: which widget names map to which API trait name ────────────────
const TRAIT_WIDGETS = {
    "casting_archetype": "casting_archetype",
    "casting_market": "casting_market",
    "casting_brand":  "casting_brand",
    "age":            "age",
    "skin_tone":      "skin_tone",
    "skin_features":  "skin_features",
    "nationality":    "nationality",
    "bone_structure": "bone_structure",
    "eyes_color":     "eyes_color",
    "eyes_shape":     "eyes_shape",
    "eyes_details":   "eyes_details",
    "hair_style":     "hair_style",
    "hair_color":     "hair_color",
    "hair_length":    "hair_length",
    "beard":          "beard",
    "beard_color":    "beard_color",
    "makeup":         "makeup",
    "makeup_color":   "makeup_color",
    "expression":     "face_expression",
};

// ─── Styles ───────────────────────────────────────────────────────────────
const STYLE_ID = "cpb-unified-styles";
if (!document.getElementById(STYLE_ID)) {
    const style = document.createElement("style");
    style.id = STYLE_ID;
    style.textContent = `
        #cpb-modal-overlay {
            position: fixed; inset: 0;
            background: rgba(0,0,0,0.8);
            z-index: 99999;
            display: flex; align-items: center; justify-content: center;
            font-family: 'Inter', 'Segoe UI', sans-serif;
            backdrop-filter: blur(4px);
        }
        #cpb-modal {
            background: #151520;
            border: 1px solid #333;
            border-radius: 12px;
            width: 800px; max-width: 95vw; height: 600px; max-height: 90vh;
            display: flex; flex-direction: column;
            box-shadow: 0 16px 64px rgba(0,0,0,0.9);
            overflow: hidden;
        }
        #cpb-header {
            padding: 16px 24px;
            background: linear-gradient(to right, #1a1a2e, #2a2a40);
            border-bottom: 1px solid #333;
            display: flex; align-items: center; justify-content: space-between;
        }
        #cpb-title {
            font-size: 16px; font-weight: 600; color: #fff;
            letter-spacing: 0.5px; display: flex; align-items: center; gap: 8px;
        }
        #cpb-close {
            background: none; border: none; color: #888;
            font-size: 20px; cursor: pointer; transition: color 0.2s;
        }
        #cpb-close:hover { color: #fff; }
        
        #cpb-body {
            display: flex; flex: 1; overflow: hidden;
        }
        
        /* Sidebar */
        #cpb-sidebar {
            width: 200px; background: #0f0f16;
            border-right: 1px solid #2a2a35;
            display: flex; flex-direction: column;
            overflow-y: auto; padding: 12px 0;
        }
        .cpb-tab {
            padding: 12px 20px; color: #999;
            font-size: 13px; font-weight: 500;
            cursor: pointer; text-transform: capitalize;
            border-left: 3px solid transparent;
            transition: all 0.2s;
            display: flex; justify-content: space-between; align-items: center;
        }
        .cpb-tab:hover { background: #1a1a25; color: #d0d0e0; }
        .cpb-tab.active {
            background: #1e1e30; color: #fff;
            border-left-color: #667eea;
        }
        .cpb-tab-badge {
            background: #667eea; color: #fff; font-size: 10px;
            padding: 2px 6px; border-radius: 10px;
            display: none;
        }
        .cpb-tab.has-selections .cpb-tab-badge { display: inline-block; }

        /* Main Content */
        #cpb-main {
            flex: 1; display: flex; flex-direction: column;
            background: #181824;
        }
        #cpb-controls {
            padding: 12px 20px; border-bottom: 1px solid #2a2a35;
            display: flex; gap: 12px; align-items: center;
            background: rgba(24, 24, 36, 0.4); backdrop-filter: blur(8px);
            flex-wrap: wrap;
        }
        #cpb-search {
            flex: 1; min-width: 180px; padding: 10px 16px;
            background: #0f0f16; border: 1px solid #333;
            border-radius: 8px; color: #eee; font-size: 13px;
            transition: all 0.2s;
        }
        #cpb-search:focus { outline: none; border-color: #667eea; box-shadow: 0 0 0 2px rgba(102,126,234,0.15); }
        .cpb-btn {
            font-size: 12px; padding: 8px 12px; border-radius: 6px; border: none;
            cursor: pointer; transition: all 0.2s; font-weight: 600;
            white-space: nowrap;
        }
        .cpb-btn-secondary { background: #232330; color: #aaa; border: 1px solid #333; }
        .cpb-btn-secondary:hover { background: #2f2f45; color: #fff; border-color: #555; }
        
        #cpb-show-desc-container {
            display: flex; align-items: center; gap: 8px; font-size: 11px; color: #aaa;
            padding: 0 12px; border-left: 1px solid #333;
            user-select: none; margin-left: auto;
        }
        
        /* Toggle Switch Styling */
        .cpb-switch {
            position: relative; display: inline-block; width: 32px; height: 18px;
        }
        .cpb-switch input { opacity: 0; width: 0; height: 0; }
        .cpb-slider {
            position: absolute; cursor: pointer; inset: 0;
            background-color: #333; transition: .4s; border-radius: 18px;
        }
        .cpb-slider:before {
            position: absolute; content: ""; height: 12px; width: 12px; left: 3px; bottom: 3px;
            background-color: white; transition: .4s; border-radius: 50%;
        }
        input:checked + .cpb-slider { background-color: #667eea; }
        input:checked + .cpb-slider:before { transform: translateX(14px); }
        input:focus + .cpb-slider { box-shadow: 0 0 1px #667eea; }

        #cpb-list {
            flex: 1; overflow-y: auto; padding: 12px 20px;
        }
        
        /* Conditional Toggle Row */
        #cpb-conditional-toggle {
            transition: all 0.3s ease;
        }
        
        /* Items */
        .cpb-item {
            display: flex; align-items: center; gap: 12px;
            padding: 8px 12px; border-radius: 6px;
            margin-bottom: 4px; transition: background 0.15s;
        }
        .cpb-item:hover { background: #222230; }
        .cpb-item.checked { background: #1d1d2d; border-left: 2px solid #667eea; }
        
        .cpb-item-actions {
            display: flex; gap: 4px; margin-left: auto; opacity: 0; transition: opacity 0.2s;
        }
        .cpb-item:hover .cpb-item-actions { opacity: 1; }
        .cpb-action-btn {
            background: none; border: none; cursor: pointer; font-size: 14px; color: #888;
            padding: 4px; border-radius: 4px; transition: all 0.2s; line-height: 1;
        }
        .cpb-action-btn:hover.save-btn { color: #667eea; background: rgba(102,126,234,0.1); }
        .cpb-action-btn:hover.edit-btn { color: #f5a623; background: rgba(245,166,35,0.1); }
        .cpb-action-btn:hover.del-btn { color: #f5222d; background: rgba(245,34,45,0.1); }

        .cpb-item input[type=checkbox] { 
            accent-color: #667eea; width: 16px; height: 16px; 
            cursor: pointer;
        }
        .cpb-item-label {
            font-size: 13px; color: #ddd; flex: 1; cursor: pointer; user-select: none;
        }
        .cpb-item-weight {
            display: flex; align-items: center; gap: 8px;
            opacity: 0; pointer-events: none; transition: opacity 0.2s;
        }
        .cpb-item.checked .cpb-item-weight { opacity: 1; pointer-events: all; }
        .cpb-item.checked .cpb-item-label { color: #fff; font-weight: 500; }
        
        .cpb-weight-range {
            width: 100px; accent-color: #667eea; cursor: pointer;
        }
        .cpb-weight-num {
            font-size: 12px; color: #aaa; width: 32px; text-align: right;
            font-family: monospace;
        }
        
        .cpb-item-label-container {
            flex: 1; pointer-events: none;
        }
        .cpb-item-desc {
            display: block; font-size: 11px; color: #767690; margin-top: 4px;
            font-style: italic; line-height: 1.3;
            max-height: 100px;
            overflow: hidden;
            transition: all 0.2s ease;
        }
        #cpb-list:not(.show-descriptions) .cpb-item-desc {
            display: none;
        }
        .cpb-hidden { display: none !important; }
        
        /* Footer */
        #cpb-footer {
            padding: 16px 24px; background: #0f0f16;
            border-top: 1px solid #2a2a35;
            display: flex; justify-content: space-between; align-items: center;
        }
        #cpb-preview {
            font-size: 12px; color: #888; flex: 1; margin-right: 20px;
            white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        }
        .cpb-btn-primary {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: #fff; padding: 8px 24px; font-weight: 600; font-size: 13px;
            box-shadow: 0 4px 12px rgba(102,126,234,0.3);
        }
        .cpb-btn-primary:hover { opacity: 0.9; transform: translateY(-1px); }
        
        /* Scrollbars */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #333; border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: #555; }
    `;
    document.head.appendChild(style);
}

// ─── Api Calls & Helpers ──────────────────────────────────────────────────
async function fetchTraitOptions(traitName) {
    try {
        const res = await fetch(`/chargenesis/traits/${traitName}`);
        if (!res.ok) return { items: [], descriptions: {} };
        const data = await res.json();
        return { items: data.items || [], descriptions: data.descriptions || {} };
    } catch { return { items: [], descriptions: {} }; }
}

async function mutateTraitOption(traitName, action, value, description = null, oldValue = null) {
    try {
        const res = await fetch(`/chargenesis/traits/${traitName}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action, value, description, old_value: oldValue })
        });
        if (!res.ok) throw new Error("HTTP error");
        const data = await res.json();
        if (data.error) throw new Error(data.error);
        return data; // returns {success:true, items:[]}
    } catch (e) {
        console.error("Failed to mutate trait:", e);
        return null;
    }
}


function parseCurrentValue(text) {
    if (typeof text !== 'string') text = String(text != null ? text : "");
    if (!text || text.trim() === '' || text.trim() === '-') return [];
    return text.split(',').map(entry => {
        const m = entry.trim().match(/^(.+?)\s+(\d+(?:\.\d+)?)\s*$/);
        if (m) return { value: m[1].trim(), weight: parseFloat(m[2]) };
        return { value: entry.trim(), weight: null };
    }).filter(e => e.value);
}

function buildOutputString(selections) {
    const arr = Array.from(selections.entries()).map(([v, w]) => ({value: v, weight: w}));
    if (!arr.length) return '';
    const hasWeights = arr.some(s => s.weight !== null);
    if (!hasWeights) return arr.map(s => s.value).join(', ');
    return arr.map(s => `${s.value}${s.weight !== null ? ' ' + s.weight : ''}`).join(', ');
}

// ─── Unified Modal ────────────────────────────────────────────────────────
async function openUnifiedBrowserModal(node) {
    // Prevent multiple modals
    const existing = document.getElementById('cpb-modal-overlay');
    if (existing) existing.remove();

    // 1. Initialize logic state
    const traits = Object.entries(TRAIT_WIDGETS).map(([wName, tName]) => ({
        widgetName: wName,
        traitName: tName,
        options: [], // populated below
        descriptions: {}, // populated below
        state: new Map() // value -> weight
    }));
    
    let activeTrait = traits[0];

    // Read initial boolean states
    let makeupOnlyFemaleWidget = node.widgets.find(x => x.name === "makeup_only_female");
    let beardOnlyMaleWidget = node.widgets.find(x => x.name === "beard_only_male");
    let makeupOnlyFemale = makeupOnlyFemaleWidget ? makeupOnlyFemaleWidget.value : true;
    let beardOnlyMale = beardOnlyMaleWidget ? beardOnlyMaleWidget.value : true;

    // Read initial strings from node widgets
    traits.forEach(t => {
        const w = node.widgets.find(x => x.name === t.widgetName);
        parseCurrentValue(w ? w.value : "").forEach(s => t.state.set(s.value, s.weight));
    });

    // 2. Build DOM
    const overlay = document.createElement('div');
    overlay.id = 'cpb-modal-overlay';
    overlay.innerHTML = `
        <div id="cpb-modal">
            <div id="cpb-header">
                <div id="cpb-title">✨ High-Fashion Casting Studio</div>
                <button id="cpb-close">✕</button>
            </div>
            <div id="cpb-body">
                <div id="cpb-sidebar"></div>
                <div id="cpb-main">
                    <div id="cpb-controls">
                        <input id="cpb-search" type="text" placeholder="Search parameters..." autocomplete="off"/>
                        <button class="cpb-btn cpb-btn-secondary" id="cpb-select-all">Select All</button>
                        <button class="cpb-btn cpb-btn-secondary" id="cpb-clear-all">Clear Selection</button>
                        <button class="cpb-btn cpb-btn-secondary" id="cpb-equal-weights">Equalize Weights</button>
                        <div id="cpb-show-desc-container">
                             <label class="cpb-switch">
                                <input type="checkbox" id="cpb-toggle-desc" checked />
                                <span class="cpb-slider"></span>
                             </label>
                             <label for="cpb-toggle-desc" style="cursor: pointer;">Descriptions</label>
                        </div>
                    </div>
                    <div id="cpb-conditional-toggle" style="display: none; padding: 12px 16px; background: #222230; border-bottom: 1px solid #333; align-items: center;">
                        <input type="checkbox" id="cpb-conditional-checkbox" style="accent-color: #667eea; width: 16px; height: 16px; cursor: pointer; margin: 0;" />
                        <label for="cpb-conditional-checkbox" id="cpb-conditional-label" style="font-size: 13px; color: #ddd; cursor: pointer; margin-left: 8px; font-weight: 500;"></label>
                    </div>
                    <div id="cpb-list">
                        <div style="padding: 20px; color: #888; text-align: center;">Loading database...</div>
                    </div>
                </div>
            </div>
            <div id="cpb-footer">
                <div id="cpb-preview"></div>
                <div style="display: flex; gap: 12px;">
                    <button class="cpb-btn cpb-btn-secondary" id="cpb-cancel">Cancel</button>
                    <button class="cpb-btn cpb-btn-primary" id="cpb-apply">✓ Apply Traits to Node</button>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(overlay);

    const sidebar = overlay.querySelector('#cpb-sidebar');
    const listEl = overlay.querySelector('#cpb-list');
    const searchEl = overlay.querySelector('#cpb-search');
    const previewEl = overlay.querySelector('#cpb-preview');
    const toggleDescEl = overlay.querySelector('#cpb-toggle-desc');
    
    // Initial sync
    if (toggleDescEl.checked) listEl.classList.add('show-descriptions');
    else listEl.classList.remove('show-descriptions');

    // Fetch all trait options in parallel
    await Promise.all(traits.map(async t => {
        const data = await fetchTraitOptions(t.traitName);
        t.options = data.items;
        t.descriptions = data.descriptions;
    }));

    // ─── Render functions ───
    function renderSidebar() {
        sidebar.innerHTML = '';
        traits.forEach(t => {
            const count = t.state.size;
            const tab = document.createElement('div');
            tab.className = `cpb-tab ${t === activeTrait ? 'active' : ''} ${count > 0 ? 'has-selections' : ''}`;
            tab.innerHTML = `
                <span>${t.widgetName.replace(/_/g, ' ')}</span>
                <span class="cpb-tab-badge">${count}</span>
            `;
            tab.addEventListener('click', () => {
                activeTrait = t;
                searchEl.value = '';
                renderSidebar();
                renderList();
                updateConditionalToggle();
            });
            sidebar.appendChild(tab);
        });
        updatePreview();
    }

    function renderList(filter = '') {
        listEl.innerHTML = '';
        const t = activeTrait;
        
        let filtered = filter 
            ? t.options.filter(o => o.toLowerCase().includes(filter.toLowerCase()))
            : t.options;
            
        // Allow adding custom value if it isn't in list
        if (filter && !filtered.some(o => o.toLowerCase() === filter.toLowerCase())) {
            filtered.unshift(filter.trim());
        }

        if (filtered.length === 0) {
            listEl.innerHTML = `<div style="padding: 20px; color: #666; text-align: center;">No options found. Type to add a custom value.</div>`;
            return;
        }

        filtered.forEach(opt => {
            const isChecked = t.state.has(opt);
            const weight = t.state.get(opt) ?? 50;
            const item = document.createElement('div');
            item.className = `cpb-item ${isChecked ? 'checked' : ''}`;
            
            const isCustom = !t.options.includes(opt);
            const allowsEdit = t.traitName !== 'bone_structure';
            let actionsHTML = '';
            
            if (allowsEdit && opt !== '') {
                actionsHTML = `
                    <div class="cpb-item-actions">
                        ${isCustom 
                            ? `<button class="cpb-action-btn save-btn" title="Save to Database">💾</button>`
                            : `<button class="cpb-action-btn edit-btn" title="Edit Option">✏️</button>
                               <button class="cpb-action-btn del-btn" title="Delete Option">🗑️</button>`
                        }
                    </div>
                `;
            }

            const desc = t.descriptions[opt] || "";
            
            item.innerHTML = `
                <input type="checkbox" ${isChecked ? 'checked' : ''} />
                <div class="cpb-item-label-container" style="pointer-events: none;">
                    <label class="cpb-item-label" style="pointer-events: all; cursor: pointer;">${opt}</label>
                    <span class="cpb-item-desc ${!desc ? 'cpb-hidden' : ''}">${desc}</span>
                </div>
                <div class="cpb-item-weight">
                    <input type="range" class="cpb-weight-range" min="1" max="100" value="${weight}" />
                    <span class="cpb-weight-num">${weight}</span>
                </div>
                ${actionsHTML}
            `;

            const cb = item.querySelector('input[type=checkbox]');
            const range = item.querySelector('.cpb-weight-range');
            const numEl = item.querySelector('.cpb-weight-num');

            cb.addEventListener('change', () => {
                if (cb.checked) {
                    t.state.set(opt, parseInt(range.value));
                    item.classList.add('checked');
                } else {
                    t.state.delete(opt);
                    item.classList.remove('checked');
                }
                renderSidebar(); // update badges
            });

            range.addEventListener('input', () => {
                numEl.textContent = range.value;
                if (t.state.has(opt)) t.state.set(opt, parseInt(range.value));
                updatePreview();
            });

            item.querySelector('.cpb-item-label').addEventListener('click', () => {
                cb.checked = !cb.checked;
                cb.dispatchEvent(new Event('change'));
            });

            if (allowsEdit) {
                const saveBtn = item.querySelector('.save-btn');
                const editBtn = item.querySelector('.edit-btn');
                const delBtn = item.querySelector('.del-btn');
                
                if (saveBtn) {
                    saveBtn.addEventListener('click', async (e) => {
                        e.stopPropagation();
                        const desc = prompt(`Provide a professional industry-standard description for "${opt}":`, "");
                        
                        // Check it when it gets saved
                        if (!cb.checked) {
                            cb.checked = true; cb.dispatchEvent(new Event('change'));
                        }
                        saveBtn.innerHTML = "⌛";
                        const result = await mutateTraitOption(t.traitName, 'add', opt, desc);
                        if (result?.success) {
                            // Refresh from backend to get descriptions too
                            const updated = await fetchTraitOptions(t.traitName);
                            t.options = updated.items;
                            t.descriptions = updated.descriptions;
                            renderList(searchEl.value);
                        } else {
                            alert("Failed to save option. Check console.");
                            saveBtn.innerHTML = "💾";
                        }
                    });
                }
                if (editBtn) {
                    editBtn.addEventListener('click', async (e) => {
                        e.stopPropagation();
                        // 1. Edit Name
                        const newName = prompt("Edit trait name:", opt);
                        if (!newName || newName.trim() === '') return;
                        
                        // 2. Edit Description
                        const oldDesc = t.descriptions[opt] || "";
                        const newDesc = prompt(`Edit professional description for "${newName.trim()}":`, oldDesc);
                        
                        if ((newName.trim() !== opt) || (newDesc !== oldDesc)) {
                            const trimmedName = newName.trim();
                            const result = await mutateTraitOption(t.traitName, 'edit', trimmedName, newDesc, opt);
                            if (result?.success) {
                                // Refresh weights if name changed
                                if (trimmedName !== opt) {
                                    if (t.state.has(opt)) {
                                        const w = t.state.get(opt);
                                        t.state.delete(opt);
                                        t.state.set(trimmedName, w);
                                    }
                                }
                                // Full refresh from backend
                                const updated = await fetchTraitOptions(t.traitName);
                                t.options = updated.items;
                                t.descriptions = updated.descriptions;
                                
                                renderSidebar();
                                renderList(searchEl.value);
                            } else {
                                alert("Failed to edit option. Check console.");
                            }
                        }
                    });
                }
                if (delBtn) {
                    delBtn.addEventListener('click', async (e) => {
                        e.stopPropagation();
                        if (confirm(`Are you sure you want to delete "${opt}" from the database permanently?`)) {
                            const result = await mutateTraitOption(t.traitName, 'delete', opt);
                            if (result?.success) {
                                const updated = await fetchTraitOptions(t.traitName);
                                t.options = updated.items;
                                t.descriptions = updated.descriptions;
                                t.state.delete(opt);
                                renderSidebar();
                                renderList(searchEl.value);
                            } else {
                                alert("Failed to delete option. Check console.");
                            }
                        }
                    });
                }

            }

            listEl.appendChild(item);
        });
        
        // Scroll list to top
        listEl.scrollTop = 0;
    }

    function updatePreview() {
        const out = buildOutputString(activeTrait.state);
        previewEl.innerHTML = `<b style="color:#fff">${activeTrait.widgetName}:</b> ${out || '<span style="color:#555">(empty)</span>'}`;
    }

    function updateConditionalToggle() {
        const condToggle = overlay.querySelector('#cpb-conditional-toggle');
        const condCheck = overlay.querySelector('#cpb-conditional-checkbox');
        const condLabel = overlay.querySelector('#cpb-conditional-label');
        if (!condToggle) return;
        
        if (activeTrait.traitName === 'beard' || activeTrait.traitName === 'beard_color') {
            condToggle.style.display = 'flex';
            condLabel.textContent = "Aplicar barba solamente cuando el personaje es masculino";
            condCheck.checked = beardOnlyMale;
            condCheck.onchange = (e) => { beardOnlyMale = e.target.checked; };
        } else if (activeTrait.traitName === 'makeup' || activeTrait.traitName === 'makeup_color') {
            condToggle.style.display = 'flex';
            condLabel.textContent = "Aplicar maquillaje solamente cuando el personaje es femenino";
            condCheck.checked = makeupOnlyFemale;
            condCheck.onchange = (e) => { makeupOnlyFemale = e.target.checked; };
        } else {
            condToggle.style.display = 'none';
        }
    }

    // ─── Initial Render ───
    renderSidebar();
    renderList();
    updateConditionalToggle();
    setTimeout(() => searchEl.focus(), 50);

    // ─── Events ───
    searchEl.addEventListener('input', () => renderList(searchEl.value));
    
    toggleDescEl.addEventListener('change', () => {
        if (toggleDescEl.checked) listEl.classList.add('show-descriptions');
        else listEl.classList.remove('show-descriptions');
    });

    overlay.querySelector('#cpb-select-all').addEventListener('click', () => {
        const filter = searchEl.value.toLowerCase();
        const t = activeTrait;
        const visible = filter 
            ? t.options.filter(o => o.toLowerCase().includes(filter))
            : t.options;
        
        visible.forEach(opt => {
            if (!t.state.has(opt)) t.state.set(opt, 50);
        });
        
        renderSidebar();
        renderList(searchEl.value);
    });

    overlay.querySelector('#cpb-clear-all').addEventListener('click', () => {
        activeTrait.state.clear();
        renderSidebar();
        renderList(searchEl.value);
    });

    overlay.querySelector('#cpb-equal-weights').addEventListener('click', () => {
        activeTrait.state.forEach((w, v) => activeTrait.state.set(v, null));
        renderList(searchEl.value);
        updatePreview();
    });

    const close = () => overlay.remove();
    overlay.querySelector('#cpb-close').addEventListener('click', close);
    overlay.querySelector('#cpb-cancel').addEventListener('click', close);
    overlay.addEventListener('mousedown', e => { if(e.target === overlay) close(); });

    // Apply saves everything back to the node widgets
    overlay.querySelector('#cpb-apply').addEventListener('click', () => {
        if (beardOnlyMaleWidget) beardOnlyMaleWidget.value = beardOnlyMale;
        if (makeupOnlyFemaleWidget) makeupOnlyFemaleWidget.value = makeupOnlyFemale;
        
        traits.forEach(t => {
            const w = node.widgets.find(x => x.name === t.widgetName);
            if (w) {
                const newVal = buildOutputString(t.state);
                w.value = newVal;
                if (w.callback) w.callback(newVal); // trigger any updates
            }
        });
        app.graph.setDirtyCanvas(true, true);
        close();
    });
}

// ─── Entry Point ──────────────────────────────────────────────────────────
function injectUniversalButton(node) {
    if (node.__cpbBrowserConfigured) return;
    node.__cpbBrowserConfigured = true;

    // Add a single standard LiteGraph button to the node
    const btnUrl = node.addWidget("button", "✨ High-Fashion Casting Studio", "browse", () => {
        openUnifiedBrowserModal(node);
    });
    
    // Optional: Move it to the very top conceptually
    setTimeout(() => {
        const idx = node.widgets.indexOf(btnUrl);
        if (idx !== -1 && node.widgets.length > 1) {
            node.widgets.splice(idx, 1);
            node.widgets.unshift(btnUrl);
            node.setSize(node.computeSize());
        }
    }, 50);
}

app.registerExtension({
    name: "AIWizArt.CharacterGenesisNode",
    async nodeCreated(node) {
        if (node.comfyClass === "CharacterGenesisNode") {
            injectUniversalButton(node);
        }
    }
});
