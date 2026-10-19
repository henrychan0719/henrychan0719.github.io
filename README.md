# Sheng-Wei Chan · 個人學術網站

更新：2026-10-18。中英文純靜態網站，包含論文、研究專題、完整 PDF 報告，以及 Google Scholar／GitHub 個人檔案入口。無須安裝前端套件或執行建置。

此版本是可上傳的來源檔；尚未替你購買網域、設定 DNS 或發布網站。

## 本機預覽

解壓縮後，在含有 `index.html` 的 `gb` 目錄執行：

```bash
python -m http.server 8000
```

開啟 `http://localhost:8000`。也可直接開啟 `index.html`，但以本機伺服器預覽比較接近部署環境。外部字型與圖示需要網路；QR Code 圖片由網站本身提供。

## 本次改善

- 首頁 Google Scholar／GitHub 檔案卡片，附直接連結、可放大及下載的 QR Code。
- QR Code 指向既有個人檔案，換網站網域時不必重做。
- 各頁共用語言偏好與導覽程式，保留中英文切換。
- 精簡首頁開場，將論文與專題提前；手機改為可展開選單。
- 論文架構圖支援鍵盤開啟與 Esc 關閉；複製網址、信箱與 BibTeX 顯示成功或失敗提示。
- 修復五篇論文的分享摘要被截斷問題，補齊圖片尺寸及延後載入。
- 補齊網址設定工具及 GitHub Pages／Cloudflare 部署說明。
- 保留原有論文、專題成果及 PDF 內容；沒有把投稿中論文改成已發表，也沒有新增未核實的引用數。

QR Code 的用途是跨裝置開啟個人檔案，不是 Scholar／GitHub 頁面截圖。若日後加入平台截圖，請保留擷取日期；數據及版面會隨平台更新。

## 更新位置

| 要修改的內容 | 檔案 |
| --- | --- |
| 個人簡介、論文列表、專題卡片、外部檔案連結 | `index.html` |
| 全站外觀 | `style.css`、`enhancements.css`（本次版面與互動樣式） |
| 頁面載入前的語言偏好 | `preferences.js` |
| 共用導覽、語言切換及互動 | `site.js` |
| 專題樣式 | `projects.css`（互動已整合至 `site.js`） |
| 學術檔案 QR Code | `assets/profiles/google-scholar-qr.svg`、`.png`；`github-qr.svg`、`.png` |
| 重新產生 QR Code | `scripts/generate_qr.py`（需 Python、ReportLab 與 Pillow） |
| 檢查檔案及連結 | `scripts/validate_site.py`（無額外套件） |
| 正式網址及社群預覽網址 | `scripts/configure_site.py`（Python 3.9+，無額外套件） |
| 部署步驟 | `DEPLOYMENT.md` |
| 原始成果數據與圖表出處 | `CONTENT_SOURCES.md` |

中英文文字以 `lang="en"` 與 `lang="zh-Hant"` 分別維護；修改同一項資訊時請同步更新兩種語言。可用 `?lang=zh` 或 `?lang=en` 指定開啟語言。

## 專題及完整報告

| 專題 | 摘要頁 | 完整報告 |
| --- | --- | --- |
| KalMed-UNet | `kalmed-unet.html` | `reports/kalmed-unet-report.pdf` |
| Swin-TransKalman | `swin-tk.html` | `reports/swin-tk-report.pdf` |
| YOLO-CFR / YOLO-LDS | `edge-yolo.html` | `reports/edge-yolo-report.pdf` |
| TopoNet / 神經微影模擬 | `toponet.html` | `reports/toponet-report.pdf` |

PDF 連結中的頁碼以檔案實際頁序為準，能否自動跳頁取決於瀏覽器的 PDF 閱讀器。上傳時保留 `reports/`、`assets/` 及所有 CSS／JS 檔案。

## 發布前確認

正式網址尚未確定，目前網址中保留原檔使用的 `https://henrychan0719.github.io/`。這不是已發布的確認；確定實際部署位置後，依 `DEPLOYMENT.md` 執行網址設定工具。

檢查範圍以本機靜態檔案、連結及腳本檢查為主，尚未完成真實瀏覽器與手機實機驗證。發布前請確認中英文切換、手機選單、QR 放大／下載、PDF、外部檔案連結，並以手機相機各掃描一次兩張 QR Code。
