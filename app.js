/**
 * Holiday Hacker — Progressive Web App Logic & Optimizer Engine
 */

// 1. Comprehensive 2026 & 2027 Public Holidays Dataset
const ALL_PUBLIC_HOLIDAYS = [
  // 2026
  { name: "New Year's Day", date: "2026-01-01", desc: "First day of the year" },
  { name: "Republic Day", date: "2026-01-26", desc: "National Holiday - Republic Day" },
  { name: "Maha Shivratri", date: "2026-02-17", desc: "Festival of Lord Shiva" },
  { name: "Holi", date: "2026-03-04", desc: "Festival of Colors" },
  { name: "Good Friday", date: "2026-04-03", desc: "Christian Holiday" },
  { name: "Easter Sunday", date: "2026-04-05", desc: "Easter Celebration" },
  { name: "Eid al-Fitr", date: "2026-04-20", desc: "Islamic Festival" },
  { name: "May Day / Labor Day", date: "2026-05-01", desc: "International Workers' Day" },
  { name: "Bakrid / Eid al-Adha", date: "2026-05-27", desc: "Feast of Sacrifice" },
  { name: "Muharram", date: "2026-06-26", desc: "Islamic New Year" },
  { name: "Independence Day", date: "2026-08-15", desc: "National Independence Day" },
  { name: "Raksha Bandhan", date: "2026-08-28", desc: "Festival of Siblings" },
  { name: "Janmashtami", date: "2026-09-04", desc: "Birth of Lord Krishna" },
  { name: "Milad-un-Nabi", date: "2026-09-05", desc: "Prophet's Birthday" },
  { name: "Mahatma Gandhi Jayanti", date: "2026-10-02", desc: "Father of the Nation Birthday" },
  { name: "Dussehra", date: "2026-10-20", desc: "Victory of Good over Evil" },
  { name: "Diwali / Deepavali", date: "2026-11-08", desc: "Festival of Lights" },
  { name: "Guru Nanak Jayanti", date: "2026-11-24", desc: "Birth of Guru Nanak" },
  { name: "Christmas Day", date: "2026-12-25", desc: "Christmas Celebration" },
  // 2027
  { name: "New Year's Day", date: "2027-01-01", desc: "First day of 2027" },
  { name: "Republic Day", date: "2027-01-26", desc: "Republic Day 2027" },
  { name: "Maha Shivratri", date: "2027-03-08", desc: "Festival of Lord Shiva 2027" },
  { name: "Holi", date: "2027-03-23", desc: "Festival of Colors 2027" },
  { name: "Good Friday", date: "2027-03-26", desc: "Good Friday 2027" },
  { name: "Eid al-Fitr", date: "2027-04-10", desc: "Islamic Festival 2027" },
  { name: "May Day", date: "2027-05-01", desc: "Labor Day 2027" },
  { name: "Independence Day", date: "2027-08-15", desc: "Independence Day 2027" },
  { name: "Gandhi Jayanti", date: "2027-10-02", desc: "Gandhi Jayanti 2027" },
  { name: "Dussehra", date: "2027-10-09", desc: "Dussehra 2027" },
  { name: "Diwali", date: "2027-10-29", desc: "Diwali 2027" },
  { name: "Christmas Day", date: "2027-12-25", desc: "Christmas 2027" }
];

const SUCCESS_QUOTES = [
  "Congratulations! You legally hacked your calendar. 😎",
  "Productivity has left the chat. 😂",
  "Elite Holiday Hacker detected. 🏆",
  "Your boss will never know. 🤫",
  "Maximum chill achieved. 🧊",
  "This is the way. 🚀",
  "HR wants to know your location. 📍"
];

// Helper: Format Date String YYYY-MM-DD
function formatDate(d) {
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function parseDate(str) {
  const [y, m, d] = str.split('-').map(Number);
  return new Date(y, m - 1, d);
}

function formatPrettyDate(str) {
  const d = parseDate(str);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

// 2. Core State - Automatically defaults to CURRENT real date
const State = {
  totalLeaves: 10,
  bookedLeaves: JSON.parse(localStorage.getItem('hh_booked_leaves') || '[]'),
  savedPlans: JSON.parse(localStorage.getItem('hh_saved_plans') || '[]'),
  currentMonth: new Date(), // Always defaults to TODAY'S real month & year!
  currentScope: 'month', // 'month' (default), 'next_month', 'quarter', 'year'
  currentBudgetFilter: 'all',
  deferredInstallPrompt: null
};

// 3. Holiday Optimizer Algorithm (Sliding Window Strategy)
class HolidayOptimizer {
  constructor(holidays = ALL_PUBLIC_HOLIDAYS) {
    this.holidayMap = new Map();
    holidays.forEach(h => this.holidayMap.set(h.date, h.name));
  }

  buildCalendar(startDate, endDate, bookedLeavesSet) {
    const days = [];
    const curr = new Date(startDate);
    while (curr <= endDate) {
      const dateStr = formatDate(curr);
      const dayOfWeek = curr.getDay(); // 0 = Sun, 6 = Sat
      const isWeekend = (dayOfWeek === 0 || dayOfWeek === 6);
      const isHoliday = this.holidayMap.has(dateStr);
      const isBookedLeave = bookedLeavesSet.has(dateStr);

      let status = 'working';
      let label = null;

      if (isWeekend) {
        status = 'weekend';
        label = 'Weekend';
      } else if (isHoliday) {
        status = 'holiday';
        label = this.holidayMap.get(dateStr);
      } else if (isBookedLeave) {
        status = 'booked_leave';
        label = 'Booked Leave';
      }

      days.push({
        dateStr,
        date: new Date(curr),
        dayOfWeek,
        status,
        label,
        isOff: status !== 'working'
      });

      curr.setDate(curr.getDate() + 1);
    }
    return days;
  }

  findBestStrategies(startDate, endDate, maxNewLeaves = 3, bookedLeaves = []) {
    const bookedSet = new Set(bookedLeaves);
    const cal = this.buildCalendar(startDate, endDate, bookedSet);
    const n = cal.length;
    if (n === 0) return [];

    const free = cal.map(d => d.isOff);
    const strategies = [];
    const seenRanges = new Set();

    // 1. Zero-leave baseline opportunities (long weekends >= 3 days)
    let i = 0;
    while (i < n) {
      if (free[i]) {
        let j = i;
        while (j < n && free[j]) j++;
        const len = j - i;
        if (len >= 3) {
          const key = `${cal[i].dateStr}_${cal[j-1].dateStr}`;
          if (!seenRanges.has(key)) {
            seenRanges.add(key);
            const sequence = [];
            for (let k = i; k < j; k++) {
              sequence.push({ ...cal[k] });
            }
            strategies.push({
              startDateStr: cal[i].dateStr,
              endDateStr: cal[j-1].dateStr,
              totalDays: len,
              leavesNeeded: 0,
              leaveDates: [],
              sequence,
              efficiency: len
            });
          }
        }
        i = j;
      } else {
        i++;
      }
    }

    // 2. Comprehensive candidate search around holidays for each budget
    for (let budget = 1; budget <= maxNewLeaves; budget++) {
      for (let left = 0; left < n; left++) {
        let workCount = 0;
        for (let right = left; right < n; right++) {
          if (!free[right]) workCount++;
          if (workCount > budget) break;

          const isMaxLeft = (left === 0 || !free[left - 1]);
          const isMaxRight = (right === n - 1 || !free[right + 1]);

          if (isMaxLeft && isMaxRight && workCount > 0) {
            let hasHoliday = false;
            for (let k = left; k <= right; k++) {
              if (cal[k].status === 'holiday') { hasHoliday = true; break; }
            }
            const totalDays = right - left + 1;
            if (hasHoliday && totalDays >= budget + 2) {
              const key = `${cal[left].dateStr}_${cal[right].dateStr}`;
              if (!seenRanges.has(key)) {
                seenRanges.add(key);
                const recommended = [];
                const sequence = [];
                for (let k = left; k <= right; k++) {
                  const orig = cal[k];
                  const isRec = !free[k];
                  if (isRec) recommended.push(orig.dateStr);
                  sequence.push({
                    dateStr: orig.dateStr,
                    date: orig.date,
                    status: isRec ? 'recommended' : orig.status,
                    label: isRec ? 'Recommended Leave' : orig.label,
                    isOff: true
                  });
                }
                const actualLeaves = recommended.length;
                if (actualLeaves > 0) {
                  strategies.push({
                    startDateStr: cal[left].dateStr,
                    endDateStr: cal[right].dateStr,
                    totalDays,
                    leavesNeeded: actualLeaves,
                    leaveDates: recommended,
                    sequence,
                    efficiency: totalDays / actualLeaves
                  });
                }
              }
            }
          }
        }
      }
    }

    // 3. Fallback to global best allocation for any budget not yet captured
    for (let budget = 1; budget <= maxNewLeaves; budget++) {
      const allocation = this._findBestAllocation(free, n, budget);
      if (allocation.winLen > 0) {
        const key = `${cal[allocation.winStart].dateStr}_${cal[allocation.winEnd].dateStr}`;
        if (!seenRanges.has(key)) {
          const recommended = [];
          const sequence = [];
          for (let k = allocation.winStart; k <= allocation.winEnd; k++) {
            const orig = cal[k];
            const isRec = !free[k] && allocation.bestArr[k];
            if (isRec) recommended.push(orig.dateStr);
            sequence.push({
              dateStr: orig.dateStr,
              date: orig.date,
              status: isRec ? 'recommended' : orig.status,
              label: isRec ? 'Recommended Leave' : orig.label,
              isOff: true
            });
          }
          const actualLeaves = recommended.length;
          if (actualLeaves > 0) {
            seenRanges.add(key);
            strategies.push({
              startDateStr: cal[allocation.winStart].dateStr,
              endDateStr: cal[allocation.winEnd].dateStr,
              totalDays: allocation.winLen,
              leavesNeeded: actualLeaves,
              leaveDates: recommended,
              sequence,
              efficiency: allocation.winLen / actualLeaves
            });
          }
        }
      }
    }

    // Sort by efficiency descending, then total days descending
    strategies.sort((a, b) => b.efficiency - a.efficiency || b.totalDays - a.totalDays);
    return strategies;
  }

  _findBestAllocation(free, n, budget) {
    let bestLen = 0;
    let bestLeft = 0;
    let left = 0;
    let workCount = 0;

    for (let right = 0; right < n; right++) {
      if (!free[right]) workCount++;

      while (workCount > budget) {
        if (!free[left]) workCount--;
        left++;
      }

      const windowLen = right - left + 1;
      if (windowLen > bestLen) {
        bestLen = windowLen;
        bestLeft = left;
      }
    }

    const bestRight = Math.min(n - 1, bestLeft + bestLen - 1);
    const bestArr = [...free];
    for (let i = bestLeft; i <= bestRight; i++) {
      bestArr[i] = true;
    }

    return { bestArr, winStart: bestLeft, winEnd: bestRight, winLen: bestLen };
  }
}

const optimizer = new HolidayOptimizer();

// 4. Live Date & Holiday Banner
function updateTodayBanner() {
  const now = new Date();
  const todayStr = formatDate(now);
  
  // Format Today Label
  const options = { weekday: 'long', month: 'short', day: 'numeric', year: 'numeric' };
  const dateLabel = document.getElementById('bannerTodayDate');
  if (dateLabel) dateLabel.textContent = now.toLocaleDateString('en-US', options);

  // Today's Status
  const dayOfWeek = now.getDay();
  const isWeekend = (dayOfWeek === 0 || dayOfWeek === 6);
  const isHoliday = optimizer.holidayMap.has(todayStr);
  const isLeave = State.bookedLeaves.includes(todayStr);

  const statusChip = document.getElementById('bannerTodayStatus');
  const statusText = document.getElementById('bannerTodayStatusText');

  if (statusChip && statusText) {
    if (isHoliday) {
      statusChip.querySelector('.status-icon').textContent = '🎉';
      statusText.textContent = `Today is ${optimizer.holidayMap.get(todayStr)}!`;
      statusChip.style.borderColor = 'var(--green)';
      statusChip.style.color = 'var(--green)';
    } else if (isLeave) {
      statusChip.querySelector('.status-icon').textContent = '🌴';
      statusText.textContent = `Today is a Booked Leave!`;
      statusChip.style.borderColor = 'var(--cyan)';
      statusChip.style.color = 'var(--cyan)';
    } else if (isWeekend) {
      statusChip.querySelector('.status-icon').textContent = '🛌';
      statusText.textContent = `Today: Weekend (Day Off)`;
      statusChip.style.borderColor = 'var(--purple)';
      statusChip.style.color = 'var(--purple)';
    } else {
      statusChip.querySelector('.status-icon').textContent = '💼';
      statusText.textContent = `Today: Working Day`;
      statusChip.style.borderColor = 'var(--cyan)';
      statusChip.style.color = 'var(--cyan)';
    }
  }

  // Next Public Holiday Countdown
  const upcomingHolidays = ALL_PUBLIC_HOLIDAYS
    .filter(h => h.date >= todayStr)
    .sort((a, b) => a.date.localeCompare(b.date));

  const nextNameEl = document.getElementById('bannerNextHolidayName');
  const nextCountEl = document.getElementById('bannerNextHolidayCountdown');
  const nextDateEl = document.getElementById('bannerNextHolidayDate');

  if (upcomingHolidays.length > 0 && nextNameEl && nextCountEl && nextDateEl) {
    const nextH = upcomingHolidays[0];
    const nextHDate = parseDate(nextH.date);
    const diffTime = nextHDate - new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    let countTxt = `in ${diffDays} days`;
    if (diffDays === 0) countTxt = "Today! 🎉";
    else if (diffDays === 1) countTxt = "Tomorrow! 🚀";

    nextNameEl.textContent = `🎉 ${nextH.name}`;
    nextCountEl.textContent = countTxt;
    nextDateEl.textContent = nextHDate.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric', year: 'numeric' });
  }
}

function updateLeaveHeader() {
  const used = State.bookedLeaves.length;
  const available = Math.max(0, State.totalLeaves - used);
  document.getElementById('headerLeaveCount').textContent = available;
  document.getElementById('headerTotalLeaves').textContent = State.totalLeaves;
}

function getEfficiencyBadge(eff) {
  if (eff >= 5.0) return { label: '🔥 LEGENDARY', color: 'var(--cyan)' };
  if (eff >= 4.0) return { label: '🏆 ELITE', color: 'var(--green)' };
  if (eff >= 3.0) return { label: '⭐ GREAT', color: 'var(--yellow)' };
  if (eff >= 2.0) return { label: '👍 GOOD', color: 'var(--purple)' };
  return { label: '🤔 OKAY', color: 'var(--text-muted)' };
}

// 5. Quick Hacks (Calculated based on selected Scope, DEFAULT: CURRENT MONTH)
function renderQuickHacks() {
  const container = document.getElementById('quickHacksList');
  container.innerHTML = '';

  const today = new Date();
  today.setHours(0, 0, 0, 0);

  let start = new Date(today);
  let end = new Date(today);
  let scopeLabel = '';

  if (State.currentScope === 'month') {
    // Current Month: From today to the end of the current month
    end = new Date(today.getFullYear(), today.getMonth() + 1, 0);
    const mName = today.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
    scopeLabel = `CURRENT MONTH (${mName}) from ${formatPrettyDate(formatDate(start))} to ${formatPrettyDate(formatDate(end))}`;
  } else if (State.currentScope === 'next_month') {
    // Next Month: From 1st to last day
    start = new Date(today.getFullYear(), today.getMonth() + 1, 1);
    end = new Date(today.getFullYear(), today.getMonth() + 2, 0);
    const mName = start.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
    scopeLabel = `NEXT MONTH (${mName}) from ${formatPrettyDate(formatDate(start))} to ${formatPrettyDate(formatDate(end))}`;
  } else if (State.currentScope === 'quarter') {
    end.setDate(end.getDate() + 90);
    scopeLabel = `NEXT 3 MONTHS from ${formatPrettyDate(formatDate(start))} to ${formatPrettyDate(formatDate(end))}`;
  } else {
    // Full year
    end.setFullYear(end.getFullYear() + 1);
    scopeLabel = `FULL YEAR from ${formatPrettyDate(formatDate(start))} to ${formatPrettyDate(formatDate(end))}`;
  }

  const subtitleEl = document.getElementById('quickHacksSubtitle');
  if (subtitleEl) {
    subtitleEl.textContent = `🎯 Focus: ${scopeLabel}. Minimal leaves, maximum freedom.`;
  }

  const allHacks = optimizer.findBestStrategies(start, end, 3, State.bookedLeaves);

  const filtered = State.currentBudgetFilter === 'all' 
    ? allHacks 
    : allHacks.filter(h => h.leavesNeeded === Number(State.currentBudgetFilter));

  if (filtered.length === 0) {
    container.innerHTML = `<div class="panel-card" style="text-align:center; padding:30px;"><p class="text-muted">No hacks found for this leave budget in the selected timeframe. Try selecting "All".</p></div>`;
    return;
  }

  filtered.forEach(hack => {
    const effBadge = getEfficiencyBadge(hack.efficiency);
    const card = document.createElement('div');
    card.className = 'hack-card';

    // Build timeline indicators
    const timelineHtml = hack.sequence.map(d => {
      let cls = 'day-working';
      let emoji = '💼';
      if (d.status === 'weekend') { cls = 'day-weekend'; emoji = '🛌'; }
      else if (d.status === 'holiday') { cls = 'day-holiday'; emoji = '🎉'; }
      else if (d.status === 'recommended') { cls = 'day-recommended'; emoji = '🏖️'; }
      else if (d.status === 'booked_leave') { cls = 'day-recommended'; emoji = '🌴'; }

      const dateObj = parseDate(d.dateStr);
      const dayNum = dateObj.getDate();
      const monthShort = dateObj.toLocaleDateString('en-US', { month: 'short' });

      return `
        <div class="timeline-day ${cls}" title="${d.label || d.dateStr}">
          <span>${monthShort}</span>
          <span style="font-weight:700;">${dayNum}</span>
          <span class="timeline-emoji">${emoji}</span>
        </div>
      `;
    }).join('');

    card.innerHTML = `
      <div class="card-top">
        <div class="card-dates">
          <div class="date-range">${formatPrettyDate(hack.startDateStr)} – ${formatPrettyDate(hack.endDateStr)}</div>
          <span class="day-count-badge">🚀 ${hack.totalDays} Consecutive Days Off</span>
        </div>
        <div class="efficiency-badge">
          <span class="eff-score">${hack.efficiency.toFixed(1)}x</span>
          <span class="eff-tag">${effBadge.label}</span>
        </div>
      </div>

      <div class="card-timeline">
        ${timelineHtml}
      </div>

      <div class="card-bottom">
        <div class="leave-info">
          Requires taking <strong>${hack.leavesNeeded} ${hack.leavesNeeded === 1 ? 'leave' : 'leaves'}</strong>: 
          <span class="text-cyan">${hack.leaveDates.map(formatPrettyDate).join(', ')}</span>
        </div>
        <div class="card-actions">
          <button class="btn btn-primary btn-small btn-book-hack" data-hack='${JSON.stringify(hack)}'>🌴 Book Leaves</button>
          <button class="btn btn-secondary btn-small btn-save-plan" data-hack='${JSON.stringify(hack)}'>💾 Save Plan</button>
        </div>
      </div>
    `;

    container.appendChild(card);
  });

  // Attach event listeners to buttons inside cards
  container.querySelectorAll('.btn-book-hack').forEach(btn => {
    btn.addEventListener('click', () => {
      const hack = JSON.parse(btn.getAttribute('data-hack'));
      bookHackLeaves(hack);
    });
  });

  container.querySelectorAll('.btn-save-plan').forEach(btn => {
    btn.addEventListener('click', () => {
      const hack = JSON.parse(btn.getAttribute('data-hack'));
      saveHolidayPlan(hack);
    });
  });
}

function bookHackLeaves(hack) {
  let newlyAdded = 0;
  hack.leaveDates.forEach(d => {
    if (!State.bookedLeaves.includes(d)) {
      State.bookedLeaves.push(d);
      newlyAdded++;
    }
  });

  if (newlyAdded > 0) {
    localStorage.setItem('hh_booked_leaves', JSON.stringify(State.bookedLeaves));
    showToast(`Booked ${newlyAdded} leaves successfully!`);
    updateLeaveHeader();
    renderQuickHacks();
    renderCalendar();
    renderMyLeaves();
    updateStats();
    updateTodayBanner();
  } else {
    showToast(`These leaves are already booked!`);
  }
}

function saveHolidayPlan(hack) {
  const planName = `${hack.totalDays}-Day Break (${formatPrettyDate(hack.startDateStr)})`;
  const existing = State.savedPlans.find(p => p.startDateStr === hack.startDateStr && p.endDateStr === hack.endDateStr);
  if (existing) {
    showToast(`This plan is already saved in My Plans!`);
    return;
  }

  State.savedPlans.push({
    id: Date.now(),
    name: planName,
    ...hack
  });
  localStorage.setItem('hh_saved_plans', JSON.stringify(State.savedPlans));
  showToast(`Plan "${planName}" saved!`);
  renderMyLeaves();
}

// 6. Calendar Rendering (Current Month by default, with TODAY cell marker)
function renderCalendar() {
  const monthYearLabel = document.getElementById('currentMonthYearLabel');
  const daysGrid = document.getElementById('calendarDaysGrid');
  daysGrid.innerHTML = '';

  const year = State.currentMonth.getFullYear();
  const month = State.currentMonth.getMonth();

  monthYearLabel.textContent = State.currentMonth.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });

  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);
  const startDayOfWeek = firstDay.getDay(); // 0 = Sun
  const totalDaysInMonth = lastDay.getDate();

  const bookedSet = new Set(State.bookedLeaves);
  const holidayMap = optimizer.holidayMap;
  const todayDate = new Date();

  // Render padding cells for previous month
  for (let i = 0; i < startDayOfWeek; i++) {
    const cell = document.createElement('div');
    cell.className = 'cal-day-cell other-month';
    daysGrid.appendChild(cell);
  }

  // Render days of the month
  for (let day = 1; day <= totalDaysInMonth; day++) {
    const currentDayDate = new Date(year, month, day);
    const dateStr = formatDate(currentDayDate);
    const dayOfWeek = currentDayDate.getDay();
    const isWeekend = (dayOfWeek === 0 || dayOfWeek === 6);
    const isHoliday = holidayMap.has(dateStr);
    const isLeave = bookedSet.has(dateStr);
    const isToday = currentDayDate.toDateString() === todayDate.toDateString();

    const cell = document.createElement('div');
    cell.className = 'cal-day-cell';

    if (isToday) {
      cell.classList.add('is-today');
    }

    let labelText = '';
    if (isLeave) {
      cell.classList.add('day-leave');
      labelText = '🌴 Booked Leave';
    } else if (isHoliday) {
      cell.classList.add('day-holiday');
      labelText = `🎉 ${holidayMap.get(dateStr)}`;
    } else if (isWeekend) {
      cell.classList.add('day-weekend');
      labelText = '🛌 Weekend';
    }

    cell.innerHTML = `
      <div class="cal-date-num">${day}</div>
      <div class="cal-day-label" title="${labelText}">${labelText}</div>
    `;

    // Click handler: toggle leave on working day
    cell.addEventListener('click', () => {
      if (isHoliday) {
        showToast(`Public Holiday: ${holidayMap.get(dateStr)}`);
      } else if (isWeekend) {
        showToast(`Weekend: No leave required!`);
      } else {
        // Toggle booked leave
        if (isLeave) {
          State.bookedLeaves = State.bookedLeaves.filter(d => d !== dateStr);
          showToast(`Cancelled leave on ${formatPrettyDate(dateStr)}`);
        } else {
          State.bookedLeaves.push(dateStr);
          showToast(`Booked leave on ${formatPrettyDate(dateStr)}`);
        }
        localStorage.setItem('hh_booked_leaves', JSON.stringify(State.bookedLeaves));
        updateLeaveHeader();
        renderCalendar();
        renderQuickHacks();
        renderMyLeaves();
        updateStats();
        updateTodayBanner();
      }
    });

    daysGrid.appendChild(cell);
  }
}

// 7. Range Explorer
function setupExplorer() {
  const slider = document.getElementById('rangeMaxLeaves');
  const sliderVal = document.getElementById('maxLeavesDisplay');
  slider.addEventListener('input', (e) => {
    sliderVal.textContent = e.target.value;
  });

  // Default explorer to TODAY and 6 months ahead!
  const today = new Date();
  const future = new Date(today);
  future.setMonth(future.getMonth() + 6);
  document.getElementById('rangeStartDate').value = formatDate(today);
  document.getElementById('rangeEndDate').value = formatDate(future);

  document.getElementById('runExplorerBtn').addEventListener('click', () => {
    const startStr = document.getElementById('rangeStartDate').value;
    const endStr = document.getElementById('rangeEndDate').value;
    const maxLeaves = Number(slider.value);

    if (!startStr || !endStr) {
      showToast('Please select valid start and end dates.');
      return;
    }

    const start = parseDate(startStr);
    const end = parseDate(endStr);
    if (start > end) {
      showToast('Start date must be before end date.');
      return;
    }

    const results = optimizer.findBestStrategies(start, end, maxLeaves, State.bookedLeaves);
    const container = document.getElementById('explorerResults');
    container.innerHTML = '';

    if (results.length === 0) {
      container.innerHTML = `<div class="panel-card" style="text-align:center; padding:30px;"><p class="text-muted">No strategies found for this range and budget. Try increasing max leaves!</p></div>`;
      return;
    }

    results.forEach(hack => {
      const effBadge = getEfficiencyBadge(hack.efficiency);
      const card = document.createElement('div');
      card.className = 'hack-card';

      card.innerHTML = `
        <div class="card-top">
          <div class="card-dates">
            <div class="date-range">${formatPrettyDate(hack.startDateStr)} – ${formatPrettyDate(hack.endDateStr)}</div>
            <span class="day-count-badge">🚀 ${hack.totalDays} Consecutive Days Off</span>
          </div>
          <div class="efficiency-badge">
            <span class="eff-score">${hack.efficiency.toFixed(1)}x</span>
            <span class="eff-tag">${effBadge.label}</span>
          </div>
        </div>

        <div class="card-bottom">
          <div class="leave-info">
            Uses <strong>${hack.leavesNeeded} leaves</strong>: 
            <span class="text-cyan">${hack.leaveDates.map(formatPrettyDate).join(', ')}</span>
          </div>
          <div class="card-actions">
            <button class="btn btn-primary btn-small btn-book-exp" data-hack='${JSON.stringify(hack)}'>🌴 Book Leaves</button>
            <button class="btn btn-secondary btn-small btn-save-exp" data-hack='${JSON.stringify(hack)}'>💾 Save Plan</button>
          </div>
        </div>
      `;

      card.querySelector('.btn-book-exp').addEventListener('click', () => bookHackLeaves(hack));
      card.querySelector('.btn-save-exp').addEventListener('click', () => saveHolidayPlan(hack));
      container.appendChild(card);
    });

    showToast(`Found ${results.length} optimal strategies!`);
  });
}

// 8. My Leaves & Plans View
function renderMyLeaves() {
  const leavesContainer = document.getElementById('bookedLeavesList');
  document.getElementById('bookedCountBadge').textContent = State.bookedLeaves.length;
  leavesContainer.innerHTML = '';

  if (State.bookedLeaves.length === 0) {
    leavesContainer.innerHTML = `<p class="text-muted" style="padding:10px 0;">No booked leaves yet. Click any day in the calendar or book from Quick Hacks!</p>`;
  } else {
    State.bookedLeaves.sort().forEach(dateStr => {
      const row = document.createElement('div');
      row.className = 'item-row';
      row.innerHTML = `
        <div>
          <div class="item-title">${formatPrettyDate(dateStr)}</div>
          <div class="item-sub">Personal Planned Leave</div>
        </div>
        <div class="item-actions">
          <button class="btn btn-outline btn-small btn-del-leave" data-date="${dateStr}">Cancel</button>
        </div>
      `;
      row.querySelector('.btn-del-leave').addEventListener('click', () => {
        State.bookedLeaves = State.bookedLeaves.filter(d => d !== dateStr);
        localStorage.setItem('hh_booked_leaves', JSON.stringify(State.bookedLeaves));
        updateLeaveHeader();
        renderCalendar();
        renderQuickHacks();
        renderMyLeaves();
        updateStats();
        updateTodayBanner();
        showToast('Leave cancelled.');
      });
      leavesContainer.appendChild(row);
    });
  }

  const plansContainer = document.getElementById('savedPlansList');
  document.getElementById('savedPlansCountBadge').textContent = State.savedPlans.length;
  plansContainer.innerHTML = '';

  if (State.savedPlans.length === 0) {
    plansContainer.innerHTML = `<p class="text-muted" style="padding:10px 0;">No saved holiday plans yet. Click "Save Plan" on any Quick Hack!</p>`;
  } else {
    State.savedPlans.forEach(plan => {
      const row = document.createElement('div');
      row.className = 'item-row';
      row.innerHTML = `
        <div>
          <div class="item-title">${plan.name}</div>
          <div class="item-sub text-green">${plan.totalDays} Days Off • ${plan.leavesNeeded} Leaves Used • ${plan.efficiency.toFixed(1)}x Eff</div>
        </div>
        <div class="item-actions">
          <button class="btn btn-primary btn-small btn-book-plan" data-id="${plan.id}">Book</button>
          <button class="btn btn-outline btn-small btn-del-plan" data-id="${plan.id}">Delete</button>
        </div>
      `;
      row.querySelector('.btn-book-plan').addEventListener('click', () => bookHackLeaves(plan));
      row.querySelector('.btn-del-plan').addEventListener('click', () => {
        State.savedPlans = State.savedPlans.filter(p => p.id !== plan.id);
        localStorage.setItem('hh_saved_plans', JSON.stringify(State.savedPlans));
        renderMyLeaves();
        showToast('Plan removed.');
      });
      plansContainer.appendChild(row);
    });
  }
}

// 9. Uselessness & Productivity Stats
function updateStats() {
  const usedLeaves = State.bookedLeaves.length;
  const workAvoidance = Math.min(100, Math.round((usedLeaves / State.totalLeaves) * 100));
  const productivity = Math.max(0, 100 - workAvoidance);
  const leaveEfficiency = Math.min(100, Math.round(usedLeaves > 0 ? (usedLeaves * 8) + 20 : 0));

  document.getElementById('workAvoidancePercent').textContent = `${workAvoidance}%`;
  document.getElementById('workAvoidanceBar').style.width = `${workAvoidance}%`;

  document.getElementById('leaveEfficiencyPercent').textContent = `${leaveEfficiency}%`;
  document.getElementById('leaveEfficiencyBar').style.width = `${leaveEfficiency}%`;

  document.getElementById('productivityPercent').textContent = `${productivity}%`;
  document.getElementById('productivityBar').style.width = `${productivity}%`;

  // Hacker Rank
  let title = "🌱 Holiday Seedling";
  if (usedLeaves >= 8) title = "🧙 Calendar Wizard";
  else if (usedLeaves >= 5) title = "🥷 Holiday Ninja";
  else if (usedLeaves >= 3) title = "🏄 Break Surfer";
  else if (usedLeaves >= 1) title = "😎 Certified Chiller";

  document.getElementById('hackerRankTitle').textContent = title;
  const randomQuote = SUCCESS_QUOTES[Math.floor(Math.random() * SUCCESS_QUOTES.length)];
  document.getElementById('hackerHumorQuote').textContent = `"${randomQuote}"`;
}

// 10. Toast Notification
function showToast(msg) {
  const toast = document.getElementById('toastNotification');
  toast.textContent = msg;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 3000);
}

// 11. Navigation Tab Switcher
function setupTabs() {
  const allTabs = document.querySelectorAll('.nav-tab, .mobile-tab');
  allTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const tabKey = tab.getAttribute('data-tab');

      // Update active states
      document.querySelectorAll('.nav-tab').forEach(t => {
        t.classList.toggle('active', t.getAttribute('data-tab') === tabKey);
      });
      document.querySelectorAll('.mobile-tab').forEach(t => {
        t.classList.toggle('active', t.getAttribute('data-tab') === tabKey);
      });

      // Show tab section
      document.querySelectorAll('.tab-view').forEach(view => {
        view.classList.toggle('active', view.id === `tab-${tabKey}`);
      });
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  });
}

// 12. PWA Installation Setup
function setupPWAInstall() {
  const installBtn = document.getElementById('installAppBtn');

  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    State.deferredInstallPrompt = e;
    installBtn.style.display = 'inline-flex';
  });

  installBtn.addEventListener('click', async () => {
    if (State.deferredInstallPrompt) {
      State.deferredInstallPrompt.prompt();
      const { outcome } = await State.deferredInstallPrompt.userChoice;
      if (outcome === 'accepted') {
        showToast('Thank you for installing Holiday Hacker!');
      }
      State.deferredInstallPrompt = null;
      installBtn.style.display = 'none';
    } else {
      showToast('Tap Share then "Add to Home Screen" to install on iOS!');
    }
  });

  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('./sw.js')
      .then(reg => console.log('Service Worker registered!', reg))
      .catch(err => console.error('Service Worker registration failed:', err));
  }
}

// 13. Initialize App
document.addEventListener('DOMContentLoaded', () => {
  updateTodayBanner();
  updateLeaveHeader();
  setupTabs();
  renderQuickHacks();
  renderCalendar();
  setupExplorer();
  renderMyLeaves();
  updateStats();
  setupPWAInstall();

  // Scope filter buttons (This Month, Next Month, Next 3 Months, Full Year)
  document.querySelectorAll('.scope-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.scope-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      State.currentScope = btn.getAttribute('data-scope');
      renderQuickHacks();
    });
  });

  // Budget filter buttons (All, 1, 2, 3)
  document.querySelectorAll('.budget-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.budget-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      State.currentBudgetFilter = btn.getAttribute('data-budget');
      renderQuickHacks();
    });
  });

  // Calendar prev/next buttons
  document.getElementById('prevMonthBtn').addEventListener('click', () => {
    State.currentMonth.setMonth(State.currentMonth.getMonth() - 1);
    renderCalendar();
  });
  document.getElementById('nextMonthBtn').addEventListener('click', () => {
    State.currentMonth.setMonth(State.currentMonth.getMonth() + 1);
    renderCalendar();
  });
  document.getElementById('todayBtn').addEventListener('click', () => {
    State.currentMonth = new Date();
    renderCalendar();
  });

  // Reset leaves button
  document.getElementById('resetLeavesBtn').addEventListener('click', () => {
    if (confirm('Are you sure you want to reset all booked leaves and plans?')) {
      State.bookedLeaves = [];
      State.savedPlans = [];
      localStorage.removeItem('hh_booked_leaves');
      localStorage.removeItem('hh_saved_plans');
      updateLeaveHeader();
      renderCalendar();
      renderQuickHacks();
      renderMyLeaves();
      updateStats();
      updateTodayBanner();
      showToast('Reset to defaults.');
    }
  });

  // Add manual leave date prompt
  document.getElementById('addManualLeaveBtn').addEventListener('click', () => {
    const inputDate = prompt('Enter leave date (YYYY-MM-DD):', formatDate(new Date()));
    if (inputDate && /^\d{4}-\d{2}-\d{2}$/.test(inputDate)) {
      if (!State.bookedLeaves.includes(inputDate)) {
        State.bookedLeaves.push(inputDate);
        localStorage.setItem('hh_booked_leaves', JSON.stringify(State.bookedLeaves));
        updateLeaveHeader();
        renderCalendar();
        renderQuickHacks();
        renderMyLeaves();
        updateStats();
        updateTodayBanner();
        showToast(`Booked leave on ${formatPrettyDate(inputDate)}`);
      } else {
        showToast('Date is already booked!');
      }
    }
  });
});
