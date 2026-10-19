# 部署與換網域

此網站使用純 HTML／CSS／JavaScript。**先上 GitHub Pages，之後買網域再接 Cloudflare DNS**，即可符合目前的規劃。買網域、存放程式碼和網站託管是三件不同的事。

| 方案 | 原始碼 | 網站託管 | Cloudflare 的角色 |
| --- | --- | --- | --- |
| 建議起點：GitHub Pages + Cloudflare DNS | GitHub | GitHub Pages | 日後購買網域、管理 DNS |
| 另一種選擇：Cloudflare Pages | GitHub | Cloudflare Pages | 託管網站、管理網域與 DNS |

不需要同時開啟兩種 Pages 託管，也不必先買網域才能預覽線上網站。以下操作需要你在自己的帳號完成；本檔案不代表已部署。

## 1. 先使用 GitHub Pages

1. 若要網址為 `https://henrychan0719.github.io/`，建立名稱為 `henrychan0719.github.io` 的儲存庫。若用其他名稱，例如 `portfolio`，預設網址會是 `https://henrychan0719.github.io/portfolio/`。
2. 將 `gb` **裡面的全部內容**放進儲存庫根目錄，讓 `index.html` 直接位於根目錄；保留 `.nojekyll`。
3. 在本機 `gb` 目錄，依實際位置執行下方其中一行，然後一併上傳更新後的檔案：

   ```bash
   python scripts/configure_site.py https://henrychan0719.github.io/
   ```

   若儲存庫為 `portfolio`：

   ```bash
   python scripts/configure_site.py https://henrychan0719.github.io/portfolio/
   ```

4. 在 GitHub 儲存庫的 **Settings → Pages**，選擇 **Deploy from a branch → main → /(root)**，儲存並等待部署完成。帳號方案需支援該儲存庫的 Pages；一般公開儲存庫即可使用。
5. 以 GitHub 顯示的實際網址檢查首頁、內頁、圖片與 PDF。

## 2. 買好網域後，用 Cloudflare DNS 接 GitHub Pages

以下 `example.com` 都是範例，請換成你實際擁有的網域。

1. 先在 GitHub 帳號 **Settings → Pages** 驗證網域，依 GitHub 顯示的值在 Cloudflare 加入 TXT 記錄。
2. 在網站儲存庫 **Settings → Pages → Custom domain** 填入主要網域，例如 `example.com`，儲存。
3. 在 Cloudflare DNS 設定下列記錄。首次設定建議使用 **DNS only（灰雲）**，讓連線直接到 GitHub Pages，方便確認 DNS 與 GitHub 的 HTTPS 憑證。

   | Type | Name | Content |
   | --- | --- | --- |
   | A | `@` | `185.199.108.153` |
   | A | `@` | `185.199.109.153` |
   | A | `@` | `185.199.110.153` |
   | A | `@` | `185.199.111.153` |
   | CNAME | `www` | `henrychan0719.github.io` |

   `www` 的目標不含 `https://` 或儲存庫路徑。這組設定同時提供主網域與 `www`；以 GitHub Pages 的 Custom domain 決定主要網址。若既有相同名稱的記錄指向舊網站，請依官方說明處理衝突；不要更動無關的郵件記錄。

4. 待 GitHub 確認 DNS 並完成憑證後，勾選 **Enforce HTTPS**。
5. 更新本機網站網址，再把變更推送至 GitHub：

   ```bash
   python scripts/configure_site.py https://example.com/ --write-cname
   ```

   `--write-cname` 會建立只含網域名稱的 `CNAME`，適用此處的「從分支發布」方式；仍需完成前述 GitHub 與 DNS 設定。

## 3. 如果改選 Cloudflare Pages

將同一份原始碼放在 GitHub，於 Cloudflare **Workers & Pages → Create application → Pages → Import an existing Git repository** 連接該儲存庫。選擇：

| 設定 | 值 |
| --- | --- |
| Framework preset | None |
| Production branch | `main` |
| Build command | `exit 0` |
| Build output directory | `.`（`index.html` 位於儲存庫根目錄時） |

若儲存庫保留外層 `gb/`，輸出目錄改為 `gb`。首次部署會取得 `*.pages.dev` 網址；以實際網址執行設定工具，再推送一次更新。

日後到該 Pages 專案的 **Custom domains → Set up a domain** 加入個人網域。根網域需使用同帳號的 Cloudflare DNS zone／nameservers；**先在 Pages 加入網域，再依提示設定 DNS**。只手動新增 DNS CNAME 並不足以完成 Pages 綁定。

此方案不使用網站根目錄的 GitHub `CNAME` 檔；若從 GitHub Pages 移轉，可執行：

```bash
python scripts/configure_site.py https://example.com/ --remove-cname
```

若希望往後由 GitHub 推送自動部署，一開始選 Git integration。Direct Upload 專案之後要改成 Git integration，需另外建立專案。

## 網址工具做什麼

```bash
python scripts/configure_site.py https://example.com/ --dry-run
```

加上 `--dry-run` 可先列出變更，不寫入。實際執行時會更新根目錄各 HTML 的 canonical、`og:url`、站內社群預覽圖片網址、JSON-LD 中的站內網址，以及 `sitemap.xml`／`robots.txt`；不改 Google Scholar、GitHub、ORCID 等外部檔案連結，也不會部署或修改 DNS。

- 支援網站根目錄與 GitHub 專案的 `/repo/` 路徑。
- `--write-cname` 僅用於自訂網域的網站根目錄；不要用於 `github.io`、`pages.dev` 或 `/repo/`。
- 切回預設網域或專案路徑時，若有舊 `CNAME`，加上 `--remove-cname`。
- `robots.txt` 只有放在整個網域根目錄時才控制該網域的爬蟲規則；專案網站中的 `/repo/robots.txt` 不具相同效果。
- 社群平台可能快取分享預覽，更新後不一定立即反映。

## 日常維護

更新 HTML／圖片／PDF → 本機預覽 → 推送 GitHub。網域沒變時，不必反覆執行網址工具。若新增根目錄 HTML 頁面，可再執行一次以重建 sitemap。

若更換 Scholar 或 GitHub 帳號，請同步更新 `index.html` 的連結與 JSON-LD `sameAs`、QR 產生腳本中的目的網址，重新產生 QR 圖檔後以手機驗證。只有更換「個人網站網域」時，既有 Scholar／GitHub QR 不需改動。

## 官方文件

核對日期：2026-10-18。平台介面可能調整，以官方文件為準。

- [GitHub：選擇 Pages 發布來源](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
- [GitHub：自訂網域與 DNS 設定](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)
- [GitHub：HTTPS 設定](https://docs.github.com/en/pages/getting-started-with-github-pages/securing-your-github-pages-site-with-https)
- [Cloudflare：DNS Proxy 狀態](https://developers.cloudflare.com/dns/proxy-status/)
- [Cloudflare Pages：靜態 HTML 部署](https://developers.cloudflare.com/pages/framework-guides/deploy-anything/)
- [Cloudflare Pages：自訂網域](https://developers.cloudflare.com/pages/configuration/custom-domains/)
- [Cloudflare Pages：Git integration](https://developers.cloudflare.com/pages/configuration/git-integration/)
- [Cloudflare Pages：Direct Upload](https://developers.cloudflare.com/pages/get-started/direct-upload/)
