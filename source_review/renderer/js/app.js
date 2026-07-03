/**
 * NBACore Desktop — Frontend Application v2
 * ===========================================
 * Features: i18n (zh/en), Stop Crawl, Interval/Duration settings
 */

// ── i18n Translations ──
const I18N = {
  en: {
    app_subtitle: 'Desktop Platform',
    nav_data: 'Data', nav_system: 'System',
    nav_dashboard: 'Dashboard', nav_browser: 'Data Browser',
    nav_visualizer: 'Visualizer', nav_analysis: 'Analysis',
    nav_crawler: 'Crawler', nav_logs: 'Live Logs',
    status_connecting: 'Connecting...', status_connected: 'Connected',
    status_server_db: 'Server & DB Ready', status_db_offline: 'DB Offline',
    status_server_offline: 'Server Offline', status_reconnecting: 'Reconnecting...',
    page_dashboard: 'Dashboard', page_browser: 'Data Browser',
    page_visualizer: 'Visualizer', page_analysis: 'Analysis',
    page_crawler: 'Crawler Control', page_logs: 'Live Logs',
    stat_tables: 'Tables', stat_records: 'Total Records',
    stat_teams: 'Active Teams', stat_lastgame: 'Last Game',
    stat_season: 'Season', stat_splits: 'Splits Records',
    dash_topscorers: 'Top Scoring Teams (2026)', dash_recentgames: 'Recent Games',
    dash_latest10: 'Latest 10', dash_dbtables: 'Database Tables',
    col_date: 'Date', col_away: 'Away', col_score: 'Score', col_home: 'Home',
    col_table: 'Table', col_rows: 'Rows', col_size: 'Size',
    col_player: 'Player', col_team: 'Team',
    lbl_season: 'Season:', lbl_interval: 'Request Interval (s):',
    lbl_duration: 'Max Duration (h):',
    hint_duration: '0 = no limit',
    ph_search: 'Search...', ph_player_name: 'Player name...',
    btn_refresh: 'Refresh', btn_search: 'Search', btn_compare: 'Compare',
    btn_load: 'Load', btn_clear: 'Clear', btn_start: 'Start',
    btn_check: 'Check Status', btn_daily: 'Daily Crawl',
    btn_list_tables: 'List Tables', btn_stop: 'Stop Crawl',
    btn_backfill: 'Backfill', btn_full_season: 'Full Season',
    crawl_settings: 'Crawl Settings', crawl_quick: 'Quick Actions',
    crawl_single: 'Single Table Crawl', crawl_backfill: 'Backfill',
    crawl_full_season: 'Full Season', crawl_logs: 'Crawl Logs',
    crawl_in_progress: 'Crawl in progress...', crawl_completed: 'Crawl completed in',
    crawl_failed: 'Crawl failed:', crawl_stopped: 'Crawl stopped by user',
    crawl_started: 'Crawl started:', crawl_stopped_msg: 'Crawl stopped successfully',
    no_crawl_running: 'No crawl is running',
    logs_realtime: 'Real-time Log Stream',
    viz_league_scoring: 'League Scoring Rankings',
    viz_scoring_trend: 'Team Scoring Trend', viz_team_radar: 'Team Radar',
    viz_team_comparison: 'Team Comparison',
    ana_leaderboard: 'Player Leaderboard',
    ana_topscorers_chart: 'Top Scorers Chart', ana_player_search: 'Players Search',
    opt_per_game: 'Per Game', opt_totals: 'Totals', opt_advanced: 'Advanced',
    opt_points: 'Points', opt_rebounds: 'Rebounds', opt_assists: 'Assists',
    opt_steals: 'Steals', opt_blocks: 'Blocks',
    toast_load_dash: 'Failed to load dashboard: ',
  },
  zh: {
    app_subtitle: '桌面平台',
    nav_data: '数据', nav_system: '系统',
    nav_dashboard: '仪表盘', nav_browser: '数据浏览',
    nav_visualizer: '可视化', nav_analysis: '数据分析',
    nav_crawler: '爬虫控制', nav_logs: '实时日志',
    status_connecting: '连接中...', status_connected: '已连接',
    status_server_db: '服务器和数据库就绪', status_db_offline: '数据库离线',
    status_server_offline: '服务器离线', status_reconnecting: '重新连接中...',
    page_dashboard: '仪表盘', page_browser: '数据浏览',
    page_visualizer: '可视化', page_analysis: '数据分析',
    page_crawler: '爬虫控制', page_logs: '实时日志',
    stat_tables: '数据表', stat_records: '总记录数',
    stat_teams: '活跃球队', stat_lastgame: '最近比赛',
    stat_season: '赛季', stat_splits: '分球记录',
    dash_topscorers: '得分排名球队 (2026)', dash_recentgames: '最近比赛',
    dash_latest10: '最新 10 场', dash_dbtables: '数据库表',
    col_date: '日期', col_away: '客队', col_score: '比分', col_home: '主队',
    col_table: '表名', col_rows: '行数', col_size: '大小',
    col_player: '球员', col_team: '球队',
    lbl_season: '赛季:', lbl_interval: '请求间隔 (秒):',
    lbl_duration: '最大持续时间 (小时):',
    hint_duration: '0 = 无限制',
    ph_search: '搜索...', ph_player_name: '球员姓名...',
    btn_refresh: '刷新', btn_search: '搜索', btn_compare: '对比',
    btn_load: '加载', btn_clear: '清空', btn_start: '开始',
    btn_check: '检查状态', btn_daily: '每日爬取',
    btn_list_tables: '列出表格', btn_stop: '停止爬取',
    btn_backfill: '回填', btn_full_season: '全赛季',
    crawl_settings: '爬取设置', crawl_quick: '快捷操作',
    crawl_single: '单表爬取', crawl_backfill: '回填',
    crawl_full_season: '全赛季', crawl_logs: '爬取日志',
    crawl_in_progress: '爬取进行中...', crawl_completed: '爬取完成，用时',
    crawl_failed: '爬取失败:', crawl_stopped: '爬取已被用户停止',
    crawl_started: '爬取已启动:', crawl_stopped_msg: '爬取已成功停止',
    no_crawl_running: '没有正在运行的爬取',
    logs_realtime: '实时日志流',
    viz_league_scoring: '联盟得分排名',
    viz_scoring_trend: '球队得分趋势', viz_team_radar: '球队雷达图',
    viz_team_comparison: '球队对比',
    ana_leaderboard: '球员排行榜',
    ana_topscorers_chart: '得分榜图表', ana_player_search: '球员搜索',
    opt_per_game: '场均', opt_totals: '总计', opt_advanced: '高级',
    opt_points: '得分', opt_rebounds: '篮板', opt_assists: '助攻',
    opt_steals: '抢断', opt_blocks: '盖帽',
    toast_load_dash: '加载仪表盘失败: ',
  },
};

let currentLang = 'zh'; // default Chinese

function t(key) {
  return (I18N[currentLang] && I18N[currentLang][key]) || I18N.en[key] || key;
}

function applyI18n() {
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    el.textContent = t(key);
  });
  document.querySelectorAll('[data-i18n-ph]').forEach(el => {
    const key = el.getAttribute('data-i18n-ph');
    el.placeholder = t(key);
  });
  document.documentElement.lang = currentLang === 'zh' ? 'zh-CN' : 'en';
}

function toggleLang() {
  currentLang = currentLang === 'zh' ? 'en' : 'zh';
  document.getElementById('langLabel').textContent = currentLang === 'zh' ? 'EN' : '中';
  applyI18n();
}

// ── API Configuration ──
let API_BASE = 'http://127.0.0.1:5577';

async function initApiBase() {
  if (window.nbaAPI && window.nbaAPI.getApiUrl) {
    try { API_BASE = await window.nbaAPI.getApiUrl(); } catch (e) {}
  }
  console.log('[App] API Base:', API_BASE);
}

// ── State ──
let currentPage = 'dashboard';
let browsePage = 1;
let browsePerPage = 50;
let logES = null;
let charts = {};
let teamList = [];

// ── Helpers ──
async function api(path, opts) {
  try {
    const r = await fetch(API_BASE + path, opts);
    if (!r.ok) {
      const err = await r.json().catch(() => ({ error: r.statusText }));
      throw new Error(err.error || `HTTP ${r.status}`);
    }
    return r.json();
  } catch (e) { console.error('[API]', path, e); throw e; }
}

function toast(msg, type = 'success') {
  const el = document.createElement('div');
  el.className = 'toast toast-' + type;
  el.textContent = msg;
  document.getElementById('toastContainer').appendChild(el);
  setTimeout(() => el.remove(), 3500);
}

function fmt(n) {
  if (n == null) return '—';
  if (n >= 1e9) return (n / 1e9).toFixed(2) + 'B';
  if (n >= 1e6) return (n / 1e6).toFixed(2) + 'M';
  if (n >= 1e3) return (n / 1e3).toFixed(1) + 'K';
  return String(n);
}

function fmtNum(v, d = 1) {
  if (v == null) return '—';
  return Number(v).toFixed(d);
}

// ── Navigation ──
function nav(page) {
  currentPage = page;
  document.querySelectorAll('.nav-item').forEach(e => e.classList.toggle('active', e.dataset.page === page));
  document.querySelectorAll('.page').forEach(e => e.classList.remove('active'));
  document.getElementById('page-' + page).classList.add('active');
  if (page === 'dashboard') loadDashboard();
  else if (page === 'browser') initBrowser();
  else if (page === 'visualizer') initVisualizer();
  else if (page === 'analysis') loadLeaderboard();
}

// ── Server Status ──
async function checkServerStatus() {
  const dot = document.querySelector('.status-dot');
  const text = document.querySelector('.status-text');
  try {
    const r = await api('/api/health');
    if (r.db) {
      dot.className = 'status-dot ready';
      text.textContent = t('status_server_db');
    } else {
      dot.className = 'status-dot error';
      text.textContent = t('status_db_offline');
    }
  } catch {
    dot.className = 'status-dot error';
    text.textContent = t('status_server_offline');
  }
}

// ── Dashboard ──
async function loadDashboard() {
  try {
    const d = await api('/api/status');
    document.getElementById('statTables').textContent = d.total_tables;
    document.getElementById('statRecords').textContent = fmt(d.total_records);
    document.getElementById('statRecordsSub').textContent = d.total_records.toLocaleString();
    document.getElementById('statTeams').textContent = d.active_teams;
    document.getElementById('statSeason').textContent = d.season;
    document.getElementById('statLastGame').textContent = d.last_game_date || 'N/A';
    document.getElementById('statSplits').textContent = fmt(d.splits.total);
    document.getElementById('statSplitsSub').textContent = `${d.splits.teams} teams, ${d.splits.seasons} seasons`;
    document.getElementById('tblCount').textContent = d.total_tables + ' tables';

    const tbody = document.getElementById('tablesBody');
    tbody.innerHTML = d.tables.map(t => {
      const badge = t.rows > 1e6 ? 'badge-orange' : t.rows > 1e4 ? 'badge-blue' : t.rows > 0 ? 'badge-green' : 'badge-gray';
      return `<tr><td style="font-family:var(--mono);font-size:12px;">${t.name}</td><td style="text-align:right;font-weight:600;">${t.rows.toLocaleString()}</td><td style="text-align:right;"><span class="badge ${badge}">${fmt(t.rows)}</span></td></tr>`;
    }).join('');

    const rgBody = document.getElementById('recentGamesBody');
    rgBody.innerHTML = (d.recent_games || []).map(g => {
      const aw = g.away_pts > g.home_pts;
      return `<tr><td style="font-size:12px;">${g.date}</td><td style="font-weight:${aw ? '700' : '400'};">${g.away}</td><td style="font-family:var(--mono);">${g.away_pts} - ${g.home_pts}</td><td style="font-weight:${!aw ? '700' : '400'};">${g.home}</td></tr>`;
    }).join('');

    renderTopScorersChart(d.top_scorers || []);
    if (d.tables) teamList = d.tables.filter(t => t.rows > 0).map(t => t.name);
  } catch (e) { toast(t('toast_load_dash') + e.message, 'error'); }
}

function renderTopScorersChart(data) {
  const el = document.getElementById('topScorersChart');
  if (!el) return;
  if (charts.topScorers) charts.topScorers.dispose();
  charts.topScorers = echarts.init(el);
  charts.topScorers.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['PPG', 'Plus/Minus'], textStyle: { color: '#6b7a99' } },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: data.map(d => d.team), axisLabel: { color: '#6b7a99', fontSize: 11 } },
    yAxis: [
      { type: 'value', name: 'PPG', axisLabel: { color: '#6b7a99' }, splitLine: { lineStyle: { color: '#1e2a45' } } },
      { type: 'value', name: '+/-', axisLabel: { color: '#6b7a99' }, splitLine: { show: false } },
    ],
    series: [
      { name: 'PPG', type: 'bar', data: data.map(d => d.pts), itemStyle: { color: '#00d9a3', borderRadius: [4, 4, 0, 0] }, barWidth: '50%' },
      { name: 'Plus/Minus', type: 'line', yAxisIndex: 1, data: data.map(d => d.plus_minus), itemStyle: { color: '#ffb84d' }, lineStyle: { width: 2 }, symbol: 'circle', symbolSize: 6 },
    ],
  });
}

// ── Data Browser ──
async function initBrowser() {
  const sel = document.getElementById('browseTable');
  if (sel.children.length > 0) return;
  const d = await api('/api/status');
  d.tables.forEach(t => {
    const opt = document.createElement('option');
    opt.value = t.name; opt.textContent = `${t.name} (${fmt(t.rows)})`;
    sel.appendChild(opt);
  });
  loadTable();
}

async function loadTable() {
  const table = document.getElementById('browseTable').value;
  if (!table) return;
  const search = document.getElementById('browseSearch').value;
  try {
    const d = await api(`/api/tables/${table}?page=${browsePage}&per_page=${browsePerPage}&search=${encodeURIComponent(search)}`);
    if (d.error) { toast(d.error, 'error'); return; }
    document.getElementById('dataHead').innerHTML = d.columns.map(c => `<th>${c}</th>`).join('');
    document.getElementById('dataBody').innerHTML = d.rows.map(row =>
      `<tr>${d.columns.map(c => { let v = row[c]; if (v === null || v === undefined) v = '<span style="color:var(--text-dim);">—</span>'; else if (typeof v === 'object') v = JSON.stringify(v); return `<td style="font-size:12px;font-family:var(--mono);">${v}</td>`; }).join('')}</tr>`
    ).join('');
    document.getElementById('browseInfo').textContent = `${d.total.toLocaleString()} rows · ${d.page}/${d.total_pages}`;
    const pg = document.getElementById('pagination');
    pg.innerHTML = '';
    if (d.total_pages > 1) {
      const mk = (label, page, dis, act) => { const b = document.createElement('button'); b.className = 'btn btn-sm' + (act ? ' btn-primary' : ''); b.textContent = label; b.disabled = dis; b.onclick = () => { browsePage = page; loadTable(); }; pg.appendChild(b); };
      mk('‹', d.page - 1, d.page <= 1);
      let s = Math.max(1, d.page - 2), e = Math.min(d.total_pages, d.page + 2);
      if (s > 1) { mk('1', 1); pg.innerHTML += '<span style="color:var(--text-dim);">…</span>'; }
      for (let i = s; i <= e; i++) mk(i, i, false, i === d.page);
      if (e < d.total_pages) { pg.innerHTML += '<span style="color:var(--text-dim);">…</span>'; mk(d.total_pages, d.total_pages); }
      mk('›', d.page + 1, d.page >= d.total_pages);
    }
  } catch (e) { toast(e.message, 'error'); }
}

// ── Visualizer ──
async function initVisualizer() {
  if (teamList.length === 0) { const d = await api('/api/status'); teamList = d.tables || []; }
  let teams = [];
  try { const d = await api('/api/teams'); teams = d.teams.filter(t => t.is_active).map(t => t.team_abbr); } catch { teams = ['BOS','LAL','GSW','DEN','OKC','SAS','MIA','CLE','DET','MIN','ATL','NYK','UTA','PHI','DAL','PHX','POR','SAC','MEM','MIL','NOP','IND','LAC','CHI','HOU','ORL','TOR','CHA','BKN','WAS']; }
  ['trendTeam', 'radarTeam', 'cmpTeam1', 'cmpTeam2'].forEach(id => {
    const sel = document.getElementById(id);
    if (sel.children.length === 0) teams.forEach(t => { const o = document.createElement('option'); o.value = t; o.textContent = t; sel.appendChild(o); });
  });
  document.getElementById('cmpTeam1').value = 'BOS';
  document.getElementById('cmpTeam2').value = 'LAL';
  loadLeagueScoring(); loadScoringTrend(); loadTeamRadar(); loadTeamComparison();
}

async function loadLeagueScoring() {
  const season = document.getElementById('vizSeason').value || '2026';
  try {
    const d = await api(`/api/charts/league-scoring?season=${season}`);
    const el = document.getElementById('leagueScoringChart');
    if (charts.leagueScoring) charts.leagueScoring.dispose();
    charts.leagueScoring = echarts.init(el);
    charts.leagueScoring.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      legend: { data: ['Points', 'Plus/Minus'], textStyle: { color: '#6b7a99' } },
      grid: { left: '3%', right: '4%', bottom: '10%', containLabel: true },
      xAxis: { type: 'category', data: d.data.map(r => r.team_abbr), axisLabel: { color: '#6b7a99', fontSize: 11, rotate: 45 } },
      yAxis: [
        { type: 'value', name: 'PTS', axisLabel: { color: '#6b7a99' }, splitLine: { lineStyle: { color: '#1e2a45' } } },
        { type: 'value', name: '+/-', axisLabel: { color: '#6b7a99' }, splitLine: { show: false } },
      ],
      series: [
        { name: 'Points', type: 'bar', data: d.data.map(r => r.pts), itemStyle: { color: '#00d9a3' } },
        { name: 'Plus/Minus', type: 'line', yAxisIndex: 1, data: d.data.map(r => r.plus_minus), itemStyle: { color: '#ffb84d' }, symbol: 'circle', symbolSize: 6 },
      ],
    });
  } catch (e) { toast(e.message, 'error'); }
}

async function loadScoringTrend() {
  const team = document.getElementById('trendTeam').value || 'BOS';
  try {
    const d = await api(`/api/charts/scoring-trend?team=${team}`);
    const el = document.getElementById('scoringTrendChart');
    if (charts.scoringTrend) charts.scoringTrend.dispose();
    charts.scoringTrend = echarts.init(el);
    charts.scoringTrend.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['PTS', 'Plus/Minus'], textStyle: { color: '#6b7a99' } },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'category', data: d.data.map(r => r.season), axisLabel: { color: '#6b7a99' } },
      yAxis: [
        { type: 'value', name: 'PTS', axisLabel: { color: '#6b7a99' }, splitLine: { lineStyle: { color: '#1e2a45' } } },
        { type: 'value', name: '+/-', axisLabel: { color: '#6b7a99' }, splitLine: { show: false } },
      ],
      series: [
        { name: 'PTS', type: 'line', data: d.data.map(r => r.pts), smooth: true, itemStyle: { color: '#00d9a3' }, areaStyle: { color: 'rgba(0,217,163,.1)' } },
        { name: 'Plus/Minus', type: 'line', yAxisIndex: 1, data: d.data.map(r => r.plus_minus), smooth: true, itemStyle: { color: '#ffb84d' } },
      ],
    });
  } catch (e) { toast(e.message, 'error'); }
}

async function loadTeamRadar() {
  const team = document.getElementById('radarTeam').value || 'BOS';
  const season = document.getElementById('vizSeason').value || '2026';
  try {
    const d = await api(`/api/charts/team-radar?team=${team}&season=${season}`);
    const el = document.getElementById('teamRadarChart');
    if (charts.teamRadar) charts.teamRadar.dispose();
    charts.teamRadar = echarts.init(el);
    const r = d.data || {};
    const max = { pts: 130, reb: 50, ast: 35, stl: 12, blk: 8, fg_pct: 0.55, fg3_pct: 0.45, ft_pct: 0.85 };
    charts.teamRadar.setOption({
      tooltip: {},
      radar: {
        indicator: [
          { name: 'PTS', max: max.pts }, { name: 'REB', max: max.reb },
          { name: 'AST', max: max.ast }, { name: 'STL', max: max.stl },
          { name: 'BLK', max: max.blk }, { name: 'FG%', max: max.fg_pct },
          { name: '3P%', max: max.fg3_pct }, { name: 'FT%', max: max.ft_pct },
        ],
        axisName: { color: '#6b7a99', fontSize: 11 },
        splitArea: { areaStyle: { color: ['rgba(0,217,163,.02)', 'rgba(0,217,163,.05)'] } },
        splitLine: { lineStyle: { color: '#1e2a45' } },
      },
      series: [{ type: 'radar', data: [{ value: [r.pts||0, r.reb||0, r.ast||0, r.stl||0, r.blk||0, r.fg_pct||0, r.fg3_pct||0, r.ft_pct||0], name: team, itemStyle: { color: '#00d9a3' }, areaStyle: { color: 'rgba(0,217,163,.2)' } }] }],
    });
  } catch (e) { toast(e.message, 'error'); }
}

async function loadTeamComparison() {
  const t1 = document.getElementById('cmpTeam1').value || 'BOS';
  const t2 = document.getElementById('cmpTeam2').value || 'LAL';
  const season = document.getElementById('vizSeason').value || '2026';
  try {
    const d = await api(`/api/charts/team-comparison?team1=${t1}&team2=${t2}&season=${season}`);
    const el = document.getElementById('teamCompareChart');
    if (charts.teamCompare) charts.teamCompare.dispose();
    charts.teamCompare = echarts.init(el);
    const stats = ['pts', 'reb', 'ast', 'stl', 'blk', 'fg_pct', 'fg3_pct', 'ft_pct'];
    const labels = ['PTS', 'REB', 'AST', 'STL', 'BLK', 'FG%', '3P%', 'FT%'];
    const maxVals = [130, 50, 35, 12, 8, 0.55, 0.45, 0.85];
    const d1 = d.teams[t1] || {}, d2 = d.teams[t2] || {};
    charts.teamCompare.setOption({
      tooltip: {},
      legend: { data: [t1, t2], textStyle: { color: '#6b7a99' } },
      radar: { indicator: labels.map((l, i) => ({ name: l, max: maxVals[i] })), axisName: { color: '#6b7a99', fontSize: 11 }, splitLine: { lineStyle: { color: '#1e2a45' } } },
      series: [{ type: 'radar', data: [
        { value: stats.map(s => d1[s] || 0), name: t1, itemStyle: { color: '#00d9a3' }, areaStyle: { color: 'rgba(0,217,163,.15)' } },
        { value: stats.map(s => d2[s] || 0), name: t2, itemStyle: { color: '#4d9fff' }, areaStyle: { color: 'rgba(77,159,255,.15)' } },
      ] }],
    });
  } catch (e) { toast(e.message, 'error'); }
}

// ── Analysis ──
async function loadLeaderboard() {
  const statType = document.getElementById('lbStatType').value;
  const sort = document.getElementById('lbSort').value;
  const season = document.getElementById('lbSeason').value || '2026';
  try {
    const d = await api(`/api/leaderboard/${statType}?sort=${sort}&season=${season}&limit=30`);
    const body = document.getElementById('leaderboardBody');
    body.innerHTML = (d.leaderboard || []).map((p, i) => {
      const rc = i < 3 ? ['var(--warn)', 'var(--text-dim)', '#cd7f32'][i] : 'var(--text-dim)';
      return `<tr><td style="font-weight:700;color:${rc};">${i+1}</td><td style="font-weight:600;">${p.player_name}</td><td><span class="badge badge-blue">${p.team}</span></td><td>${p.g}</td><td>${fmtNum(p.mp,1)}</td><td style="font-weight:700;color:var(--accent);">${fmtNum(p.pts,1)}</td><td>${fmtNum(p.reb,1)}</td><td>${fmtNum(p.ast,1)}</td><td>${fmtNum(p.stl,1)}</td><td>${fmtNum(p.blk,1)}</td><td>${fmtNum(p.fg_pct,3)}</td><td>${fmtNum(p.fg3_pct,3)}</td><td>${fmtNum(p.ts_pct,3)}</td></tr>`;
    }).join('');
    renderTopPlayersChart(d.leaderboard || []);
  } catch (e) { toast(e.message, 'error'); }
}

function renderTopPlayersChart(data) {
  const el = document.getElementById('topPlayersChart');
  if (!el) return;
  if (charts.topPlayers) charts.topPlayers.dispose();
  charts.topPlayers = echarts.init(el);
  const top10 = data.slice(0, 10);
  charts.topPlayers.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'value', axisLabel: { color: '#6b7a99' }, splitLine: { lineStyle: { color: '#1e2a45' } } },
    yAxis: { type: 'category', data: top10.map(d => d.player_name).reverse(), axisLabel: { color: '#6b7a99', fontSize: 11 } },
    series: [{ type: 'bar', data: top10.map(d => d.pts).reverse(), itemStyle: { color: new echarts.graphic.LinearGradient(0,0,1,0,[{offset:0,color:'#00a87e'},{offset:1,color:'#00d9a3'}]), borderRadius: [0,4,4,0] } }],
  });
}

async function searchPlayers() {
  const search = document.getElementById('playerSearch').value;
  const season = document.getElementById('lbSeason').value || '2026';
  try {
    const d = await api(`/api/players?search=${encodeURIComponent(search)}&season=${season}&per_page=50`);
    document.getElementById('playerBody').innerHTML = (d.players || []).map(p => `<tr><td style="font-weight:600;">${p.player_name}</td><td><span class="badge badge-blue">${p.team}</span></td><td>${p.g}</td><td style="font-weight:700;color:var(--accent);">${fmtNum(p.pts,1)}</td><td>${fmtNum(p.reb,1)}</td><td>${fmtNum(p.ast,1)}</td></tr>`).join('');
  } catch (e) { toast(e.message, 'error'); }
}

// ── Crawler Control ──
function getCrawlParams() {
  const interval = parseInt(document.getElementById('crawlInterval')?.value) || 0;
  const durationHours = parseFloat(document.getElementById('crawlDuration')?.value) || 0;
  const durationSeconds = Math.round(durationHours * 3600); // convert hours to seconds
  const params = {};
  if (interval > 0) params.interval = interval;
  if (durationSeconds > 0) params.duration = durationSeconds;
  return params;
}

async function crawl(mode, extraParams = {}) {
  const baseParams = getCrawlParams();
  const params = { ...baseParams, ...extraParams };
  try {
    const r = await api('/api/crawl', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mode, params }),
    });
    if (r.error) { toast(r.error, 'error'); return; }
    toast(t('crawl_started') + ' ' + mode);
    updateCrawlButtons(true);
    pollCrawlStatus();
  } catch (e) { toast(e.message, 'error'); }
}

function crawlSingle() {
  crawl('single', {
    table: document.getElementById('singleTable').value,
    season: document.getElementById('singleSeason').value,
    teams: document.getElementById('singleTeams').value,
  });
}
function crawlBackfill() { crawl('backfill', { days: document.getElementById('backfillDays').value }); }
function crawlFull() { crawl('full_season', { season: document.getElementById('fullSeason').value }); }

async function stopCrawl() {
  try {
    const r = await api('/api/crawl/stop', { method: 'POST' });
    if (r.error) { toast(r.error, 'error'); return; }
    toast(t('crawl_stopped_msg'));
    updateCrawlButtons(false);
  } catch (e) { toast(e.message, 'error'); }
}

function updateCrawlButtons(running) {
  document.querySelectorAll('#page-crawler .btn-primary').forEach(b => b.disabled = running);
  document.querySelectorAll('#page-crawler .btn').forEach(b => {
    if (b.id !== 'btnStop') b.disabled = running;
  });
  const stopBtn = document.getElementById('btnStop');
  if (stopBtn) stopBtn.disabled = !running;
  const banner = document.getElementById('crawlStatusBanner');
  if (running) {
    banner.innerHTML = `<div class="crawl-banner"><span class="spinner"></span> <strong>${t('crawl_in_progress')}</strong></div>`;
  } else {
    banner.innerHTML = '';
  }
}

async function pollCrawlStatus() {
  const check = async () => {
    try {
      const r = await api('/api/crawl/status');
      if (!r.running) {
        updateCrawlButtons(false);
        if (r.last_result) {
          if (r.last_result.status === 'success') {
            toast(`${t('crawl_completed')} ${r.last_result.duration}s`);
          } else if (r.last_result.status === 'stopped') {
            toast(t('crawl_stopped'));
          } else {
            toast(`${t('crawl_failed')} ${r.last_result.error || 'error'}`, 'error');
          }
        }
        loadDashboard();
        return;
      }
      setTimeout(check, 2000);
    } catch { setTimeout(check, 3000); }
  };
  setTimeout(check, 1000);
}

// ── Logs (SSE) ──
function startLogStream() {
  if (logES) logES.close();
  logES = new EventSource(API_BASE + '/api/logs/stream');
  logES.onmessage = (e) => {
    if (e.data.startsWith(':')) return;
    try { const log = JSON.parse(e.data); addLog(log, 'crawlLogBox'); addLog(log, 'fullLogBox'); } catch (_) {}
  };
  logES.onerror = () => {
    const s = document.getElementById('sseStatus');
    if (s) { s.textContent = t('status_reconnecting'); s.className = 'badge badge-orange'; }
  };
  logES.onopen = () => {
    const s = document.getElementById('sseStatus');
    if (s) { s.textContent = t('status_connected'); s.className = 'badge badge-green'; }
  };
}

function addLog(log, boxId) {
  const box = document.getElementById(boxId);
  if (!box) return;
  const div = document.createElement('div');
  div.className = 'log-line log-' + log.level;
  div.textContent = log.msg;
  box.appendChild(div);
  while (box.children.length > 500) box.removeChild(box.firstChild);
  box.scrollTop = box.scrollHeight;
}

function clearLogs() {
  ['crawlLogBox', 'fullLogBox'].forEach(id => { const el = document.getElementById(id); if (el) el.innerHTML = ''; });
}

// ── Window resize ──
window.addEventListener('resize', () => { Object.values(charts).forEach(c => { if (c && c.resize) c.resize(); }); });

// ── Init ──
window.addEventListener('DOMContentLoaded', async () => {
  applyI18n();
  await initApiBase();
  checkServerStatus();
  setInterval(checkServerStatus, 30000);
  loadDashboard();
  startLogStream();
  setInterval(() => { if (currentPage === 'dashboard') loadDashboard(); }, 60000);
});
