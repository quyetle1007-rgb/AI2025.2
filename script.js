const state = {
  grid: [],
  originalGrid: [],
  start: [0, 0],
  goal: [0, 0],
  tool: 'wall',
  mouseDown: false,
  running: false,
};

const gridBoard = document.getElementById('gridBoard');
const mapSelect = document.getElementById('mapSelect');
const algorithmSelect = document.getElementById('algorithmSelect');
const statusText = document.getElementById('statusText');
const statFound = document.getElementById('statFound');
const statCost = document.getElementById('statCost');
const statExpanded = document.getElementById('statExpanded');
const statRuntime = document.getElementById('statRuntime');

function cloneGrid(grid) {
  return grid.map((row) => [...row]);
}

function setStatus(message) {
  statusText.textContent = message;
}

function setStats(result = null) {
  if (!result) {
    statFound.textContent = '-';
    statCost.textContent = '-';
    statExpanded.textContent = '-';
    statRuntime.textContent = '-';
    return;
  }
  statFound.textContent = result.found ? 'Yes' : 'No';
  statCost.textContent = result.found ? String(result.path_cost) : 'No path';
  statExpanded.textContent = String(result.expanded_nodes);
  statRuntime.textContent = `${result.runtime_ms.toFixed(3)} ms`;
}

function syncButtons(enabled) {
  document.querySelectorAll('button, select').forEach((el) => {
    if (el.id === 'algorithmSelect' || el.id === 'mapSelect') {
      el.disabled = !enabled;
    } else if (el.tagName === 'BUTTON') {
      el.disabled = !enabled;
    }
  });
  state.running = !enabled;
}

function drawGrid(visited = new Set(), path = new Set()) {
  if (!state.grid.length) return;
  const rows = state.grid.length;
  const cols = state.grid[0].length;
  gridBoard.style.gridTemplateColumns = `repeat(${cols}, 32px)`;
  gridBoard.innerHTML = '';

  for (let r = 0; r < rows; r += 1) {
    for (let c = 0; c < cols; c += 1) {
      const key = `${r},${c}`;
      const cell = document.createElement('div');
      cell.className = 'cell';
      cell.dataset.row = String(r);
      cell.dataset.col = String(c);

      if (state.grid[r][c] === 1) cell.classList.add('wall');
      if (visited.has(key)) cell.classList.add('visited');
      if (path.has(key)) cell.classList.add('path');
      if (state.start[0] === r && state.start[1] === c) {
        cell.classList.add('start');
        cell.textContent = 'S';
      } else if (state.goal[0] === r && state.goal[1] === c) {
        cell.classList.add('goal');
        cell.textContent = 'G';
      }

      cell.addEventListener('mousedown', () => handleCellPaint(r, c));
      cell.addEventListener('mouseenter', () => {
        if (state.mouseDown && (state.tool === 'wall' || state.tool === 'erase')) {
          handleCellPaint(r, c);
        }
      });
      gridBoard.appendChild(cell);
    }
  }
}

function handleCellPaint(r, c) {
  if (state.running) return;
  const isStart = state.start[0] === r && state.start[1] === c;
  const isGoal = state.goal[0] === r && state.goal[1] === c;

  if (state.tool === 'wall') {
    if (!isStart && !isGoal) state.grid[r][c] = 1;
  } else if (state.tool === 'erase') {
    state.grid[r][c] = 0;
  } else if (state.tool === 'start') {
    if (!isGoal && state.grid[r][c] === 0) state.start = [r, c];
  } else if (state.tool === 'goal') {
    if (!isStart && state.grid[r][c] === 0) state.goal = [r, c];
  }
  drawGrid();
}

function activateTool(tool) {
  state.tool = tool;
  document.querySelectorAll('.tool').forEach((btn) => {
    btn.classList.toggle('active', btn.dataset.tool === tool);
  });
}

async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || 'Request failed');
  }
  return data;
}

async function loadMapList() {
  const data = await fetchJson('/api/maps');
  mapSelect.innerHTML = '';
  data.maps.forEach((name) => {
    const option = document.createElement('option');
    option.value = name;
    option.textContent = name;
    mapSelect.appendChild(option);
  });
}

async function loadMap(name) {
  const data = await fetchJson(`/api/map/${encodeURIComponent(name)}`);
  state.grid = cloneGrid(data.grid);
  state.originalGrid = cloneGrid(data.grid);
  state.start = [...data.start];
  state.goal = [...data.goal];
  setStats();
  setStatus(`Loaded ${name}.`);
  drawGrid();
}

function resetColors() {
  drawGrid();
  setStatus('Grid colors reset.');
}

function clearWalls() {
  state.grid = state.grid.map((row, r) => row.map((_, c) => ((state.start[0] === r && state.start[1] === c) || (state.goal[0] === r && state.goal[1] === c) ? 0 : 0)));
  drawGrid();
  setStatus('All obstacles cleared.');
}

function randomWalls() {
  const rows = state.grid.length;
  const cols = state.grid[0].length;
  for (let r = 0; r < rows; r += 1) {
    for (let c = 0; c < cols; c += 1) {
      const isStart = state.start[0] === r && state.start[1] === c;
      const isGoal = state.goal[0] === r && state.goal[1] === c;
      state.grid[r][c] = (!isStart && !isGoal && Math.random() < 0.22) ? 1 : 0;
    }
  }
  drawGrid();
  setStatus('Random obstacles generated.');
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function animateResult(result) {
  const visited = new Set();
  const path = new Set();

  for (let i = 0; i < result.visited_order.length; i += 1) {
    const [r, c] = result.visited_order[i];
    visited.add(`${r},${c}`);
    drawGrid(visited, path);
    await sleep(18);
  }

  result.path.forEach(([r, c]) => path.add(`${r},${c}`));
  drawGrid(visited, path);
}

async function runSearch() {
  syncButtons(false);
  setStatus(`Running ${algorithmSelect.value}...`);
  setStats();
  drawGrid();

  try {
    const result = await fetchJson('/api/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        algorithm: algorithmSelect.value,
        grid: state.grid,
        start: state.start,
        goal: state.goal,
      }),
    });

    setStats(result);
    await animateResult(result);
    setStatus(result.found
      ? `${result.algorithm} finished. Path found.`
      : `${result.algorithm} finished. No path found.`);
  } catch (error) {
    setStatus(error.message);
    alert(error.message);
  } finally {
    syncButtons(true);
  }
}

window.addEventListener('mouseup', () => {
  state.mouseDown = false;
});

gridBoard.addEventListener('mousedown', () => {
  state.mouseDown = true;
});

document.getElementById('loadMapBtn').addEventListener('click', () => loadMap(mapSelect.value));
document.getElementById('runBtn').addEventListener('click', runSearch);
document.getElementById('resetBtn').addEventListener('click', resetColors);
document.getElementById('clearWallsBtn').addEventListener('click', clearWalls);
document.getElementById('randomBtn').addEventListener('click', randomWalls);

document.querySelectorAll('.tool').forEach((btn) => {
  btn.addEventListener('click', () => activateTool(btn.dataset.tool));
});

(async function init() {
  try {
    await loadMapList();
    if (mapSelect.options.length > 0) {
      await loadMap(mapSelect.value);
    }
    activateTool('wall');
    setStatus('Ready. Edit the grid or run a search.');
  } catch (error) {
    setStatus(error.message);
  }
})();
