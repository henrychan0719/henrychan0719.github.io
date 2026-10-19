# 專題頁內容出處

以下頁碼是 PDF 的實際頁序。網頁摘要為原報告的濃縮整理；並未重新執行實驗。

| 專題 | 核心來源 | 摘要頁保留的比較條件 |
| --- | --- | --- |
| KalMed-UNet | PDF 第 6 頁摘要；第 19 頁圖 3；第 32–33 頁表 5–7；第 35 頁圖 5 | KiTS23 公開訓練集 489 例、1,000 epochs、五折內部交叉驗證。表 7 的成本與單折 250 epochs 分數分開處理；不由 GFLOPs 推定加速。 |
| Swin-TK | PDF 第 6 頁摘要；第 18 頁圖 2；第 33 頁表 10；第 39–40 頁表 15–16；第 42 頁圖 14 | FLARE22 標註訓練資料 50 例，每折 40／10。完整配置包含額外深監督與不確定度損失；主 DSC 和 NSD 來源沿用表 10，不混合另一評估流程的 DSC。 |
| YOLO-CFR / LDS | PDF 第 2 頁摘要；第 17 頁圖 3；第 29–31 頁量測、切分與表 16–17；第 32 頁圖 9；第 37–41 頁部署與限制 | 三種子、100 epochs；Pi 5 CPU／FP32／NCNN 純推論中位數；FLOPs 採 PNNX 摘要。保留 val/test 重用及輸出分支差異。 |
| TopoNet | PDF 第 2 頁摘要；第 18 頁圖 2；第 34–36 頁表 21–24；第 40 頁圖 15 | 增強 DOINN 與 TopoNet 同於 MixSet 訓練；相同 571 橋接參考事件、三次訓練平均。194 個未擾動 cell 的結果另列；原版與增強 DOINN 不混為同一基準。 |

## 圖片對照

| 網站圖片 | 原始圖表 |
| --- | --- |
| `assets/projects/kalmed-architecture.png` | KalMed-UNet 圖 3 |
| `assets/projects/kalmed-result.jpg` | KalMed-UNet 圖 5 |
| `assets/projects/swin-architecture.png` | Swin-TK 圖 2 |
| `assets/projects/swin-tk-architecture.svg` / `.png` | 依 Swin-TK 第 3.1–3.4 節、表 4 及公式 (6)–(10) 重繪。五層解碼器的尺寸以 96³ 輸入為例；P 為正值融合狀態，不宣稱真實共變異數或物理時間濾波。 |
| `assets/projects/swin-result.jpg` | Swin-TK 圖 14（開發階段示例） |
| `assets/projects/yolo-architecture.png` | YOLO 圖 3 |
| `assets/projects/yolo-results.png` | YOLO 圖 9 |
| `assets/projects/toponet-architecture.png` | 微影報告圖 2 |
| `assets/projects/toponet-result.png` | 微影報告圖 15 |

報告封面均標示中華民國 115 年 10 月；網頁僅標示 2026 年專題報告，未據此宣稱正式出版或錄取。

## 個人資料與論文狀態

首頁開頭、「關於我」、ISPACS 2026 TPC Reviewer 身分與錄取資訊依本人於本次修改確認的資料更新。FoR-Net 接受日期為 2026-08-15，會議為 ISPACS 2026；MambaPSA 與 G-Mamba 接受日期為 2026-09-11，會議為 IET ICETA 2026。已接受與正式出版區分處理，未新增 proceedings DOI、頁碼或未提供的出版資料。原有 arXiv 引用及歷史消息保留。

## 正在進行的研究

- PNSE：依提供的《PNSE 工業異常檢測研究計畫書》概述正常狀態估計、正常外觀變動與缺陷辨識。標示訓練與驗證中，不將計畫目標當作已達成成果。
- RANO：依提供的 `RANO_research_plan.md` 概述串流 LiDAR 稀疏節點記憶、位姿對齊與跨幀更新。初步消融與完整逐點評估不混為最終成果。
- ARC-SSM：依提供的 v0.3 方法文件概述記憶保留與資訊寫入控制。目前任務為文件二值化／OCR 前處理，不宣稱已輸出 OCR 文字辨識結果。

上述研究計畫僅整理為首頁簡介，未將研究計畫全文加入公開網站檔案包。
