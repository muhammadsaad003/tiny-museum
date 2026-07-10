const state = {
  objects: [],
  stats: null,
  editingId: null,
  favoriteOnly: false,
  searchTimer: null
}

const elements = {
  grid: document.querySelector("#object-grid"),
  empty: document.querySelector("#empty-state"),
  emptyTitle: document.querySelector("#empty-title"),
  emptyCopy: document.querySelector("#empty-copy"),
  resultCount: document.querySelector("#result-count"),
  search: document.querySelector("#search"),
  room: document.querySelector("#filter-room"),
  mood: document.querySelector("#filter-mood"),
  sort: document.querySelector("#sort"),
  favoriteFilter: document.querySelector("#favorite-filter"),
  modal: document.querySelector("#object-modal"),
  form: document.querySelector("#object-form"),
  modalTitle: document.querySelector("#modal-title"),
  saveButton: document.querySelector("#save-object"),
  toast: document.querySelector("#toast"),
  exhibitForm: document.querySelector("#exhibit-form"),
  exhibitTheme: document.querySelector("#exhibit-theme"),
  exhibitCount: document.querySelector("#exhibit-count"),
  rangeOutput: document.querySelector("#range-output"),
  exhibitOutput: document.querySelector("#exhibit-output"),
  exhibitTitle: document.querySelector("#exhibit-title"),
  exhibitNote: document.querySelector("#exhibit-note"),
  exhibitList: document.querySelector("#exhibit-list"),
  pulseBars: document.querySelector("#pulse-bars"),
  pulseLabel: document.querySelector("#pulse-label")
}

const colorMap = {
  blue: "#5f83a2",
  red: "#aa5d50",
  orange: "#c9854e",
  yellow: "#d0af57",
  green: "#718a6e",
  purple: "#806f92",
  pink: "#bc7f8b",
  black: "#3c403e",
  white: "#d8d5cd",
  silver: "#9aa3a0",
  gold: "#b88a45",
  brown: "#8b684c",
  charcoal: "#59615e",
  terracotta: "#b8674f",
  natural: "#a48863",
  unspecified: "#9b9b8f"
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options
  })
  if (!response.ok) {
    let message = "Something went wrong"
    try {
      const data = await response.json()
      message = data.detail || message
    } catch {
      message = response.statusText || message
    }
    throw new Error(message)
  }
  if (response.status === 204) return null
  return response.json()
}

function escapeHTML(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;")
}

function showToast(message) {
  elements.toast.textContent = message
  elements.toast.classList.add("visible")
  window.clearTimeout(showToast.timer)
  showToast.timer = window.setTimeout(() => elements.toast.classList.remove("visible"), 2600)
}

function buildQuery() {
  const params = new URLSearchParams()
  const q = elements.search.value.trim()
  if (q) params.set("q", q)
  if (elements.room.value) params.set("room", elements.room.value)
  if (elements.mood.value) params.set("mood", elements.mood.value)
  if (state.favoriteOnly) params.set("favorite", "true")
  params.set("sort", elements.sort.value)
  return params.toString()
}

async function loadObjects() {
  try {
    state.objects = await api(`/api/objects?${buildQuery()}`)
    renderObjects()
  } catch (error) {
    showToast(error.message)
  }
}

async function loadStats() {
  try {
    state.stats = await api("/api/stats")
    renderStats()
  } catch (error) {
    showToast(error.message)
  }
}

async function loadFilterOptions() {
  try {
    const allObjects = await api("/api/objects?sort=name")
    fillSelect(elements.room, "All rooms", [...new Set(allObjects.map(item => item.room))])
    fillSelect(elements.mood, "All moods", [...new Set(allObjects.map(item => item.mood))])
  } catch (error) {
    showToast(error.message)
  }
}

function fillSelect(select, firstLabel, values) {
  const current = select.value
  select.innerHTML = `<option value="">${escapeHTML(firstLabel)}</option>`
  values.sort((a, b) => a.localeCompare(b)).forEach(value => {
    const option = document.createElement("option")
    option.value = value
    option.textContent = value
    select.append(option)
  })
  if (values.includes(current)) select.value = current
}

function renderStats() {
  if (!state.stats) return
  document.querySelector("#stat-total").textContent = state.stats.total
  document.querySelector("#stat-favorites").textContent = state.stats.favorites
  document.querySelector("#stat-significance").textContent = state.stats.average_significance.toFixed(1)
  document.querySelector("#stat-oldest").textContent = state.stats.oldest_acquired_year || "—"
  renderPulse()
}

function renderPulse() {
  const entries = Object.entries(state.stats?.by_mood || {}).sort((a, b) => b[1] - a[1]).slice(0, 4)
  elements.pulseBars.innerHTML = ""
  if (!entries.length) {
    elements.pulseLabel.textContent = "No data yet"
    return
  }
  const maximum = Math.max(...entries.map(entry => entry[1]))
  elements.pulseLabel.textContent = entries[0][0]
  entries.forEach(([label, count]) => {
    const row = document.createElement("div")
    row.className = "pulse-row"
    row.innerHTML = `
      <span>${escapeHTML(label)}</span>
      <div class="pulse-track"><div class="pulse-fill" style="width:${Math.max(8, count / maximum * 100)}%"></div></div>
      <b>${count}</b>
    `
    elements.pulseBars.append(row)
  })
}

function renderObjects() {
  elements.grid.innerHTML = ""
  const count = state.objects.length
  elements.resultCount.textContent = `${count} ${count === 1 ? "object" : "objects"}`
  if (!count) {
    elements.empty.hidden = false
    elements.grid.hidden = true
    const filtering = elements.search.value || elements.room.value || elements.mood.value || state.favoriteOnly
    elements.emptyTitle.textContent = filtering ? "No objects match this view" : "The gallery is waiting"
    elements.emptyCopy.textContent = filtering
      ? "Try a different search or clear one of the filters."
      : "Add an object with a story, or load a small demonstration collection."
    return
  }
  elements.empty.hidden = true
  elements.grid.hidden = false
  state.objects.forEach((item, index) => elements.grid.append(createObjectCard(item, index)))
}

function createObjectCard(item, index) {
  const card = document.createElement("article")
  card.className = "object-card"
  card.style.setProperty("--object-color", resolveColor(item.color))
  const ageText = item.estimated_age === null ? "Age unknown" : `${item.estimated_age} ${item.estimated_age === 1 ? "year" : "years"} old`
  const acquiredText = item.acquired_year ? `Acquired ${item.acquired_year}` : "Arrival unknown"
  const dots = Array.from({ length: 5 }, (_, dot) => `<i class="${dot < item.significance ? "active" : ""}"></i>`).join("")
  card.innerHTML = `
    <div class="object-top">
      <span class="object-index">${String(index + 1).padStart(2, "0")}</span>
      <div class="card-actions">
        <button class="card-icon ${item.favorite ? "favorite-active" : ""}" data-action="favorite" type="button" aria-label="${item.favorite ? "Remove from" : "Add to"} favorites">${item.favorite ? "♥" : "♡"}</button>
        <button class="card-icon" data-action="edit" type="button" aria-label="Edit object">✎</button>
        <button class="card-icon" data-action="delete" type="button" aria-label="Delete object">×</button>
      </div>
    </div>
    <h3>${escapeHTML(item.name)}</h3>
    <p class="object-story">${escapeHTML(item.story)}</p>
    <div class="object-tags">
      <span>${escapeHTML(item.room)}</span>
      <span>${escapeHTML(item.material)}</span>
      <span>${escapeHTML(item.mood)}</span>
    </div>
    <div class="object-footer">
      <span>${escapeHTML(acquiredText)} · ${escapeHTML(ageText)}</span>
      <span class="significance-dots" title="Significance ${item.significance} out of 5">${dots}</span>
    </div>
  `
  card.querySelector('[data-action="favorite"]').addEventListener("click", () => toggleFavorite(item))
  card.querySelector('[data-action="edit"]').addEventListener("click", () => openModal(item))
  card.querySelector('[data-action="delete"]').addEventListener("click", () => deleteObject(item))
  return card
}

function resolveColor(color) {
  const normalized = String(color || "unspecified").toLowerCase()
  const direct = colorMap[normalized]
  if (direct) return direct
  const match = Object.keys(colorMap).find(key => normalized.includes(key))
  return colorMap[match] || colorMap.unspecified
}

function openModal(item = null) {
  state.editingId = item?.id || null
  elements.form.reset()
  elements.form.elements.color.value = "Unspecified"
  elements.form.elements.significance.value = "3"
  elements.modalTitle.textContent = item ? "Edit collection record" : "Catalog an object"
  elements.saveButton.textContent = item ? "Update object" : "Save object"
  if (item) {
    const fields = ["name", "story", "room", "material", "mood", "color", "acquired_year", "estimated_age"]
    fields.forEach(field => {
      elements.form.elements[field].value = item[field] ?? ""
    })
    elements.form.elements.significance.value = String(item.significance)
    elements.form.elements.favorite.checked = item.favorite
  }
  elements.modal.showModal()
  window.setTimeout(() => elements.form.elements.name.focus(), 50)
}

function closeModal() {
  elements.modal.close()
  state.editingId = null
}

function formPayload() {
  const data = new FormData(elements.form)
  return {
    name: String(data.get("name") || "").trim(),
    story: String(data.get("story") || "").trim(),
    room: String(data.get("room") || "").trim(),
    material: String(data.get("material") || "").trim(),
    mood: String(data.get("mood") || "").trim(),
    color: String(data.get("color") || "Unspecified").trim(),
    acquired_year: data.get("acquired_year") ? Number(data.get("acquired_year")) : null,
    estimated_age: data.get("estimated_age") ? Number(data.get("estimated_age")) : null,
    significance: Number(data.get("significance") || 3),
    favorite: data.get("favorite") === "on"
  }
}

async function saveObject(event) {
  event.preventDefault()
  if (!elements.form.reportValidity()) return
  elements.saveButton.disabled = true
  try {
    const editing = Boolean(state.editingId)
    await api(editing ? `/api/objects/${state.editingId}` : "/api/objects", {
      method: editing ? "PUT" : "POST",
      body: JSON.stringify(formPayload())
    })
    closeModal()
    await refreshAll()
    showToast(editing ? "Object record updated" : "Object added to the museum")
  } catch (error) {
    showToast(error.message)
  } finally {
    elements.saveButton.disabled = false
  }
}

async function toggleFavorite(item) {
  try {
    await api(`/api/objects/${item.id}/favorite`, {
      method: "PATCH",
      body: JSON.stringify({ favorite: !item.favorite })
    })
    await refreshAll()
    showToast(item.favorite ? "Removed from favorites" : "Added to favorites")
  } catch (error) {
    showToast(error.message)
  }
}

async function deleteObject(item) {
  const accepted = window.confirm(`Remove “${item.name}” from the museum?`)
  if (!accepted) return
  try {
    await api(`/api/objects/${item.id}`, { method: "DELETE" })
    await refreshAll()
    showToast("Object removed")
  } catch (error) {
    showToast(error.message)
  }
}

async function seedDemo() {
  try {
    const result = await api("/api/demo/seed", { method: "POST", body: "{}" })
    await refreshAll()
    showToast(result.added ? `${result.added} demo objects added` : "The collection already contains objects")
  } catch (error) {
    showToast(error.message)
  }
}

async function generateExhibit(event) {
  event?.preventDefault()
  try {
    const exhibit = await api("/api/exhibitions/generate", {
      method: "POST",
      body: JSON.stringify({
        theme: elements.exhibitTheme.value.trim() || null,
        count: Number(elements.exhibitCount.value)
      })
    })
    elements.exhibitTitle.textContent = exhibit.title
    elements.exhibitNote.textContent = exhibit.curatorial_note
    elements.exhibitList.innerHTML = ""
    exhibit.objects.forEach(item => {
      const row = document.createElement("div")
      row.className = "exhibit-item"
      row.innerHTML = `<span></span><strong>${escapeHTML(item.name)}</strong>`
      elements.exhibitList.append(row)
    })
    elements.exhibitOutput.hidden = false
    elements.exhibitOutput.scrollIntoView({ behavior: "smooth", block: "nearest" })
  } catch (error) {
    showToast(error.message)
  }
}

async function refreshAll() {
  await Promise.all([loadObjects(), loadStats(), loadFilterOptions()])
}

function wireEvents() {
  document.querySelector("#open-create").addEventListener("click", () => openModal())
  document.querySelector("#hero-create").addEventListener("click", () => openModal())
  document.querySelector("#empty-create").addEventListener("click", () => openModal())
  document.querySelector("#close-modal").addEventListener("click", closeModal)
  document.querySelector("#cancel-modal").addEventListener("click", closeModal)
  document.querySelector("#seed-demo").addEventListener("click", seedDemo)
  document.querySelector("#hero-exhibit").addEventListener("click", () => {
    document.querySelector(".curator-panel").scrollIntoView({ behavior: "smooth", block: "start" })
    window.setTimeout(() => elements.exhibitTheme.focus(), 500)
  })
  elements.form.addEventListener("submit", saveObject)
  elements.exhibitForm.addEventListener("submit", generateExhibit)
  elements.exhibitCount.addEventListener("input", () => {
    elements.rangeOutput.textContent = elements.exhibitCount.value
  })
  elements.search.addEventListener("input", () => {
    window.clearTimeout(state.searchTimer)
    state.searchTimer = window.setTimeout(loadObjects, 240)
  })
  ;[elements.room, elements.mood, elements.sort].forEach(element => element.addEventListener("change", loadObjects))
  elements.favoriteFilter.addEventListener("click", () => {
    state.favoriteOnly = !state.favoriteOnly
    elements.favoriteFilter.setAttribute("aria-pressed", String(state.favoriteOnly))
    loadObjects()
  })
  elements.modal.addEventListener("click", event => {
    const bounds = elements.modal.getBoundingClientRect()
    const outside = event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom
    if (outside) closeModal()
  })
}

async function start() {
  wireEvents()
  await refreshAll()
}

start()
