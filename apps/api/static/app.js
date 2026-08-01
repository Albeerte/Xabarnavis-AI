const authScreen = document.getElementById("authScreen");
const appShell = document.getElementById("appShell");
const authForm = document.getElementById("authForm");
const authUsername = document.getElementById("authUsername");
const authPassword = document.getElementById("authPassword");
const authPasswordCheck = document.getElementById("authPasswordCheck");
const passwordCheckField = document.getElementById("passwordCheckField");
const registerFields = document.getElementById("registerFields");
const authFirstName = document.getElementById("authFirstName");
const authLastName = document.getElementById("authLastName");
const authEmail = document.getElementById("authEmail");
const authUsernameLabel = document.getElementById("authUsernameLabel");
const authSubmit = document.getElementById("authSubmit");
const authError = document.getElementById("authError");
const authTabs = document.querySelectorAll(".auth-tab");

const userPill = document.getElementById("userPill");
const logoutButton = document.getElementById("logoutButton");
const themeToggle = document.getElementById("themeToggle");
const breadcrumbLabel = document.getElementById("breadcrumbLabel");
const pageTitle = document.getElementById("pageTitle");
const pageSubtitle = document.getElementById("pageSubtitle");
const navItems = document.querySelectorAll("[data-page]");
const pages = document.querySelectorAll(".page");
const totalCases = document.getElementById("totalCases");
const flaggedCases = document.getElementById("flaggedCases");
const realAverage = document.getElementById("realAverage");
const caseList = document.getElementById("caseList");
const archiveCaseList = document.getElementById("archiveCaseList");
const refreshCases = document.getElementById("refreshCases");
const refreshArchive = document.getElementById("refreshArchive");
const portfolioAvatar = document.getElementById("portfolioAvatar");
const portfolioUsername = document.getElementById("portfolioUsername");
const portfolioBio = document.getElementById("portfolioBio");
const portfolioCreated = document.getElementById("portfolioCreated");
const portfolioHandle = document.getElementById("portfolioHandle");
const portfolioEmail = document.getElementById("portfolioEmail");
const portfolioPhone = document.getElementById("portfolioPhone");
const portfolioOrganization = document.getElementById("portfolioOrganization");
const portfolioRole = document.getElementById("portfolioRole");
const portfolioTotal = document.getElementById("portfolioTotal");
const portfolioFlagged = document.getElementById("portfolioFlagged");
const portfolioRealAverage = document.getElementById("portfolioRealAverage");
const notificationList = document.getElementById("notificationList");
const markReadButton = document.getElementById("markReadButton");
const settingsForm = document.getElementById("settingsForm");
const displayNameInput = document.getElementById("displayNameInput");
const reportReminderInput = document.getElementById("reportReminderInput");
const autoReadyInput = document.getElementById("autoReadyInput");
const settingsSaved = document.getElementById("settingsSaved");

const modelList = document.getElementById("modelList");
const form = document.getElementById("analysisForm");
const imageInput = document.getElementById("imageInput");
const imageDescription = document.getElementById("imageDescription");
const fileState = document.getElementById("fileState");
const previewWrap = document.getElementById("previewWrap");
const previewImage = document.getElementById("previewImage");
const selectReady = document.getElementById("selectReady");
const detectButton = document.getElementById("detectButton");
const workspacePanel = document.getElementById("workspacePanel");
const workspaceReadyModels = document.getElementById("workspaceReadyModels");
const resultPanel = document.getElementById("resultPanel");

const caseNumber = document.getElementById("caseNumber");
const verdictBand = document.getElementById("verdictBand");
const verdictText = document.getElementById("verdictText");
const realScore = document.getElementById("realScore");
const aiScore = document.getElementById("aiScore");
const manipulatedScore = document.getElementById("manipulatedScore");
const modelResults = document.getElementById("modelResults");
const reportLink = document.getElementById("reportLink");
const docxReportLink = document.getElementById("docxReportLink");
const hashValue = document.getElementById("hashValue");
const confidenceValue = document.getElementById("confidenceValue");
const modelVersion = document.getElementById("modelVersion");
const detectedSigns = document.getElementById("detectedSigns");
const detailFilename = document.getElementById("detailFilename");
const detailVerdictBand = document.getElementById("detailVerdictBand");
const detailVerdict = document.getElementById("detailVerdict");
const detailReal = document.getElementById("detailReal");
const detailAi = document.getElementById("detailAi");
const detailManipulated = document.getElementById("detailManipulated");
const detailCaseId = document.getElementById("detailCaseId");
const detailUploaded = document.getElementById("detailUploaded");
const detailHash = document.getElementById("detailHash");
const detailConfidence = document.getElementById("detailConfidence");
const detailModelVersion = document.getElementById("detailModelVersion");
const detailDocxLink = document.getElementById("detailDocxLink");
const detailJsonLink = document.getElementById("detailJsonLink");
const detailSigns = document.getElementById("detailSigns");
const detailModelResults = document.getElementById("detailModelResults");
const videoAnalysisForm = document.getElementById("videoAnalysisForm");
const videoInput = document.getElementById("videoInput");
const videoFileState = document.getElementById("videoFileState");
const videoDetectButton = document.getElementById("videoDetectButton");
const videoVerdictBand = document.getElementById("videoVerdictBand");
const videoVerdict = document.getElementById("videoVerdict");
const videoRealScore = document.getElementById("videoRealScore");
const videoFakeScore = document.getElementById("videoFakeScore");
const videoFaceScore = document.getElementById("videoFaceScore");
const videoDocxLink = document.getElementById("videoDocxLink");
const videoJsonLink = document.getElementById("videoJsonLink");
const videoSigns = document.getElementById("videoSigns");
const audioAnalysisForm = document.getElementById("audioAnalysisForm");
const audioInput = document.getElementById("audioInput");
const audioFileState = document.getElementById("audioFileState");
const audioDetectButton = document.getElementById("audioDetectButton");
const audioVerdictBand = document.getElementById("audioVerdictBand");
const audioVerdict = document.getElementById("audioVerdict");
const audioRealScore = document.getElementById("audioRealScore");
const audioAiScore = document.getElementById("audioAiScore");
const audioSpoofScore = document.getElementById("audioSpoofScore");
const audioDocxLink = document.getElementById("audioDocxLink");
const audioJsonLink = document.getElementById("audioJsonLink");
const audioSigns = document.getElementById("audioSigns");
const textAnalysisForm = document.getElementById("textAnalysisForm");
const textTitleInput = document.getElementById("textTitleInput");
const textEvidenceInput = document.getElementById("textEvidenceInput");
const textDetectButton = document.getElementById("textDetectButton");
const textVerdictBand = document.getElementById("textVerdictBand");
const textVerdict = document.getElementById("textVerdict");
const textHumanScore = document.getElementById("textHumanScore");
const textAiScore = document.getElementById("textAiScore");
const textRiskScore = document.getElementById("textRiskScore");
const textDocxLink = document.getElementById("textDocxLink");
const textJsonLink = document.getElementById("textJsonLink");
const textSigns = document.getElementById("textSigns");

let authMode = "login";
let models = [];
let currentUser = null;
let cachedStats = null;
let cachedCases = [];

const pageMeta = {
  dashboard: {
    crumb: "Xabarnavis / Dashboard",
    title: "Tahlil boshqaruv paneli",
    subtitle: "Yuklangan media fayllaringiz bo'yicha real vaqtli forensic ma'lumotlar va eksport.",
  },
  image: {
    crumb: "Xabarnavis / Image Analyzer",
    title: "Image Analyzer",
    subtitle: "Rasmni yuklang, bir yoki bir nechta modelni tanlang va legal report yarating.",
  },
  video: {
    crumb: "Xabarnavis / Video Analyzer",
    title: "Video Analyzer",
    subtitle: "Video forensics moduli uchun alohida sahifa tayyor. Hozircha coming soon.",
  },
  audio: {
    crumb: "Xabarnavis / Audio Analyzer",
    title: "Audio Analyzer",
    subtitle: "Audio deepfake va spectral tekshiruv moduli uchun alohida sahifa tayyor.",
  },
  text: {
    crumb: "Xabarnavis / Text Analyzer",
    title: "Text Analyzer",
    subtitle: "Matn, claim va AI-written signal tekshiruvi uchun alohida sahifa tayyor.",
  },
  archives: {
    crumb: "Xabarnavis / Reports",
    title: "Reports archive",
    subtitle: "Hisobingizga bog'langan barcha legal DOCX va JSON reportlarni ko'ring.",
  },
  "report-detail": {
    crumb: "Xabarnavis / Report Detail",
    title: "Report detail",
    subtitle: "Bitta case bo'yicha score, hash, verdict va legal eksportlar.",
  },
  portfolio: {
    crumb: "Xabarnavis / Portfolio",
    title: "Portfolio",
    subtitle: "Account profilingiz, forensic faoliyatingiz va umumiy report statistikasi.",
  },
  notifications: {
    crumb: "Xabarnavis / Notifications",
    title: "Notifications",
    subtitle: "Report, model va system holatlari bo'yicha xabarlar.",
  },
  settings: {
    crumb: "Xabarnavis / Settings",
    title: "Settings",
    subtitle: "Local account sozlamalari va ish jarayoni preferencelari.",
  },
};

function percent(value) {
  return `${Math.round((Number(value || 0)) * 100)}%`;
}

async function api(path, options = {}) {
  const response = await fetch(path, { credentials: "same-origin", ...options });
  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json") ? await response.json() : await response.text();
  if (!response.ok) {
    throw new Error(payload.detail || payload || `HTTP ${response.status}`);
  }
  return payload;
}

function showApp(user) {
  authScreen.hidden = true;
  appShell.hidden = false;
  currentUser = user;
  userPill.textContent = user.username;
  hydrateSettings();
  renderPortfolio();
  renderNotifications();
  openInitialPage();
  loadModels();
}

function showAuth() {
  appShell.hidden = true;
  authScreen.hidden = false;
}

async function boot() {
  const storedTheme = localStorage.getItem("xabarnavis_theme");
  if (storedTheme === "light") document.body.classList.add("light");
  themeToggle.textContent = document.body.classList.contains("light") ? "Light" : "Dark";
  try {
    const payload = await api("/api/auth/me");
    showApp(payload.user);
  } catch {
    showAuth();
  }
}

authTabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    authMode = tab.dataset.authMode;
    authTabs.forEach((item) => item.classList.toggle("active", item === tab));
    authSubmit.textContent = authMode === "login" ? "Login" : "Register";
    registerFields.hidden = authMode !== "register";
    passwordCheckField.hidden = authMode !== "register";
    authFirstName.required = authMode === "register";
    authLastName.required = authMode === "register";
    authPassword.autocomplete = authMode === "login" ? "current-password" : "new-password";
    authUsernameLabel.textContent = authMode === "login" ? "Username or email" : "Username";
    authError.textContent = "";
  });
});

authForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  authError.textContent = "";
  authSubmit.disabled = true;
  if (authMode === "register" && authPassword.value !== authPasswordCheck.value) {
    authError.textContent = "Passwords do not match.";
    authSubmit.disabled = false;
    return;
  }
  const data = new FormData();
  data.append("username", authUsername.value.trim());
  data.append("password", authPassword.value);
  if (authMode === "register") {
    data.append("first_name", authFirstName.value.trim());
    data.append("last_name", authLastName.value.trim());
    data.append("email", authEmail.value.trim());
  }
  try {
    const payload = await api(`/api/auth/${authMode}`, { method: "POST", body: data });
    showApp(payload.user);
  } catch (error) {
    authError.textContent = error.message;
  } finally {
    authSubmit.disabled = false;
  }
});

logoutButton.addEventListener("click", async () => {
  await api("/api/auth/logout", { method: "POST" }).catch(() => null);
  showAuth();
});

themeToggle.addEventListener("click", () => {
  document.body.classList.toggle("light");
  const theme = document.body.classList.contains("light") ? "light" : "dark";
  localStorage.setItem("xabarnavis_theme", theme);
  themeToggle.textContent = theme === "light" ? "Light" : "Dark";
});

function showPage(name, options = {}) {
  const meta = pageMeta[name] || pageMeta.dashboard;
  pages.forEach((page) => page.classList.toggle("active", page.id === `page-${name}`));
  navItems.forEach((item) => item.classList.toggle("active", item.dataset.page === name));
  breadcrumbLabel.textContent = meta.crumb;
  pageTitle.textContent = meta.title;
  pageSubtitle.textContent = meta.subtitle;
  if (options.updateHash !== false && name !== "report-detail") {
    history.replaceState(null, "", `#${name}`);
  }
  if (name === "dashboard" || name === "archives") {
    loadDashboard().catch(() => null);
  }
  if (name === "portfolio") renderPortfolio();
  if (name === "notifications") renderNotifications();
  if (name === "settings") hydrateSettings();
}

navItems.forEach((item) => {
  item.addEventListener("click", () => {
    showPage(item.dataset.page);
  });
});

function openInitialPage() {
  const hash = window.location.hash.replace("#", "");
  if (hash.startsWith("report-")) {
    loadReportDetail(hash.replace("report-", ""));
    return;
  }
  showPage(pageMeta[hash] ? hash : "dashboard", { updateHash: false });
}

window.addEventListener("hashchange", () => {
  if (!currentUser) return;
  openInitialPage();
});

async function loadModels() {
  try {
    const payload = await api("/api/models");
    models = payload.models;
    renderModels(models);
  } catch (error) {
    modelList.innerHTML = `<div class="result-item"><p>${error.message}</p></div>`;
  }
}

function renderModels(items) {
  modelList.innerHTML = "";
  const settings = readSettings();
  const autoReady = settings.autoReady !== false;
  workspaceReadyModels.textContent = items.filter((model) => model.status === "ready").length;
  for (const model of items) {
    const label = document.createElement("label");
    label.className = "model-item";
    label.innerHTML = `
      <input type="checkbox" name="selected_models" value="${model.id}" ${autoReady && model.status === "ready" ? "checked" : ""} />
      <span>
        <strong>${model.name}</strong>
        <small>${model.purpose}</small>
      </span>
      <span class="model-state ${model.status}">${model.status.replaceAll("_", " ")}</span>
    `;
    modelList.appendChild(label);
  }
}

selectReady.addEventListener("click", () => {
  for (const checkbox of modelList.querySelectorAll("input[type='checkbox']")) {
    const model = models.find((item) => item.id === checkbox.value);
    checkbox.checked = model && model.status === "ready";
  }
});

imageInput.addEventListener("change", () => {
  const file = imageInput.files[0];
  if (!file) {
    fileState.textContent = "No file selected";
    previewWrap.hidden = true;
    return;
  }
  fileState.textContent = file.name;
  previewImage.src = URL.createObjectURL(file);
  previewWrap.hidden = false;
  resultPanel.hidden = true;
  workspacePanel.hidden = false;
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const file = imageInput.files[0];
  if (!file) {
    fileState.textContent = "Select an image first";
    return;
  }

  const selected = [...modelList.querySelectorAll("input[name='selected_models']:checked")].map((item) => item.value);
  const data = new FormData();
  data.append("file", file);
  data.append("image_description", imageDescription.value.trim());
  for (const modelId of selected) data.append("selected_models", modelId);

  detectButton.disabled = true;
  detectButton.textContent = "Detecting...";
  try {
    workspacePanel.hidden = true;
    const payload = await api("/api/analyze", { method: "POST", body: data });
    renderResult(payload);
    await loadDashboard();
  } catch (error) {
    workspacePanel.hidden = true;
    resultPanel.hidden = false;
    verdictText.textContent = error.message;
    verdictBand.className = "verdict-band manipulated";
  } finally {
    detectButton.disabled = false;
    detectButton.textContent = "Start Detecting";
  }
});

videoInput.addEventListener("change", () => {
  videoFileState.textContent = videoInput.files[0]?.name || "MP4, MOV, AVI";
});

audioInput.addEventListener("change", () => {
  audioFileState.textContent = audioInput.files[0]?.name || "WAV, MP3, M4A";
});

videoAnalysisForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  await submitMediaFileAnalysis({
    fileInput: videoInput,
    button: videoDetectButton,
    endpoint: "/api/analyze/video",
    mediaType: "video",
  });
});

audioAnalysisForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  await submitMediaFileAnalysis({
    fileInput: audioInput,
    button: audioDetectButton,
    endpoint: "/api/analyze/audio",
    mediaType: "audio",
  });
});

textAnalysisForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = new FormData();
  data.append("title", textTitleInput.value.trim() || "text-evidence.txt");
  data.append("text", textEvidenceInput.value.trim());
  textDetectButton.disabled = true;
  textDetectButton.textContent = "Analyzing...";
  try {
    const payload = await api("/api/analyze/text", { method: "POST", body: data });
    renderMediaResult("text", payload);
    await loadDashboard();
  } catch (error) {
    renderMediaError("text", error.message);
  } finally {
    textDetectButton.disabled = false;
    textDetectButton.textContent = "Analyze Text";
  }
});

async function submitMediaFileAnalysis({ fileInput, button, endpoint, mediaType }) {
  const file = fileInput.files[0];
  if (!file) {
    renderMediaError(mediaType, "Select a file first.");
    return;
  }
  const data = new FormData();
  data.append("file", file);
  button.disabled = true;
  button.textContent = "Analyzing...";
  try {
    const payload = await api(endpoint, { method: "POST", body: data });
    renderMediaResult(mediaType, payload);
    await loadDashboard();
  } catch (error) {
    renderMediaError(mediaType, error.message);
  } finally {
    button.disabled = false;
    button.textContent = mediaType === "video" ? "Analyze Video" : "Analyze Audio";
  }
}

function renderMediaError(mediaType, message) {
  const target = mediaTargets(mediaType);
  target.verdict.textContent = message;
  target.band.className = "verdict-band manipulated";
}

function renderMediaResult(mediaType, payload) {
  const target = mediaTargets(mediaType);
  target.verdict.textContent = payload.final_verdict;
  target.band.className = "verdict-band";
  const lower = payload.final_verdict.toLowerCase();
  if (lower.includes("real") || lower.includes("human")) target.band.classList.add("real");
  if (lower.includes("ai") || lower.includes("synthetic") || lower.includes("deepfake")) target.band.classList.add("ai");
  if (lower.includes("suspicious") || lower.includes("manipulated") || lower.includes("spoof")) target.band.classList.add("manipulated");
  target.primary.textContent = percent(payload.scores[target.primaryKey]);
  target.secondary.textContent = percent(payload.scores[target.secondaryKey]);
  target.tertiary.textContent = percent(payload.scores[target.tertiaryKey]);
  target.docx.href = `/api/cases/${payload.case_id}/report.docx`;
  target.json.href = `/api/cases/${payload.case_id}/report`;
  target.signs.innerHTML = "";
  for (const sign of payload.detected_signs || []) {
    const item = document.createElement("li");
    item.textContent = sign;
    target.signs.appendChild(item);
  }
}

function mediaTargets(mediaType) {
  if (mediaType === "video") {
    return {
      band: videoVerdictBand,
      verdict: videoVerdict,
      primary: videoRealScore,
      secondary: videoFakeScore,
      tertiary: videoFaceScore,
      primaryKey: "video_real_score",
      secondaryKey: "video_fake_score",
      tertiaryKey: "face_manipulation_score",
      docx: videoDocxLink,
      json: videoJsonLink,
      signs: videoSigns,
    };
  }
  if (mediaType === "audio") {
    return {
      band: audioVerdictBand,
      verdict: audioVerdict,
      primary: audioRealScore,
      secondary: audioAiScore,
      tertiary: audioSpoofScore,
      primaryKey: "real_voice_score",
      secondaryKey: "ai_voice_score",
      tertiaryKey: "speaker_spoof_score",
      docx: audioDocxLink,
      json: audioJsonLink,
      signs: audioSigns,
    };
  }
  return {
    band: textVerdictBand,
    verdict: textVerdict,
    primary: textHumanScore,
    secondary: textAiScore,
    tertiary: textRiskScore,
    primaryKey: "human_written_score",
    secondaryKey: "ai_text_score",
    tertiaryKey: "claim_risk_score",
    docx: textDocxLink,
    json: textJsonLink,
    signs: textSigns,
  };
}

function renderResult(payload) {
  workspacePanel.hidden = true;
  resultPanel.hidden = false;
  caseNumber.textContent = `Case ${payload.case_id}`;
  verdictText.textContent = payload.final_verdict;
  verdictBand.className = "verdict-band";
  const verdictLower = payload.final_verdict.toLowerCase();
  if (verdictLower.includes("ai")) verdictBand.classList.add("ai");
  if (verdictLower.includes("real")) verdictBand.classList.add("real");
  if (verdictLower.includes("manipulated") || verdictLower.includes("edited")) verdictBand.classList.add("manipulated");

  realScore.textContent = percent(payload.scores.real_score);
  aiScore.textContent = percent(payload.scores.ai_score);
  manipulatedScore.textContent = percent(payload.scores.manipulated_score);
  hashValue.textContent = payload.file_hash;
  confidenceValue.textContent = payload.confidence;
  modelVersion.textContent = payload.model_version;
  reportLink.href = `/api/cases/${payload.case_id}/report`;
  docxReportLink.href = `/api/cases/${payload.case_id}/report.docx`;
  reportLink.setAttribute("aria-disabled", "false");
  docxReportLink.setAttribute("aria-disabled", "false");

  detectedSigns.innerHTML = "";
  for (const sign of payload.detected_signs) {
    const li = document.createElement("li");
    li.textContent = sign;
    detectedSigns.appendChild(li);
  }

  modelResults.innerHTML = "";
  for (const result of payload.model_results) {
    const item = document.createElement("article");
    item.className = "result-item";
    const scores = [
      result.real_score == null ? null : `Real ${percent(result.real_score)}`,
      result.ai_score == null ? null : `AI ${percent(result.ai_score)}`,
      result.manipulated_score == null ? null : `Manipulated ${percent(result.manipulated_score)}`,
    ].filter(Boolean).join(" | ");
    item.innerHTML = `
      <header>
        <strong>${result.name}</strong>
        <span class="model-state ${result.status}">${result.status.replaceAll("_", " ")}</span>
      </header>
      <p>${result.verdict}${scores ? ` - ${scores}` : ""}</p>
      ${result.error ? `<p>${result.error}</p>` : ""}
    `;
    modelResults.appendChild(item);
  }
}

async function loadDashboard() {
  const [stats, cases] = await Promise.all([
    api("/api/stats"),
    api("/api/cases?limit=20"),
  ]);
  cachedStats = stats;
  cachedCases = cases.cases;
  totalCases.textContent = stats.total_cases;
  flaggedCases.textContent = stats.flagged_cases;
  realAverage.textContent = percent(stats.avg_real_score);
  renderCases(cases.cases);
  renderPortfolio();
  renderNotifications();
}

refreshCases.addEventListener("click", loadDashboard);
refreshArchive.addEventListener("click", loadDashboard);

function renderCases(cases) {
  const targets = [caseList, archiveCaseList].filter(Boolean);
  targets.forEach((target) => {
    target.innerHTML = "";
  });
  if (!cases.length) {
    targets.forEach((target) => {
      target.innerHTML = `<div class="result-item"><p>No reports yet. Run your first image, video, audio, or text analysis.</p></div>`;
    });
    return;
  }
  for (const item of cases) {
    const row = document.createElement("article");
    row.className = "case-row";
    row.innerHTML = `
      <div>
        <strong>${item.original_filename}</strong>
        <small>${item.uploaded_at} | ${(item.media_type || "image").toUpperCase()} | ${item.final_verdict || item.status}</small>
      </div>
      <span class="model-state ready">${percent(item.ai_score)} AI</span>
      <span class="report-actions">
        <button class="small-action" type="button" data-report-id="${item.id}">Open</button>
        <a href="/api/cases/${item.id}/report.docx" target="_blank" rel="noreferrer">DOCX</a>
        <a href="/api/cases/${item.id}/report" target="_blank" rel="noreferrer">JSON</a>
      </span>
    `;
    targets.forEach((target) => target.appendChild(row.cloneNode(true)));
  }
}

document.addEventListener("click", (event) => {
  const reportButton = event.target.closest("[data-report-id]");
  if (!reportButton) return;
  loadReportDetail(reportButton.dataset.reportId);
});

function applyVerdictClass(element, verdict) {
  element.className = "verdict-band";
  const lower = String(verdict || "").toLowerCase();
  if (lower.includes("ai")) element.classList.add("ai");
  if (lower.includes("real")) element.classList.add("real");
  if (lower.includes("manipulated") || lower.includes("edited")) element.classList.add("manipulated");
}

async function loadReportDetail(caseId) {
  showPage("report-detail", { updateHash: false });
  history.replaceState(null, "", `#report-${caseId}`);
  detailFilename.textContent = "Loading report...";
  detailVerdict.textContent = "-";
  detailSigns.innerHTML = "";
  detailModelResults.innerHTML = "";

  try {
    const summary = await api(`/api/cases/${caseId}`);
    let report = null;
    try {
      report = await api(`/api/cases/${caseId}/report`);
    } catch {
      report = null;
    }

    const scores = report?.scores || summary;
    detailFilename.textContent = summary.original_filename;
    detailVerdict.textContent = summary.final_verdict || report?.final_verdict || summary.status;
    applyVerdictClass(detailVerdictBand, detailVerdict.textContent);
    detailReal.textContent = percent(scores.real_score);
    detailAi.textContent = percent(scores.ai_score);
    detailManipulated.textContent = percent(scores.manipulated_score);
    detailCaseId.textContent = `Case ${summary.id}`;
    detailUploaded.textContent = summary.uploaded_at;
    detailHash.textContent = summary.file_hash;
    detailConfidence.textContent = summary.confidence || report?.confidence || "-";
    detailModelVersion.textContent = summary.model_version || report?.model_version || "-";
    detailDocxLink.href = `/api/cases/${summary.id}/report.docx`;
    detailJsonLink.href = `/api/cases/${summary.id}/report`;

    const signs = report?.detected_signs || report?.legal_report?.detected_signs || [];
    detailSigns.innerHTML = "";
    if (!signs.length) {
      detailSigns.innerHTML = "<li>No detailed signs stored in this report.</li>";
    } else {
      for (const sign of signs) {
        const li = document.createElement("li");
        li.textContent = sign;
        detailSigns.appendChild(li);
      }
    }

    detailModelResults.innerHTML = "";
    const modelRuns = report?.model_results || [];
    if (!modelRuns.length) {
      detailModelResults.innerHTML = `<div class="result-item"><p>No per-model results stored for this report.</p></div>`;
    } else {
      for (const result of modelRuns) {
        const item = document.createElement("article");
        item.className = "result-item";
        const scoresText = [
          result.real_score == null ? null : `Real ${percent(result.real_score)}`,
          result.ai_score == null ? null : `AI ${percent(result.ai_score)}`,
          result.manipulated_score == null ? null : `Manipulated ${percent(result.manipulated_score)}`,
        ].filter(Boolean).join(" | ");
        item.innerHTML = `
          <header>
            <strong>${result.name || result.model_id}</strong>
            <span class="model-state ${result.status || "ready"}">${String(result.status || "ready").replaceAll("_", " ")}</span>
          </header>
          <p>${result.verdict || "Result stored"}${scoresText ? ` - ${scoresText}` : ""}</p>
        `;
        detailModelResults.appendChild(item);
      }
    }
  } catch (error) {
    detailFilename.textContent = "Report not found";
    detailVerdict.textContent = error.message;
    applyVerdictClass(detailVerdictBand, "manipulated");
  }
}

function getSettingsKey() {
  return `xabarnavis_settings_${currentUser?.id || "guest"}`;
}

function readSettings() {
  try {
    return JSON.parse(localStorage.getItem(getSettingsKey())) || {};
  } catch {
    return {};
  }
}

function hydrateSettings() {
  const settings = readSettings();
  displayNameInput.value = settings.displayName || currentUser?.username || "";
  reportReminderInput.checked = Boolean(settings.reportReminder);
  autoReadyInput.checked = settings.autoReady !== false;
  settingsSaved.textContent = "";
}

settingsForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const settings = {
    displayName: displayNameInput.value.trim(),
    reportReminder: reportReminderInput.checked,
    autoReady: autoReadyInput.checked,
  };
  localStorage.setItem(getSettingsKey(), JSON.stringify(settings));
  settingsSaved.textContent = "Settings saved.";
  renderPortfolio();
  renderNotifications();
});

function renderPortfolio() {
  if (!currentUser) return;
  const settings = readSettings();
  const fullName = [currentUser.first_name, currentUser.last_name].filter(Boolean).join(" ").trim();
  const displayName = settings.displayName || fullName || currentUser.username;
  portfolioUsername.textContent = displayName;
  portfolioAvatar.innerHTML = "";
  if (currentUser.avatar_path) {
    const image = document.createElement("img");
    image.src = currentUser.avatar_path;
    image.alt = `${displayName} profile image`;
    portfolioAvatar.appendChild(image);
  } else {
    portfolioAvatar.textContent = displayName.slice(0, 1).toUpperCase();
  }
  portfolioBio.textContent = currentUser.bio || "Local forensic analyst workspace";
  portfolioCreated.textContent = currentUser.created_at || "-";
  portfolioHandle.textContent = currentUser.username || "-";
  portfolioEmail.textContent = currentUser.email || "-";
  portfolioPhone.textContent = currentUser.phone || "-";
  portfolioOrganization.textContent = currentUser.organization || "-";
  portfolioRole.textContent = currentUser.role || "-";
  portfolioTotal.textContent = cachedStats?.total_cases ?? 0;
  portfolioFlagged.textContent = cachedStats?.flagged_cases ?? 0;
  portfolioRealAverage.textContent = percent(cachedStats?.avg_real_score);
}

function renderNotifications() {
  if (!notificationList) return;
  const items = [
    {
      title: "Image analyzer is live",
      body: "Xabarnavis image analysis can create DOCX and JSON legal reports.",
      state: "live",
    },
    {
      title: `${cachedCases.length} recent reports loaded`,
      body: "Open any report from Reports archive to view its individual page.",
      state: "ready",
    },
    {
      title: "Video, audio, and text analyzers prepared",
      body: "Their pages are ready and model pipelines can be connected next.",
      state: "soon",
    },
  ];
  notificationList.innerHTML = "";
  for (const item of items) {
    const row = document.createElement("article");
    row.className = "notification-row";
    row.innerHTML = `
      <span class="notification-dot ${item.state}"></span>
      <div>
        <strong>${item.title}</strong>
        <p>${item.body}</p>
      </div>
    `;
    notificationList.appendChild(row);
  }
}

markReadButton.addEventListener("click", () => {
  notificationList.querySelectorAll(".notification-row").forEach((row) => row.classList.add("read"));
});

boot();
