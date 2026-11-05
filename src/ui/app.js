// MarkItDown Studio - Client Logic (All English UI)

let currentConfig = {
  default_output_dir: "",
  ask_destination: false
};

let activePreviewText = "";
let resultsHistory = [];
let isInitialized = false;

async function initializeApp() {
  if (isInitialized) return;
  isInitialized = true;
  await loadSettings();
  setupEventListeners();
  updateStatus("READY", "badge-success");
}

window.addEventListener("pywebviewready", initializeApp);

if (window.pywebview && window.pywebview.api) {
  initializeApp();
}

async function loadSettings() {
  try {
    if (window.pywebview && window.pywebview.api) {
      currentConfig = await window.pywebview.api.get_config();
      document.getElementById("current-dest-text").textContent = currentConfig.default_output_dir || "Unset";
      document.getElementById("toggle-ask-dest").checked = !!currentConfig.ask_destination;
    }
  } catch (err) {
    console.error("Config load error:", err);
  }
}

function updateStatus(text) {
  const badge = document.getElementById("status-badge");
  if (badge) badge.textContent = `[${text}]`;
}

function setupEventListeners() {
  const dropzone = document.getElementById("dropzone");
  const btnChangeFolder = document.getElementById("btn-change-folder");
  const btnOpenFolder = document.getElementById("btn-open-folder");
  const toggleAskDest = document.getElementById("toggle-ask-dest");
  const btnClearResults = document.getElementById("btn-clear-results");
  const modalClose = document.getElementById("btn-close-modal");
  const previewModal = document.getElementById("preview-modal");
  const btnCopyPreview = document.getElementById("btn-copy-preview");

  // Click dropzone -> Native Windows File Picker
  dropzone.addEventListener("click", async () => {
    try {
      if (!window.pywebview || !window.pywebview.api) return;
      const filePaths = await window.pywebview.api.select_files();
      if (filePaths && filePaths.length > 0) {
        await processPaths(filePaths);
      }
    } catch (err) {
      showToast("Error picking files: " + err, "error");
    }
  });

  // Drag and drop events
  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  });

  dropzone.addEventListener("dragleave", (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
  });

  dropzone.addEventListener("drop", async (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");

    const files = Array.from(e.dataTransfer.files);
    if (!files || files.length === 0) return;

    await processDroppedFiles(files);
  });

  // Change destination folder
  btnChangeFolder.addEventListener("click", async () => {
    try {
      if (!window.pywebview || !window.pywebview.api) return;
      const newFolder = await window.pywebview.api.select_directory();
      if (newFolder) {
        currentConfig.default_output_dir = newFolder;
        document.getElementById("current-dest-text").textContent = newFolder;
        await window.pywebview.api.update_config("default_output_dir", newFolder);
        showToast("Destination directory updated", "success");
      }
    } catch (err) {
      showToast("Directory update error: " + err, "error");
    }
  });

  // Open folder in Windows Explorer
  btnOpenFolder.addEventListener("click", async () => {
    try {
      if (window.pywebview && window.pywebview.api) {
        await window.pywebview.api.open_folder(currentConfig.default_output_dir);
      }
    } catch (err) {
      showToast("Could not open directory", "error");
    }
  });

  // Toggle Ask destination
  toggleAskDest.addEventListener("change", async (e) => {
    try {
      currentConfig.ask_destination = e.target.checked;
      if (window.pywebview && window.pywebview.api) {
        await window.pywebview.api.update_config("ask_destination", e.target.checked);
      }
      showToast(
        e.target.checked ? "Prompt enabled for each conversion" : "Saving automatically to default directory",
        "info"
      );
    } catch (err) {
      console.error(err);
    }
  });

  // Clear list
  btnClearResults.addEventListener("click", () => {
    resultsHistory = [];
    renderResults();
  });

  // Modal events
  modalClose.addEventListener("click", closeModal);
  previewModal.addEventListener("click", (e) => {
    if (e.target === previewModal) closeModal();
  });
  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeModal();
  });

  // Copy full markdown
  btnCopyPreview.addEventListener("click", async () => {
    if (!activePreviewText) return;
    await copyText(activePreviewText);
    showToast("Full Markdown copied to clipboard!", "success");
  });
}

function closeModal() {
  document.getElementById("preview-modal").style.display = "none";
}

// Convert files selected via Windows Dialog
async function processPaths(paths) {
  if (!paths || paths.length === 0) return;

  let targetDir = currentConfig.default_output_dir;

  if (currentConfig.ask_destination) {
    targetDir = await window.pywebview.api.select_directory();
    if (!targetDir) {
      showToast("Cancelled (no folder selected)", "info");
      return;
    }
  }

  showProgress(true);
  updateStatus("PROCESSING");

  const total = paths.length;
  let successCount = 0;

  for (let i = 0; i < total; i++) {
    const filePath = paths[i];
    const fileName = filePath.split(/[/\\]/).pop();
    updateProgress(i + 1, total, `CONVERTING: ${fileName}`);

    try {
      const result = await window.pywebview.api.convert_file_path(filePath, targetDir);
      resultsHistory.unshift(result);
      renderResults();

      if (result.success) {
        successCount++;
        showToast(`Saved: ${truncatePath(result.output_path)}`, "success");
      } else {
        showToast(`Error in ${result.file_name}: ${result.error}`, "error");
      }
    } catch (err) {
      resultsHistory.unshift({
        success: false,
        file_name: fileName,
        error: String(err)
      });
      renderResults();
    }
  }

  showProgress(false);
  updateStatus("READY");

  if (successCount > 0) {
    triggerSuccessPulse();
  }
}

// Convert files dropped into browser
async function processDroppedFiles(files) {
  let targetDir = currentConfig.default_output_dir;

  if (currentConfig.ask_destination) {
    targetDir = await window.pywebview.api.select_directory();
    if (!targetDir) {
      showToast("Cancelled (no folder selected)", "info");
      return;
    }
  }

  showProgress(true);
  updateStatus("PROCESSING");

  const total = files.length;
  let successCount = 0;

  for (let i = 0; i < total; i++) {
    const file = files[i];
    updateProgress(i + 1, total, `READING: ${file.name}`);

    try {
      const base64Data = await readFileAsBase64(file);
      updateProgress(i + 1, total, `CONVERTING: ${file.name}`);

      const result = await window.pywebview.api.convert_base64_file(file.name, base64Data, targetDir);
      resultsHistory.unshift(result);
      renderResults();

      if (result.success) {
        successCount++;
        showToast(`Saved: ${truncatePath(result.output_path)}`, "success");
      } else {
        showToast(`Error in ${result.file_name}: ${result.error}`, "error");
      }
    } catch (err) {
      resultsHistory.unshift({
        success: false,
        file_name: file.name,
        error: String(err)
      });
      renderResults();
    }
  }

  showProgress(false);
  updateStatus("READY");

  if (successCount > 0) {
    triggerSuccessPulse();
  }
}

function triggerSuccessPulse() {
  const dropzone = document.getElementById("dropzone");
  const promptLabel = document.getElementById("prompt-label");
  dropzone.classList.add("success-pulse");
  if (promptLabel) promptLabel.textContent = "SAVED TO DISK [✓]";

  setTimeout(() => {
    dropzone.classList.remove("success-pulse");
    if (promptLabel) promptLabel.textContent = "DROP FILES TO CONVERT";
  }, 2200);
}

function readFileAsBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result.split(",")[1]);
    reader.onerror = (err) => reject(err);
    reader.readAsDataURL(file);
  });
}

function showProgress(visible) {
  const card = document.getElementById("progress-card");
  card.style.display = visible ? "flex" : "none";
  if (!visible) {
    document.getElementById("progress-bar-fill").style.width = "0%";
  }
}

function updateProgress(current, total, label) {
  const percent = Math.round((current / total) * 100);
  document.getElementById("progress-bar-fill").style.width = `${percent}%`;
  document.getElementById("progress-text").textContent = label;
  document.getElementById("progress-count").textContent = `${current} / ${total}`;
}

function renderResults() {
  const list = document.getElementById("results-list");
  const header = document.getElementById("results-header");

  if (!resultsHistory || resultsHistory.length === 0) {
    if (header) header.style.display = "none";
    list.innerHTML = "";
    return;
  }

  if (header) header.style.display = "flex";
  list.innerHTML = "";

  resultsHistory.forEach((item, index) => {
    const card = document.createElement("div");
    card.className = `result-card ${item.success ? "status-success" : "status-error"}`;

    const ext = getFileExtension(item.file_name);
    const badgeClass = getIconClass(ext);

    let metaHtml = "";
    if (item.success) {
      metaHtml = `
        <span class="result-meta">
          <span>${item.lines_count || 0} lines</span>
          <span>•</span>
          <span>${item.chars_count?.toLocaleString() || 0} chars</span>
          <span>•</span>
          <span title="${item.output_path}">${truncatePath(item.output_path)}</span>
        </span>
      `;
    } else {
      metaHtml = `<span class="result-error-msg" style="color: #f43f5e; font-size: 11px;">${escapeHtml(item.error || "Unknown error")}</span>`;
    }

    let actionsHtml = "";
    if (item.success) {
      actionsHtml = `
        <div class="result-actions">
          <button class="pixel-btn pixel-btn-silver btn-sm" onclick="copyResult(${index})" title="Copy entire Markdown file">
            <span>Copy</span>
          </button>
          <button class="pixel-btn pixel-btn-outline btn-sm" onclick="viewResult(${index})" title="View full Markdown content">
            <span>View</span>
          </button>
          <button class="pixel-btn pixel-btn-outline btn-sm" onclick="openResultFolder(${index})" title="Open containing folder in Explorer">
            <span>Dir ↗</span>
          </button>
        </div>
      `;
    }

    card.innerHTML = `
      <div class="result-info">
        <span class="result-badge ${badgeClass}">[${ext}]</span>
        <div class="result-details">
          <div class="result-name-row">
            <span title="${escapeHtml(item.file_name)}">${escapeHtml(item.file_name)}</span>
            <span class="result-arrow">──→</span>
            <span style="color: var(--cyan-core); font-weight: 600;">${escapeHtml(truncatePath(item.output_path) || ".md")}</span>
          </div>
          ${metaHtml}
        </div>
      </div>
      ${actionsHtml}
    `;

    list.appendChild(card);
  });
}

function getFileExtension(filename) {
  if (!filename) return "MD";
  const parts = filename.split(".");
  return parts.length > 1 ? parts.pop().toUpperCase() : "DOC";
}

function getIconClass(ext) {
  const e = ext.toLowerCase();
  if (e === "pdf") return "pdf";
  if (["docx", "doc"].includes(e)) return "docx";
  if (["xlsx", "xls", "csv"].includes(e)) return "xlsx";
  if (["pptx", "ppt"].includes(e)) return "pptx";
  return "other";
}

function truncatePath(path) {
  if (!path) return "";
  const parts = path.split(/[/\\]/);
  return parts[parts.length - 1];
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

window.viewResult = async function(index) {
  const item = resultsHistory[index];
  if (!item || !item.success) return;

  // Load 100% full markdown content
  let fullText = item.content;
  if (!fullText && window.pywebview && window.pywebview.api) {
    fullText = await window.pywebview.api.read_full_content(item.output_path);
  }

  activePreviewText = fullText || "";
  document.getElementById("modal-filename").textContent = truncatePath(item.output_path);
  document.getElementById("modal-filesize").textContent = `${item.lines_count || 0} lines • ${item.chars_count?.toLocaleString()} chars`;
  document.getElementById("modal-code").textContent = fullText || "(Empty document)";
  document.getElementById("preview-modal").style.display = "flex";
};

window.copyResult = async function(index) {
  const item = resultsHistory[index];
  if (!item || !item.success) return;

  try {
    if (window.pywebview && window.pywebview.api) {
      await window.pywebview.api.copy_file_content(item.output_path);
      showToast("Full Markdown copied to clipboard!", "success");
    } else {
      await copyText(item.content);
      showToast("Markdown copied!", "success");
    }
  } catch (err) {
    showToast("Copy error: " + err, "error");
  }
};

window.openResultFolder = async function(index) {
  const item = resultsHistory[index];
  if (!item || !item.output_dir) return;

  try {
    if (window.pywebview && window.pywebview.api) {
      await window.pywebview.api.open_folder(item.output_dir);
    }
  } catch (err) {
    showToast("Error opening directory", "error");
  }
};

async function copyText(text) {
  try {
    if (window.pywebview && window.pywebview.api) {
      await window.pywebview.api.copy_text(text);
    } else if (navigator.clipboard) {
      await navigator.clipboard.writeText(text);
    }
  } catch (err) {
    console.error("Clipboard copy error:", err);
  }
}

function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.textContent = message;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(16px)";
    toast.style.transition = "all 0.25s ease";
    setTimeout(() => toast.remove(), 250);
  }, 3200);
}
