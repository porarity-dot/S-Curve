# -*- coding: utf-8 -*-
"""
Builder script to generate index.html - Project Planner with S-Curve, Gantt Chart & Task Management
Fixed:
1. Prevent browser freezing on delete/update by guarding canvas drawing when tabs are hidden (width <= 0) and guarding all while/for loops with step/safety bounds.
2. Real-time instant status update when dragging the actual progress slider (oninput updates status badge and percent badge immediately, onchange saves state and updates KPIs).
"""
import os

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Project Planner & S-Curve Dashboard</title>
  <!-- Google Fonts: Prompt & Inter for high quality Thai & English typography -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Prompt:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --font-family: 'Prompt', 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      --bg-body: #f8fafc;
      --bg-card: #ffffff;
      --bg-subtle: #f1f5f9;
      --border-color: #e2e8f0;
      --border-subtle: #edf2f7;
      --text-main: #0f172a;
      --text-muted: #64748b;
      --text-subtle: #94a3b8;
      --primary: #2563eb;
      --primary-hover: #1d4ed8;
      --primary-subtle: #dbeafe;
      --primary-dark: #1e40af;
      --success: #10b981;
      --success-subtle: #d1fae5;
      --warning: #f59e0b;
      --warning-subtle: #fef3c7;
      --danger: #ef4444;
      --danger-hover: #dc2626;
      --danger-subtle: #fee2e2;
      --planned-color: #3b82f6;
      --actual-color: #10b981;
      --forecast-color: #f59e0b;
      --cutoff-color: #ef4444;
      --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
      --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.07), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
      --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -4px rgba(0, 0, 0, 0.04);
      --radius-sm: 6px;
      --radius-md: 10px;
      --radius-lg: 14px;
      --radius-xl: 18px;
    }

    [data-theme="dark"] {
      --bg-body: #0b1120;
      --bg-card: #1e293b;
      --bg-subtle: #334155;
      --border-color: #334155;
      --border-subtle: #1e293b;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --text-subtle: #64748b;
      --primary: #3b82f6;
      --primary-hover: #60a5fa;
      --primary-subtle: #1e3a8a;
      --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.5);
      --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
      --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      font-family: var(--font-family);
      background-color: var(--bg-body);
      color: var(--text-main);
      line-height: 1.5;
      -webkit-font-smoothing: antialiased;
      transition: background-color 0.25s ease, color 0.25s ease;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
      width: 8px;
      height: 8px;
    }
    ::-webkit-scrollbar-track {
      background: var(--bg-subtle);
    }
    ::-webkit-scrollbar-thumb {
      background: var(--text-subtle);
      border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: var(--text-muted);
    }

    /* Container */
    .container {
      max-width: 1480px;
      margin: 0 auto;
      padding: 0 20px;
      width: 100%;
    }

    /* Header Nav */
    header {
      background: var(--bg-card);
      border-bottom: 1px solid var(--border-color);
      position: sticky;
      top: 0;
      z-index: 50;
      box-shadow: var(--shadow-sm);
    }
    .header-content {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 14px 0;
      flex-wrap: wrap;
      gap: 12px;
    }
    .header-left {
      display: flex;
      align-items: center;
      gap: 14px;
    }
    .brand-icon {
      width: 44px;
      height: 44px;
      border-radius: var(--radius-md);
      background: linear-gradient(135deg, #2563eb, #06b6d4);
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-size: 22px;
      box-shadow: 0 4px 10px rgba(37, 99, 235, 0.35);
      flex-shrink: 0;
    }
    .project-title-box h1 {
      font-size: 1.35rem;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 8px;
      color: var(--text-main);
    }
    .project-title-box p {
      font-size: 0.85rem;
      color: var(--text-muted);
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .header-right {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }

    /* Buttons */
    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      font-family: inherit;
      font-size: 0.875rem;
      font-weight: 500;
      padding: 8px 14px;
      border-radius: var(--radius-sm);
      cursor: pointer;
      transition: all 0.15s ease;
      border: 1px solid transparent;
      outline: none;
      white-space: nowrap;
      user-select: none;
    }
    .btn-primary {
      background-color: var(--primary);
      color: white;
      box-shadow: 0 2px 4px rgba(37, 99, 235, 0.25);
    }
    .btn-primary:hover {
      background-color: var(--primary-hover);
      transform: translateY(-1px);
    }
    .btn-secondary {
      background-color: var(--bg-card);
      color: var(--text-main);
      border-color: var(--border-color);
    }
    .btn-secondary:hover {
      background-color: var(--bg-subtle);
    }
    .btn-success {
      background-color: var(--success);
      color: white;
    }
    .btn-success:hover {
      filter: brightness(1.08);
    }
    .btn-danger {
      background-color: var(--danger);
      color: white;
    }
    .btn-danger:hover {
      background-color: var(--danger-hover);
      transform: translateY(-1px);
    }
    .btn-outline-danger {
      background-color: transparent;
      color: var(--danger);
      border-color: var(--danger);
    }
    .btn-outline-danger:hover {
      background-color: var(--danger-subtle);
    }
    .btn-sm {
      padding: 5px 10px;
      font-size: 0.78rem;
      border-radius: 4px;
    }
    .btn-icon {
      padding: 8px;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border-color);
      background: var(--bg-card);
      color: var(--text-main);
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      transition: all 0.15s ease;
    }
    .btn-icon:hover {
      background: var(--bg-subtle);
      border-color: var(--text-subtle);
    }

    /* Date Picker Input in Header */
    .status-date-badge {
      display: flex;
      align-items: center;
      gap: 8px;
      background: var(--bg-subtle);
      border: 1px solid var(--border-color);
      padding: 4px 10px;
      border-radius: var(--radius-md);
      font-size: 0.85rem;
    }
    .status-date-badge label {
      color: var(--text-muted);
      font-weight: 500;
      font-size: 0.8rem;
    }
    .status-date-badge input[type="date"] {
      border: 1px solid var(--border-color);
      background: var(--bg-card);
      color: var(--text-main);
      padding: 4px 8px;
      border-radius: 4px;
      font-family: inherit;
      font-size: 0.82rem;
      outline: none;
      cursor: pointer;
    }

    /* KPI Summary Row */
    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
      gap: 16px;
      margin: 20px 0;
    }
    .kpi-card {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      padding: 16px 18px;
      box-shadow: var(--shadow-sm);
      position: relative;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover {
      transform: translateY(-2px);
      box-shadow: var(--shadow-md);
    }
    .kpi-card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 8px;
    }
    .kpi-title {
      font-size: 0.82rem;
      font-weight: 600;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    .kpi-icon {
      width: 32px;
      height: 32px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 15px;
    }
    .kpi-icon.blue { background: #dbeafe; color: #2563eb; }
    .kpi-icon.green { background: #d1fae5; color: #059669; }
    .kpi-icon.amber { background: #fef3c7; color: #d97706; }
    .kpi-icon.purple { background: #ede9fe; color: #7c3aed; }
    .kpi-icon.cyan { background: #cffafe; color: #0891b2; }

    .kpi-value {
      font-size: 1.85rem;
      font-weight: 700;
      color: var(--text-main);
      line-height: 1.1;
      margin-bottom: 6px;
      display: flex;
      align-items: baseline;
      gap: 4px;
    }
    .kpi-value .unit {
      font-size: 0.95rem;
      font-weight: 500;
      color: var(--text-muted);
    }
    .kpi-footer {
      font-size: 0.8rem;
      color: var(--text-muted);
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 3px 8px;
      border-radius: 20px;
      font-size: 0.75rem;
      font-weight: 600;
      line-height: 1;
    }
    .badge-success { background: var(--success-subtle); color: #065f46; }
    .badge-warning { background: var(--warning-subtle); color: #92400e; }
    .badge-danger { background: var(--danger-subtle); color: #991b1b; }
    .badge-info { background: var(--primary-subtle); color: #1e40af; }
    .badge-neutral { background: var(--bg-subtle); color: var(--text-muted); }

    /* Navigation Tabs */
    .tab-bar {
      display: flex;
      align-items: center;
      gap: 6px;
      border-bottom: 1px solid var(--border-color);
      margin-bottom: 20px;
      overflow-x: auto;
      scrollbar-width: none;
    }
    .tab-bar::-webkit-scrollbar { display: none; }
    .tab-btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 10px 18px;
      font-family: inherit;
      font-size: 0.92rem;
      font-weight: 500;
      color: var(--text-muted);
      background: transparent;
      border: none;
      border-bottom: 2px solid transparent;
      cursor: pointer;
      transition: all 0.2s ease;
      white-space: nowrap;
    }
    .tab-btn:hover {
      color: var(--primary);
    }
    .tab-btn.active {
      color: var(--primary);
      font-weight: 600;
      border-bottom-color: var(--primary);
    }

    /* Tab Contents */
    .tab-content {
      display: none;
    }
    .tab-content.active {
      display: block;
      animation: fadeIn 0.2s ease;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(4px); }
      to { opacity: 1; transform: translateY(0); }
    }

    /* Main Chart Card */
    .chart-panel {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      padding: 20px;
      box-shadow: var(--shadow-sm);
      margin-bottom: 24px;
    }
    .chart-panel-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 12px;
      margin-bottom: 18px;
      padding-bottom: 14px;
      border-bottom: 1px solid var(--border-color);
    }
    .chart-title-area h2 {
      font-size: 1.15rem;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .chart-title-area p {
      font-size: 0.82rem;
      color: var(--text-muted);
      margin-top: 2px;
    }
    .chart-controls {
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }
    .chart-legend {
      display: flex;
      align-items: center;
      gap: 16px;
      flex-wrap: wrap;
      font-size: 0.85rem;
    }
    .legend-item {
      display: flex;
      align-items: center;
      gap: 6px;
      cursor: pointer;
      user-select: none;
    }
    .legend-line {
      width: 18px;
      height: 4px;
      border-radius: 2px;
    }
    .legend-line.planned { background-color: var(--planned-color); }
    .legend-line.actual { background-color: var(--actual-color); }
    .legend-line.forecast { background: repeating-linear-gradient(90deg, var(--forecast-color), var(--forecast-color) 4px, transparent 4px, transparent 8px); }
    .legend-line.cutoff { background-color: var(--cutoff-color); }

    /* Canvas Wrapper */
    .canvas-container {
      position: relative;
      width: 100%;
      height: 440px;
      user-select: none;
    }
    canvas {
      display: block;
      width: 100%;
      height: 100%;
      cursor: crosshair;
    }

    /* Floating Tooltip */
    #chart-tooltip {
      position: absolute;
      background: rgba(15, 23, 42, 0.94);
      color: #ffffff;
      padding: 10px 14px;
      border-radius: 8px;
      font-size: 0.82rem;
      pointer-events: none;
      box-shadow: 0 10px 25px rgba(0,0,0,0.3);
      display: none;
      z-index: 100;
      min-width: 180px;
      backdrop-filter: blur(4px);
      border: 1px solid rgba(255,255,255,0.1);
      transform: translate(-50%, -115%);
      transition: opacity 0.1s ease;
    }
    #chart-tooltip .tooltip-date {
      font-weight: 600;
      border-bottom: 1px solid rgba(255,255,255,0.2);
      padding-bottom: 5px;
      margin-bottom: 6px;
      color: #93c5fd;
    }
    #chart-tooltip .tooltip-row {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 3px;
    }
    #chart-tooltip .tooltip-row.variance {
      border-top: 1px dashed rgba(255,255,255,0.2);
      margin-top: 6px;
      padding-top: 4px;
      font-weight: 600;
    }

    /* Performance Breakdown Table */
    .variance-table-card {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      padding: 20px;
      margin-bottom: 24px;
      box-shadow: var(--shadow-sm);
    }
    .variance-table-card h3 {
      font-size: 1rem;
      font-weight: 600;
      margin-bottom: 14px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .perf-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 16px;
    }
    .perf-box {
      background: var(--bg-subtle);
      border-radius: var(--radius-md);
      padding: 14px 16px;
      border: 1px solid var(--border-color);
    }
    .perf-box-title {
      font-size: 0.8rem;
      font-weight: 600;
      color: var(--text-muted);
      margin-bottom: 6px;
    }
    .perf-box-desc {
      font-size: 0.88rem;
      color: var(--text-main);
    }

    /* Gantt Chart Container */
    .gantt-wrapper {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      box-shadow: var(--shadow-sm);
      overflow: hidden;
      margin-bottom: 24px;
    }
    .gantt-toolbar {
      padding: 14px 20px;
      border-bottom: 1px solid var(--border-color);
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 12px;
      background: var(--bg-card);
    }
    .gantt-scroll-area {
      position: relative;
      overflow-x: auto;
      overflow-y: visible;
      max-height: 680px;
    }
    .gantt-table {
      border-collapse: collapse;
      width: 100%;
      min-width: 900px;
    }
    .gantt-table th, .gantt-table td {
      border: 1px solid var(--border-color);
      padding: 6px 8px;
      font-size: 0.8rem;
    }
    .gantt-task-col {
      width: 320px;
      min-width: 300px;
      position: sticky;
      left: 0;
      background: var(--bg-card);
      z-index: 20;
      box-shadow: 2px 0 5px rgba(0,0,0,0.04);
    }
    .gantt-header-row {
      background: var(--bg-subtle);
      position: sticky;
      top: 0;
      z-index: 25;
    }
    .gantt-timeline-cell {
      padding: 0 !important;
      position: relative;
      height: 38px;
      vertical-align: middle;
    }
    .gantt-bar-container {
      position: relative;
      height: 24px;
      margin: 2px 0;
    }
    .gantt-planned-bar {
      position: absolute;
      top: 2px;
      height: 18px;
      background-color: #e0e7ff;
      border: 1px solid #a5b4fc;
      border-radius: 4px;
      z-index: 1;
      opacity: 0.85;
    }
    [data-theme="dark"] .gantt-planned-bar {
      background-color: #312e81;
      border-color: #4f46e5;
    }
    .gantt-actual-bar {
      position: absolute;
      top: 5px;
      height: 12px;
      background: linear-gradient(90deg, #10b981, #059669);
      border-radius: 3px;
      z-index: 2;
      box-shadow: 0 1px 3px rgba(16, 185, 129, 0.4);
    }

    /* Task Management Table */
    .task-table-wrapper {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      box-shadow: var(--shadow-sm);
      overflow: hidden;
      margin-bottom: 24px;
    }
    .task-table-toolbar {
      padding: 16px 20px;
      border-bottom: 1px solid var(--border-color);
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 12px;
    }
    .search-filter-group {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
      flex: 1;
    }
    .search-input {
      padding: 8px 12px;
      border: 1px solid var(--border-color);
      background: var(--bg-body);
      color: var(--text-main);
      border-radius: var(--radius-sm);
      font-family: inherit;
      font-size: 0.85rem;
      min-width: 220px;
      outline: none;
    }
    .search-input:focus {
      border-color: var(--primary);
    }
    .filter-select {
      padding: 8px 12px;
      border: 1px solid var(--border-color);
      background: var(--bg-body);
      color: var(--text-main);
      border-radius: var(--radius-sm);
      font-family: inherit;
      font-size: 0.85rem;
      outline: none;
      cursor: pointer;
    }
    .task-table-responsive {
      overflow-x: auto;
      max-height: 720px;
    }
    .task-table {
      width: 100%;
      border-collapse: collapse;
      text-align: left;
    }
    .task-table th {
      background: var(--bg-subtle);
      color: var(--text-muted);
      font-weight: 600;
      font-size: 0.8rem;
      padding: 12px 12px;
      border-bottom: 1px solid var(--border-color);
      position: sticky;
      top: 0;
      z-index: 10;
      white-space: nowrap;
    }
    .task-table td {
      padding: 10px 12px;
      border-bottom: 1px solid var(--border-color);
      font-size: 0.85rem;
      vertical-align: middle;
    }
    .task-table tr:hover {
      background-color: var(--bg-subtle);
    }
    .category-row {
      background-color: var(--bg-subtle) !important;
      font-weight: 600;
      color: var(--primary);
    }
    .progress-slider-cell {
      display: flex;
      align-items: center;
      gap: 8px;
      min-width: 140px;
    }
    .progress-slider {
      flex: 1;
      height: 6px;
      -webkit-appearance: none;
      appearance: none;
      background: var(--border-color);
      border-radius: 3px;
      outline: none;
      cursor: pointer;
    }
    .progress-slider::-webkit-slider-thumb {
      -webkit-appearance: none;
      appearance: none;
      width: 16px;
      height: 16px;
      border-radius: 50%;
      background: var(--primary);
      cursor: pointer;
      box-shadow: 0 1px 3px rgba(0,0,0,0.3);
    }
    .progress-pct-badge {
      font-weight: 600;
      font-size: 0.8rem;
      min-width: 44px;
      text-align: right;
    }

    /* Modal Styles */
    .modal-overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(15, 23, 42, 0.6);
      backdrop-filter: blur(4px);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 200;
      padding: 20px;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.2s ease;
    }
    .modal-overlay.open {
      opacity: 1;
      pointer-events: auto;
    }
    .modal-card {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      width: 100%;
      max-width: 600px;
      max-height: 90vh;
      overflow-y: auto;
      box-shadow: var(--shadow-lg);
      transform: translateY(12px) scale(0.98);
      transition: all 0.2s ease;
    }
    .modal-overlay.open .modal-card {
      transform: translateY(0) scale(1);
    }
    .modal-header {
      padding: 16px 22px;
      border-bottom: 1px solid var(--border-color);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .modal-header h3 {
      font-size: 1.15rem;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .modal-body {
      padding: 20px 22px;
    }
    .modal-footer {
      padding: 14px 22px;
      border-top: 1px solid var(--border-color);
      display: flex;
      align-items: center;
      justify-content: flex-end;
      gap: 10px;
      background: var(--bg-subtle);
    }
    .form-group {
      margin-bottom: 16px;
    }
    .form-group label {
      display: block;
      font-size: 0.85rem;
      font-weight: 600;
      margin-bottom: 6px;
      color: var(--text-main);
    }
    .form-control {
      width: 100%;
      padding: 9px 12px;
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
      background: var(--bg-body);
      color: var(--text-main);
      font-family: inherit;
      font-size: 0.88rem;
      outline: none;
    }
    .form-control:focus {
      border-color: var(--primary);
      box-shadow: 0 0 0 2px var(--primary-subtle);
    }
    .form-row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
    }

    /* Toast Notification */
    .toast {
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: #1e293b;
      color: #ffffff;
      padding: 12px 20px;
      border-radius: 8px;
      font-size: 0.88rem;
      font-weight: 500;
      box-shadow: 0 10px 25px rgba(0,0,0,0.3);
      display: flex;
      align-items: center;
      gap: 10px;
      transform: translateY(100px);
      opacity: 0;
      transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
      z-index: 300;
    }
    .toast.show {
      transform: translateY(0);
      opacity: 1;
    }

    /* Print Styles */
    @media print {
      header, .tab-bar, .chart-controls, .btn, .status-date-badge input, .search-filter-group, .task-actions-col, #th-select-all, .task-checkbox {
        display: none !important;
      }
      body {
        background: white !important;
        color: black !important;
      }
      .container {
        max-width: 100% !important;
        padding: 0 !important;
      }
      .kpi-card, .chart-panel, .gantt-wrapper, .task-table-wrapper {
        box-shadow: none !important;
        border: 1px solid #ccc !important;
        page-break-inside: avoid;
      }
      .canvas-container {
        height: 380px !important;
      }
    }

    /* Responsive */
    @media (max-width: 768px) {
      .header-content {
        flex-direction: column;
        align-items: flex-start;
      }
      .header-right {
        width: 100%;
        justify-content: space-between;
      }
      .form-row {
        grid-template-columns: 1fr;
      }
      .canvas-container {
        height: 320px;
      }
    }
  </style>
</head>
<body data-theme="light">

  <!-- Header Navigation -->
  <header>
    <div class="container">
      <div class="header-content">
        <div class="header-left">
          <div class="brand-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 3v18h18"/>
              <path d="m19 9-5 5-4-4-3 3"/>
            </svg>
          </div>
          <div class="project-title-box">
            <h1 id="lbl-project-name">PVCell Project
              <button class="btn-icon btn-sm" onclick="openProjectSettingsModal()" title="แก้ไขข้อมูลโครงการ">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
              </button>
            </h1>
            <p>
              <span>ผู้รับผิดชอบหลัก: <strong id="lbl-project-lead" style="color:var(--text-main);">STeP & TSUS</strong></span>
              <span>•</span>
              <span id="lbl-project-date-range">2024-07-25 ถึง 2025-01-19</span>
            </p>
          </div>
        </div>

        <div class="header-right">
          <!-- Status Date Selector -->
          <div class="status-date-badge" title="กำหนดวันประเมินผลความคืบหน้า (As-of Date)">
            <label for="status-date-input">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="vertical-align:middle;margin-right:2px;"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
              วันประเมินผล:
            </label>
            <input type="date" id="status-date-input" onchange="onStatusDateChange(this.value)">
          </div>

          <!-- New Project Button -->
          <button class="btn btn-secondary" onclick="openNewProjectModal()" title="สร้างโครงการใหม่ (ล้างรายการงานและตั้งค่าโปรเจกต์ใหม่)">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="12" y1="18" x2="12" y2="12"/><line x1="9" y1="15" x2="15" y2="15"/></svg>
            ✨ สร้างโครงการใหม่
          </button>

          <!-- Add Task Button -->
          <button class="btn btn-primary" onclick="openTaskModal(null)">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
            เพิ่มงานใหม่
          </button>

          <!-- Export JSON -->
          <button class="btn btn-secondary" onclick="exportDataJSON()" title="สำรองข้อมูลเป็น JSON">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            ส่งออก
          </button>

          <!-- Import JSON -->
          <button class="btn btn-secondary" onclick="triggerImportJSON()" title="นำเข้าข้อมูลจาก JSON">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
            นำเข้า
          </button>
          <input type="file" id="json-file-input" style="display:none;" accept=".json" onchange="importDataJSON(event)">

          <!-- Export CSV -->
          <button class="btn btn-secondary" onclick="exportToCSV()" title="ส่งออกเป็น Excel / CSV">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
            CSV
          </button>

          <!-- Theme Toggle -->
          <button class="btn-icon" onclick="toggleTheme()" id="theme-toggle-btn" title="เปลี่ยนธีม สว่าง/มืด">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
          </button>
        </div>
      </div>
    </div>
  </header>

  <!-- Main Content Container -->
  <main class="container" style="flex: 1; padding-top: 10px; padding-bottom: 40px;">

    <!-- KPI Summary Row -->
    <section class="kpi-grid">
      <!-- KPI 1: Project Timeline -->
      <div class="kpi-card">
        <div class="kpi-card-header">
          <span class="kpi-title">ระยะเวลาโครงการ</span>
          <div class="kpi-icon blue">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
          </div>
        </div>
        <div class="kpi-value" id="kpi-days-elapsed">0 <span class="unit">/ 0 วัน</span></div>
        <div class="kpi-footer">
          <span>เริ่มงานไปแล้ว</span>
          <strong id="kpi-time-pct" style="color:var(--primary);">0.0%</strong>
          <span id="kpi-project-span" style="margin-left:auto; font-size:0.75rem;"></span>
        </div>
      </div>

      <!-- KPI 2: Planned Progress -->
      <div class="kpi-card">
        <div class="kpi-card-header">
          <span class="kpi-title">แผนงานสะสม (Planned)</span>
          <div class="kpi-icon cyan">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
          </div>
        </div>
        <div class="kpi-value" id="kpi-planned-pct">0.0 <span class="unit">%</span></div>
        <div class="kpi-footer">
          <span>เป้าหมายตามแผนงาน ณ วันที่รายงาน</span>
        </div>
      </div>

      <!-- KPI 3: Actual Progress -->
      <div class="kpi-card">
        <div class="kpi-card-header">
          <span class="kpi-title">งานจริงสะสม (Actual)</span>
          <div class="kpi-icon green">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
          </div>
        </div>
        <div class="kpi-value" id="kpi-actual-pct">0.0 <span class="unit">%</span></div>
        <div class="kpi-footer">
          <span>ผลงานที่ส่งมอบและทำได้จริง</span>
        </div>
      </div>

      <!-- KPI 4: Schedule Variance -->
      <div class="kpi-card">
        <div class="kpi-card-header">
          <span class="kpi-title">สถานะความก้าวหน้า (Variance)</span>
          <div class="kpi-icon amber" id="kpi-status-icon">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
          </div>
        </div>
        <div class="kpi-value" id="kpi-variance-val">0.0 <span class="unit">%</span></div>
        <div class="kpi-footer">
          <span id="kpi-variance-badge" class="badge badge-success">ตรงตามแผนงาน</span>
          <span id="kpi-days-variance" style="margin-left:auto; font-weight:600;">0 วัน</span>
        </div>
      </div>

      <!-- KPI 5: Site Manpower -->
      <div class="kpi-card">
        <div class="kpi-card-header">
          <span class="kpi-title">กำลังคนหน้างาน (Manpower)</span>
          <div class="kpi-icon purple">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
          </div>
        </div>
        <div class="kpi-value" id="kpi-manpower-total">0 <span class="unit">Man-days</span></div>
        <div class="kpi-footer">
          <span>เฉลี่ย: <strong id="kpi-manpower-avg">0</strong> คน/วัน</span>
          <span style="margin-left:auto;">สูงสุด: <strong id="kpi-manpower-max">0</strong> คน</span>
        </div>
      </div>
    </section>

    <!-- Navigation Tabs -->
    <nav class="tab-bar">
      <button class="tab-btn active" onclick="switchTab('tab-scurve')">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>
        กราฟ S-Curve & ตัวชี้วัด
      </button>
      <button class="tab-btn" onclick="switchTab('tab-gantt')">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
        แผนภูมิแกนต์ (Gantt Chart)
      </button>
      <button class="tab-btn" onclick="switchTab('tab-tasks')">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>
        รายการงานทั้งหมด (<span id="tab-task-count">0</span>)
      </button>
      <button class="tab-btn" onclick="switchTab('tab-manpower')">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/></svg>
        บันทึกคนงาน & งานประจำวัน
      </button>
    </nav>

    <!-- TAB 1: S-CURVE & METRICS -->
    <section id="tab-scurve" class="tab-content active">
      <div class="chart-panel">
        <div class="chart-panel-header">
          <div class="chart-title-area">
            <h2>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color:var(--primary);"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>
              กราฟเปรียบเทียบความก้าวหน้าโครงการ (Project S-Curve)
            </h2>
            <p>เปรียบเทียบผลงานสะสมตามแผนงาน (Planned) และผลงานทำได้จริง (Actual) พร้อมเส้นคาดการณ์ (Forecast)</p>
          </div>
          <div class="chart-controls">
            <div class="chart-legend">
              <div class="legend-item" onclick="toggleCurve('planned')">
                <span class="legend-line planned"></span>
                <span>แผนงานสะสม (Planned)</span>
              </div>
              <div class="legend-item" onclick="toggleCurve('actual')">
                <span class="legend-line actual"></span>
                <span>ทำจริงสะสม (Actual)</span>
              </div>
              <div class="legend-item" onclick="toggleCurve('forecast')">
                <span class="legend-line forecast"></span>
                <span>คาดการณ์ (Forecast)</span>
              </div>
              <div class="legend-item">
                <span class="legend-line cutoff"></span>
                <span>วันประเมินผล</span>
              </div>
            </div>

            <div style="display:flex; gap:6px;">
              <select id="sel-chart-interval" class="filter-select" onchange="renderCharts()">
                <option value="daily">แสดงผล: รายวัน (Daily)</option>
                <option value="weekly">แสดงผล: รายสัปดาห์ (Weekly)</option>
              </select>
              <button class="btn btn-secondary btn-sm" onclick="downloadChartImage()" title="บันทึกกราฟเป็นไฟล์ภาพ PNG">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                บันทึกภาพ
              </button>
            </div>
          </div>
        </div>

        <!-- Canvas Container -->
        <div class="canvas-container" id="canvas-container">
          <canvas id="scurve-canvas"></canvas>
          <div id="chart-tooltip"></div>
        </div>
      </div>

      <!-- Variance Breakdown Analysis -->
      <div class="variance-table-card">
        <h3>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color:var(--primary);"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
          การวิเคราะห์ประสิทธิภาพงานเชิงวิศวกรรม (Earned Value & Schedule Performance)
        </h3>
        <div class="perf-grid">
          <div class="perf-box">
            <div class="perf-box-title">SCHEDULE VARIANCE (SV - ค่าเบี่ยงเบนตารางงาน)</div>
            <div class="perf-box-desc" id="perf-sv-desc">คำนวณผลงานจริงเทียบกับแผนงาน</div>
          </div>
          <div class="perf-box">
            <div class="perf-box-title">SCHEDULE PERFORMANCE INDEX (SPI - ดัชนีตารางงาน)</div>
            <div class="perf-box-desc" id="perf-spi-desc">อัตราส่วนประสิทธิภาพการทำงานจริงเทียบกับแผน</div>
          </div>
          <div class="perf-box">
            <div class="perf-box-title">EARNED SCHEDULE (ระยะเวลาผลงานเทียบเท่า)</div>
            <div class="perf-box-desc" id="perf-es-desc">การประเมินระยะเวลาที่ผลงานจริงแล้วเสร็จเทียบเท่ากับแผน</div>
          </div>
        </div>
      </div>
    </section>

    <!-- TAB 2: GANTT CHART -->
    <section id="tab-gantt" class="tab-content">
      <div class="gantt-wrapper">
        <div class="gantt-toolbar">
          <div style="display:flex; align-items:center; gap:12px;">
            <h3 style="font-size:1.05rem; font-weight:600;">แผนภูมิแกนต์และไทม์ไลน์โครงการ (Gantt Chart)</h3>
            <span class="badge badge-info" id="gantt-item-count">0 รายการ</span>
          </div>
          <div style="display:flex; align-items:center; gap:8px;">
            <select id="gantt-category-filter" class="filter-select" onchange="renderGantt()">
              <option value="ALL">ทุกหมวดหมู่งาน</option>
            </select>
            <button class="btn btn-secondary btn-sm" onclick="scrollGanttToToday()">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
              ไปที่วันประเมิน
            </button>
          </div>
        </div>

        <div class="gantt-scroll-area" id="gantt-scroll-container">
          <table class="gantt-table" id="gantt-table">
            <thead id="gantt-thead">
              <!-- Dynamically populated -->
            </thead>
            <tbody id="gantt-tbody">
              <!-- Dynamically populated -->
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- TAB 3: TASK MANAGEMENT -->
    <section id="tab-tasks" class="tab-content">
      <div class="task-table-wrapper">
        <div class="task-table-toolbar">
          <div class="search-filter-group">
            <input type="text" id="task-search-input" class="search-input" placeholder="🔍 ค้นหาชื่องาน หรือผู้รับผิดชอบ..." oninput="filterTasks()">
            <select id="task-category-filter" class="filter-select" onchange="filterTasks()">
              <option value="ALL">ทุกหมวดหมู่งาน (All Categories)</option>
            </select>
            <select id="task-status-filter" class="filter-select" onchange="filterTasks()">
              <option value="ALL">ทุกสถานะ (All Statuses)</option>
              <option value="completed">เสร็จสมบูรณ์ (100%)</option>
              <option value="in_progress">กำลังดำเนินการ (1-99%)</option>
              <option value="not_started">ยังไม่เริ่ม (0%)</option>
              <option value="delayed">ล่าช้ากว่าแผน</option>
            </select>
          </div>

          <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
            <!-- Batch Delete Button (shown when items checked) -->
            <button class="btn btn-danger btn-sm" id="btn-batch-delete" onclick="deleteSelectedTasks()" style="display:none;" title="ลบรายการงานที่เลือก">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
              ลบที่เลือก (<span id="batch-delete-count">0</span>)
            </button>

            <!-- Clear All Tasks Button (For starting a new job) -->
            <button class="btn btn-outline-danger btn-sm" onclick="clearAllTasks()" title="ลบรายการงานทั้งหมดในตารางเพื่อเริ่มงานใหม่">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>
              ลบงานทั้งหมด (Clear All)
            </button>

            <!-- Auto-Calculate Weights -->
            <button class="btn btn-secondary btn-sm" onclick="autoCalculateWeights()" title="คำนวณสัดส่วนน้ำหนักงานอัตโนมัติตามระยะเวลา (Duration)">
              ⚖️ คำนวณน้ำหนักอัตโนมัติ
            </button>

            <!-- Add Task Button -->
            <button class="btn btn-primary btn-sm" onclick="openTaskModal(null)">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
              เพิ่มงานใหม่
            </button>
          </div>
        </div>

        <div class="task-table-responsive">
          <table class="task-table" id="task-list-table">
            <thead>
              <tr>
                <th style="width: 36px; text-align:center;">
                  <input type="checkbox" id="th-select-all" onchange="toggleSelectAllTasks(this.checked)" title="เลือกทั้งหมด">
                </th>
                <th style="width: 40px;">#</th>
                <th>หมวดหมู่</th>
                <th>รายการงาน</th>
                <th>ผู้รับผิดชอบ</th>
                <th>แผน: เริ่ม - จบ</th>
                <th style="text-align:center;">ระยะเวลา</th>
                <th>ทำจริง: เริ่ม - จบ</th>
                <th style="min-width: 170px;">ความคืบหน้าจริง (% Actual)</th>
                <th style="text-align:right;">น้ำหนัก</th>
                <th style="text-align:center; min-width:110px;">สถานะ</th>
                <th class="task-actions-col" style="text-align:center; width:90px;">จัดการ</th>
              </tr>
            </thead>
            <tbody id="task-tbody">
              <!-- Dynamically populated -->
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- TAB 4: MANPOWER & DAILY LOG -->
    <section id="tab-manpower" class="tab-content">
      <div class="chart-panel" style="margin-bottom: 20px;">
        <div class="chart-panel-header">
          <div class="chart-title-area">
            <h2>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color:var(--primary);"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/></svg>
              กราฟจำนวนผู้เข้าปฏิบัติงานหน้างาน (Daily Site Headcount)
            </h2>
            <p>บันทึกและติดตามสถิติผู้เข้าปฏิบัติงานประจำวัน เพื่อเปรียบเทียบกับอัตราความก้าวหน้าของโครงการ</p>
          </div>
          <div>
            <button class="btn btn-primary btn-sm" onclick="openAddDailyLogModal()">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
              บันทึกคนงานประจำวัน
            </button>
          </div>
        </div>

        <div class="canvas-container" style="height: 280px;">
          <canvas id="manpower-canvas"></canvas>
        </div>
      </div>

      <!-- Daily Log Table -->
      <div class="task-table-wrapper">
        <div class="task-table-toolbar">
          <h3 style="font-size:1.05rem; font-weight:600;">บันทึกรายงานหน้างานประจำวัน (Site Daily Logs)</h3>
          <span class="badge badge-info" id="manpower-log-count">0 รายการ</span>
        </div>
        <div class="task-table-responsive">
          <table class="task-table">
            <thead>
              <tr>
                <th style="width: 120px;">วันที่</th>
                <th style="width: 140px; text-align:center;">จำนวนคนงาน (คน)</th>
                <th>กิจกรรม / รายการงานที่ทำจริงประจำวัน</th>
                <th>อุปสรรค / ปัญหา / สภาพอากาศ</th>
                <th style="text-align:center; width:90px;">จัดการ</th>
              </tr>
            </thead>
            <tbody id="manpower-tbody">
              <!-- Dynamically populated -->
            </tbody>
          </table>
        </div>
      </div>
    </section>

  </main>

  <!-- MODAL: ADD / EDIT TASK -->
  <div class="modal-overlay" id="task-modal">
    <div class="modal-card">
      <div class="modal-header">
        <h3 id="task-modal-title">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color:var(--primary);"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          เพิ่ม / แก้ไขรายการงาน
        </h3>
        <button class="btn-icon btn-sm" onclick="closeTaskModal()">✕</button>
      </div>
      <div class="modal-body">
        <input type="hidden" id="modal-task-id">

        <div class="form-group">
          <label for="modal-task-name">ชื่องาน (Task Name) *</label>
          <input type="text" id="modal-task-name" class="form-control" placeholder="เช่น ติดตั้งแผงโซล่าร์เซลล์ อาคาร A" required>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="modal-task-category">หมวดหมู่งาน (Category) *</label>
            <input type="text" id="modal-task-category" class="form-control" placeholder="เช่น Initial Project, Solar Panel" list="category-datalist" required>
            <datalist id="category-datalist"></datalist>
          </div>
          <div class="form-group">
            <label for="modal-task-assigned">ผู้รับผิดชอบ (Assigned To)</label>
            <input type="text" id="modal-task-assigned" class="form-control" placeholder="เช่น นายสมชาย, ทีมช่าง ก">
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="modal-task-pstart">วันที่เริ่มตามแผน (Planned Start) *</label>
            <input type="date" id="modal-task-pstart" class="form-control" required onchange="calculateModalDuration()">
          </div>
          <div class="form-group">
            <label for="modal-task-pend">วันที่สิ้นสุดตามแผน (Planned End) *</label>
            <input type="date" id="modal-task-pend" class="form-control" required onchange="calculateModalDuration()">
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="modal-task-duration">ระยะเวลาตามแผน (วัน)</label>
            <input type="number" id="modal-task-duration" class="form-control" readonly style="background:var(--bg-subtle);">
          </div>
          <div class="form-group">
            <label for="modal-task-weight">น้ำหนักงาน (% Weight)</label>
            <input type="number" id="modal-task-weight" class="form-control" step="0.1" min="0" placeholder="คำนวณอัตโนมัติหากเว้นว่าง">
          </div>
        </div>

        <hr style="border:0; border-top:1px solid var(--border-color); margin: 16px 0;">

        <div style="font-weight:600; font-size:0.9rem; margin-bottom:12px; color:var(--primary);">
          ผลการดำเนินงานจริง (Actual Performance)
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="modal-task-astart">วันที่เริ่มทำจริง (Actual Start)</label>
            <input type="date" id="modal-task-astart" class="form-control">
          </div>
          <div class="form-group">
            <label for="modal-task-aend">วันที่แล้วเสร็จจริง (Actual End)</label>
            <input type="date" id="modal-task-aend" class="form-control">
          </div>
        </div>

        <div class="form-group">
          <label for="modal-task-progress">ความคืบหน้างานจริง (% Actual Progress): <strong id="modal-task-progress-val">0</strong>%</label>
          <input type="range" id="modal-task-progress" class="progress-slider" min="0" max="100" value="0" oninput="document.getElementById('modal-task-progress-val').innerText = this.value">
        </div>

        <div class="form-group">
          <label for="modal-task-notes">หมายเหตุ / บันทึกหน้างาน</label>
          <textarea id="modal-task-notes" class="form-control" rows="2" placeholder="รายละเอียดเพิ่มเติมหรือปัญหาที่พบ..."></textarea>
        </div>
      </div>
      <div class="modal-footer">
        <!-- Delete Task from inside modal -->
        <button class="btn btn-danger btn-sm" id="btn-modal-delete-task" onclick="deleteTaskFromModal()" style="margin-right:auto; display:none;">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
          ลบงานนี้ (Delete)
        </button>

        <button class="btn btn-secondary" onclick="closeTaskModal()">ยกเลิก</button>
        <button class="btn btn-primary" onclick="saveTaskModal()">บันทึกรายการ</button>
      </div>
    </div>
  </div>

  <!-- MODAL: CREATE NEW PROJECT -->
  <div class="modal-overlay" id="new-project-modal">
    <div class="modal-card">
      <div class="modal-header">
        <h3>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color:var(--primary);"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="12" y1="18" x2="12" y2="12"/><line x1="9" y1="15" x2="15" y2="15"/></svg>
          สร้างโครงการใหม่ (Create New Project)
        </h3>
        <button class="btn-icon btn-sm" onclick="closeNewProjectModal()">✕</button>
      </div>
      <div class="modal-body">
        <p style="font-size:0.85rem; color:var(--text-muted); margin-bottom:16px;">
          ตั้งค่าข้อมูลสำหรับโครงการใหม่ของคุณ และสามารถเลือกล้างรายการงานเดิมเพื่อเริ่มต้นทำงานใหม่ได้ทันที
        </p>

        <div class="form-group">
          <label for="new-project-name">ชื่อโครงการใหม่ (Project Name) *</label>
          <input type="text" id="new-project-name" class="form-control" placeholder="เช่น โครงการก่อสร้างโรงงานระยะที่ 2" required>
        </div>

        <div class="form-group">
          <label for="new-project-lead">ผู้รับผิดชอบหลัก / หน่วยงาน (Project Lead / Contractor)</label>
          <input type="text" id="new-project-lead" class="form-control" placeholder="เช่น บริษัท เอ็นจิเนียริ่ง จำกัด">
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="new-project-start">วันเริ่มต้นโครงการ (Start Date) *</label>
            <input type="date" id="new-project-start" class="form-control" required>
          </div>
          <div class="form-group">
            <label for="new-project-end">วันสิ้นสุดโครงการ (End Date) *</label>
            <input type="date" id="new-project-end" class="form-control" required>
          </div>
        </div>

        <div style="margin-top:16px; padding:12px; background:var(--bg-subtle); border-radius:var(--radius-sm); border:1px solid var(--border-color);">
          <label style="display:flex; align-items:center; gap:8px; cursor:pointer; font-weight:600; font-size:0.88rem; color:var(--danger);">
            <input type="checkbox" id="new-project-clear-tasks" checked style="width:16px; height:16px; accent-color:var(--danger); cursor:pointer;">
            ลบรายการงานและบันทึกประจำวันเดิมทั้งหมด (เริ่มโปรเจกต์ว่างสำหรับงานใหม่)
          </label>
          <div style="font-size:0.75rem; color:var(--text-muted); margin-top:4px; margin-left:24px;">
            * หากต้องการตัวอย่างโครงการ PVCell Project กลับคืนมา คุณสามารถกดปุ่ม "รีเซ็ตข้อมูลตัวอย่าง" ได้เสมอ
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" onclick="closeNewProjectModal()">ยกเลิก</button>
        <button class="btn btn-primary" onclick="submitNewProjectModal()">
          🚀 เริ่มต้นโครงการใหม่
        </button>
      </div>
    </div>
  </div>

  <!-- MODAL: PROJECT SETTINGS -->
  <div class="modal-overlay" id="project-modal">
    <div class="modal-card">
      <div class="modal-header">
        <h3>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color:var(--primary);"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
          ตั้งค่าข้อมูลโครงการ (Project Settings)
        </h3>
        <button class="btn-icon btn-sm" onclick="closeProjectSettingsModal()">✕</button>
      </div>
      <div class="modal-body">
        <div class="form-group">
          <label for="cfg-project-name">ชื่อโครงการ (Project Name) *</label>
          <input type="text" id="cfg-project-name" class="form-control" required>
        </div>

        <div class="form-group">
          <label for="cfg-project-lead">ผู้รับผิดชอบหลัก / บริษัท (Project Lead / Contractor) *</label>
          <input type="text" id="cfg-project-lead" class="form-control" required>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="cfg-project-start">วันเริ่มต้นโครงการ (Project Start Date)</label>
            <input type="date" id="cfg-project-start" class="form-control">
          </div>
          <div class="form-group">
            <label for="cfg-project-end">วันสิ้นสุดโครงการ (Project End Date)</label>
            <input type="date" id="cfg-project-end" class="form-control">
          </div>
        </div>

        <div class="form-group">
          <label for="cfg-weight-mode">วิธีคำนวณค่าน้ำหนักงาน (Weight Mode)</label>
          <select id="cfg-weight-mode" class="form-control">
            <option value="duration">คำนวณตามสัดส่วนระยะเวลาทำงาน (Duration Proportional)</option>
            <option value="manual">กำหนดเองอิสระในแต่ละรายการงาน (Manual Weight %)</option>
          </select>
        </div>

        <div style="margin-top:20px; padding:12px; background:var(--bg-subtle); border-radius:var(--radius-sm); font-size:0.82rem; color:var(--text-muted);">
          <div style="font-weight:600; color:var(--text-main); margin-bottom:6px;">🛠️ จัดการข้อมูลโครงการ:</div>
          <div style="display:flex; gap:8px; flex-wrap:wrap; margin-top:8px;">
            <button class="btn btn-outline-danger btn-sm" onclick="clearAllTasks(); closeProjectSettingsModal();">
              🗑️ ลบรายการงานทั้งหมด (Clear Tasks)
            </button>
            <button class="btn btn-secondary btn-sm" onclick="resetToSampleData()">
              🔄 กู้คืนตัวอย่าง PVCell Project
            </button>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" onclick="closeProjectSettingsModal()">ยกเลิก</button>
        <button class="btn btn-primary" onclick="saveProjectSettingsModal()">บันทึกการตั้งค่า</button>
      </div>
    </div>
  </div>

  <!-- MODAL: ADD DAILY LOG -->
  <div class="modal-overlay" id="daily-log-modal">
    <div class="modal-card">
      <div class="modal-header">
        <h3>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color:var(--primary);"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/></svg>
          บันทึกคนงาน & รายงานหน้างานประจำวัน
        </h3>
        <button class="btn-icon btn-sm" onclick="closeDailyLogModal()">✕</button>
      </div>
      <div class="modal-body">
        <input type="hidden" id="modal-log-id">
        <div class="form-row">
          <div class="form-group">
            <label for="modal-log-date">วันที่เข้าปฏิบัติงาน *</label>
            <input type="date" id="modal-log-date" class="form-control" required>
          </div>
          <div class="form-group">
            <label for="modal-log-workers">จำนวนผู้เข้าหน้างาน (คน) *</label>
            <input type="number" id="modal-log-workers" class="form-control" min="0" required placeholder="เช่น 4">
          </div>
        </div>

        <div class="form-group">
          <label for="modal-log-activity">กิจกรรม / งานที่ปฏิบัติได้จริง</label>
          <textarea id="modal-log-activity" class="form-control" rows="2" placeholder="เช่น ติดตั้งโครงสร้างแผงโซล่าร์ อาคาร A ได้ 10 ชุด"></textarea>
        </div>

        <div class="form-group">
          <label for="modal-log-notes">อุปสรรค / ปัญหา / สภาพอากาศ</label>
          <input type="text" id="modal-log-notes" class="form-control" placeholder="เช่น ฝนตกช่วงบ่าย 1 ชม.">
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" onclick="closeDailyLogModal()">ยกเลิก</button>
        <button class="btn btn-primary" onclick="saveDailyLogModal()">บันทึกข้อมูล</button>
      </div>
    </div>
  </div>

  <!-- Toast Notification element -->
  <div class="toast" id="toast-msg">
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
    <span id="toast-text">บันทึกข้อมูลสำเร็จ</span>
  </div>

  <!-- APPLICATION JAVASCRIPT LOGIC -->
  <script>
    /* =========================================================
       INITIAL DATA (Extracted from User PVCell Project CSV)
       ========================================================= */
    const DEFAULT_PROJECT = {
      name: "PVCell Project",
      lead: "STeP & TSUS",
      startDate: "2024-07-25",
      endDate: "2025-01-19",
      statusDate: "2024-11-09",
      weightMode: "duration"
    };

    const DEFAULT_TASKS = [
      // 1. Initial Project
      { id: "T001", category: "Initial Project", name: "ขออนุมัติเอกสารของโครงการ", assignedTo: "Gokce Aslan", plannedStart: "2024-07-25", plannedEnd: "2024-07-30", duration: 6, actualStart: "2024-07-25", actualEnd: "2024-07-31", progress: 100, weight: 1.5, notes: "" },
      { id: "T002", category: "Initial Project", name: "รื้อถอนอุปกรณ์เดิม", assignedTo: "Hayden Cook", plannedStart: "2024-07-30", plannedEnd: "2024-08-06", duration: 8, actualStart: "2024-07-30", actualEnd: "2024-08-07", progress: 100, weight: 2.0, notes: "" },
      { id: "T003", category: "Initial Project", name: "รื้อถอนโครงสร้าง - อาคาร A", assignedTo: "Jens Martensson", plannedStart: "2024-08-06", plannedEnd: "2024-08-12", duration: 7, actualStart: "2024-08-06", actualEnd: "2024-08-09", progress: 100, weight: 1.8, notes: "" },
      { id: "T004", category: "Initial Project", name: "รื้อถอนโครงสร้าง - อาคาร B", assignedTo: "Jens Martensson", plannedStart: "2024-08-12", plannedEnd: "2024-08-18", duration: 7, actualStart: "2024-08-12", actualEnd: "2024-08-19", progress: 100, weight: 1.8, notes: "" },
      { id: "T005", category: "Initial Project", name: "รื้อถอนโครงสร้าง - อาคาร C", assignedTo: "Jens Martensson", plannedStart: "2024-08-18", plannedEnd: "2024-08-24", duration: 7, actualStart: "2024-08-18", actualEnd: "2024-08-25", progress: 100, weight: 1.8, notes: "" },
      { id: "T006", category: "Initial Project", name: "รื้อถอนโครงสร้าง - อาคาร D", assignedTo: "Jens Martensson", plannedStart: "2024-08-24", plannedEnd: "2024-08-30", duration: 7, actualStart: "2024-08-24", actualEnd: "2024-08-31", progress: 100, weight: 1.8, notes: "" },

      // 2. Installation Solar Equipment System
      { id: "T007", category: "Installation Solar Equipment System", name: "ติดตั้งทางเดิน CatWalk - อาคาร A", assignedTo: "Gokce Aslan", plannedStart: "2024-08-25", plannedEnd: "2024-08-28", duration: 4, actualStart: "2024-08-25", actualEnd: "2024-08-29", progress: 100, weight: 1.2, notes: "" },
      { id: "T008", category: "Installation Solar Equipment System", name: "ติดตั้งทางเดิน CatWalk - อาคาร B", assignedTo: "Gokce Aslan", plannedStart: "2024-08-28", plannedEnd: "2024-08-31", duration: 4, actualStart: "2024-08-28", actualEnd: "2024-09-01", progress: 100, weight: 1.2, notes: "" },
      { id: "T009", category: "Installation Solar Equipment System", name: "ติดตั้งทางเดิน CatWalk - อาคาร C", assignedTo: "Gokce Aslan", plannedStart: "2024-08-31", plannedEnd: "2024-09-03", duration: 4, actualStart: "2024-08-31", actualEnd: "2024-09-04", progress: 100, weight: 1.2, notes: "" },
      { id: "T010", category: "Installation Solar Equipment System", name: "ติดตั้งทางเดิน CatWalk - อาคาร D", assignedTo: "Gokce Aslan", plannedStart: "2024-09-03", plannedEnd: "2024-09-05", duration: 3, actualStart: "2024-09-03", actualEnd: "2024-09-06", progress: 100, weight: 1.0, notes: "" },

      { id: "T011", category: "Installation Solar Equipment System", name: "ติดตั้งอุปกรณ์ฐานรองรับแผง - อาคาร A", assignedTo: "Hayden Cook", plannedStart: "2024-09-05", plannedEnd: "2024-09-07", duration: 3, actualStart: "2024-09-05", actualEnd: "2024-09-08", progress: 100, weight: 1.0, notes: "" },
      { id: "T012", category: "Installation Solar Equipment System", name: "ติดตั้งอุปกรณ์ฐานรองรับแผง - อาคาร B", assignedTo: "Hayden Cook", plannedStart: "2024-09-07", plannedEnd: "2024-09-09", duration: 3, actualStart: "2024-09-07", actualEnd: "2024-09-10", progress: 100, weight: 1.0, notes: "" },
      { id: "T013", category: "Installation Solar Equipment System", name: "ติดตั้งอุปกรณ์ฐานรองรับแผง - อาคาร C", assignedTo: "Hayden Cook", plannedStart: "2024-09-09", plannedEnd: "2024-09-11", duration: 3, actualStart: "2024-09-09", actualEnd: "2024-09-12", progress: 100, weight: 1.0, notes: "" },
      { id: "T014", category: "Installation Solar Equipment System", name: "ติดตั้งอุปกรณ์ฐานรองรับแผง - อาคาร D", assignedTo: "Hayden Cook", plannedStart: "2024-09-11", plannedEnd: "2024-09-15", duration: 5, actualStart: "2024-09-11", actualEnd: "2024-09-16", progress: 100, weight: 1.5, notes: "" },

      { id: "T015", category: "Installation Solar Equipment System", name: "ติดตั้งอุปกรณ์รางรองรับแผง - อาคาร A", assignedTo: "Hayden Cook", plannedStart: "2024-09-15", plannedEnd: "2024-09-17", duration: 3, actualStart: "2024-09-15", actualEnd: "2024-09-18", progress: 100, weight: 1.0, notes: "" },
      { id: "T016", category: "Installation Solar Equipment System", name: "ติดตั้งอุปกรณ์รางรองรับแผง - อาคาร B", assignedTo: "Hayden Cook", plannedStart: "2024-09-17", plannedEnd: "2024-09-19", duration: 3, actualStart: "2024-09-17", actualEnd: "2024-09-20", progress: 100, weight: 1.0, notes: "" },
      { id: "T017", category: "Installation Solar Equipment System", name: "ติดตั้งอุปกรณ์รางรองรับแผง - อาคาร C", assignedTo: "Hayden Cook", plannedStart: "2024-09-19", plannedEnd: "2024-09-21", duration: 3, actualStart: "2024-09-19", actualEnd: "2024-09-22", progress: 100, weight: 1.0, notes: "" },
      { id: "T018", category: "Installation Solar Equipment System", name: "ติดตั้งอุปกรณ์รางรองรับแผง - อาคาร D", assignedTo: "Hayden Cook", plannedStart: "2024-09-21", plannedEnd: "2024-09-25", duration: 5, actualStart: "2024-09-21", actualEnd: "2024-09-26", progress: 100, weight: 1.5, notes: "" },

      { id: "T019", category: "Installation Solar Equipment System", name: "ติดตั้งอุปกรณ์ประกอบสายไฟ - อาคาร A", assignedTo: "Hayden Cook", plannedStart: "2024-09-25", plannedEnd: "2024-09-26", duration: 2, actualStart: "2024-09-25", actualEnd: "2024-09-27", progress: 100, weight: 0.8, notes: "" },
      { id: "T020", category: "Installation Solar Equipment System", name: "ติดตั้งอุปกรณ์ประกอบสายไฟ - อาคาร B", assignedTo: "Hayden Cook", plannedStart: "2024-09-26", plannedEnd: "2024-09-27", duration: 2, actualStart: "2024-09-26", actualEnd: "2024-09-27", progress: 0, weight: 0.8, notes: "รอย้ายจุดติดตั้ง" },
      { id: "T021", category: "Installation Solar Equipment System", name: "ติดตั้งอุปกรณ์ประกอบสายไฟ - อาคาร C", assignedTo: "Hayden Cook", plannedStart: "2024-09-27", plannedEnd: "2024-09-28", duration: 2, actualStart: "2024-09-27", actualEnd: "2024-09-29", progress: 100, weight: 0.8, notes: "" },
      { id: "T022", category: "Installation Solar Equipment System", name: "ติดตั้งอุปกรณ์ประกอบสายไฟ - อาคาร D", assignedTo: "Hayden Cook", plannedStart: "2024-09-28", plannedEnd: "2024-09-30", duration: 3, actualStart: "2024-09-28", actualEnd: "2024-10-01", progress: 100, weight: 1.0, notes: "" },

      // 3. Installation Carpark
      { id: "T023", category: "Installation Carpark", name: "ปรับฐานราก พื้น และงานลงเสา", assignedTo: "Gokce Aslan", plannedStart: "2024-09-15", plannedEnd: "2024-09-25", duration: 11, actualStart: "2024-09-15", actualEnd: "2024-09-26", progress: 100, weight: 2.8, notes: "" },
      { id: "T024", category: "Installation Carpark", name: "งานเชื่อมประกอบ โครงสร้าง และหลังคา", assignedTo: "Hayden Cook", plannedStart: "2024-09-25", plannedEnd: "2024-09-30", duration: 6, actualStart: "2024-09-25", actualEnd: "2024-10-01", progress: 100, weight: 1.8, notes: "" },
      { id: "T025", category: "Installation Carpark", name: "ติดตั้งอุปกรณ์ฐานรองรับแผง (โรงรถ)", assignedTo: "Jens Martensson", plannedStart: "2024-09-30", plannedEnd: "2024-10-10", duration: 11, actualStart: "2024-09-30", actualEnd: "2024-10-11", progress: 100, weight: 2.5, notes: "" },
      { id: "T026", category: "Installation Carpark", name: "ติดตั้งอุปกรณ์รางรองรับแผง (โรงรถ)", assignedTo: "Nuria Acevedo", plannedStart: "2024-09-30", plannedEnd: "2024-10-10", duration: 11, actualStart: "2024-09-30", actualEnd: "2024-10-11", progress: 100, weight: 2.5, notes: "" },
      { id: "T027", category: "Installation Carpark", name: "ติดตั้งอุปกรณ์ประกอบสายไฟ (โรงรถ)", assignedTo: "Olivia Wilson", plannedStart: "2024-09-30", plannedEnd: "2024-10-10", duration: 11, actualStart: "2024-09-30", actualEnd: "2024-10-11", progress: 100, weight: 2.5, notes: "" },

      // 4. Installation Old Solar Panel
      { id: "T028", category: "Installation Old Solar Panel", name: "ติดตั้งแผงผลิตไฟฟ้าพลังงานแสงอาทิตย์เดิม", assignedTo: "Gokce Aslan", plannedStart: "2024-10-05", plannedEnd: "2024-10-12", duration: 8, actualStart: "2024-10-05", actualEnd: "2024-10-13", progress: 100, weight: 2.0, notes: "" },
      { id: "T029", category: "Installation Old Solar Panel", name: "ติดตั้ง Inverter โรงรถ ใหม่", assignedTo: "Hayden Cook", plannedStart: "2024-10-05", plannedEnd: "2024-10-12", duration: 8, actualStart: "2024-10-05", actualEnd: "2024-10-13", progress: 100, weight: 2.0, notes: "" },

      // 5. Installation Solar Panel
      { id: "T030", category: "Installation Solar Panel", name: "ติดตั้งระบบไฟฟ้าฝั่ง DC - อาคาร A", assignedTo: "Gokce Aslan", plannedStart: "2024-10-15", plannedEnd: "2024-10-20", duration: 6, actualStart: "2024-10-15", actualEnd: "2024-10-21", progress: 100, weight: 1.8, notes: "" },
      { id: "T031", category: "Installation Solar Panel", name: "ติดตั้งระบบไฟฟ้าฝั่ง DC - อาคาร B", assignedTo: "Gokce Aslan", plannedStart: "2024-10-20", plannedEnd: "2024-10-25", duration: 6, actualStart: "2024-10-20", actualEnd: "2024-10-26", progress: 100, weight: 1.8, notes: "" },
      { id: "T032", category: "Installation Solar Panel", name: "ติดตั้งระบบไฟฟ้าฝั่ง DC - อาคาร C", assignedTo: "Gokce Aslan", plannedStart: "2024-10-25", plannedEnd: "2024-10-30", duration: 6, actualStart: "2024-10-25", actualEnd: "2024-10-31", progress: 100, weight: 1.8, notes: "" },
      { id: "T033", category: "Installation Solar Panel", name: "ติดตั้งระบบไฟฟ้าฝั่ง DC - อาคาร D", assignedTo: "Gokce Aslan", plannedStart: "2024-10-30", plannedEnd: "2024-11-04", duration: 6, actualStart: "2024-10-30", actualEnd: "2024-11-05", progress: 100, weight: 1.8, notes: "" },

      { id: "T034", category: "Installation Solar Panel", name: "ติดตั้งระบบไฟฟ้าฝั่ง AC - อาคาร A", assignedTo: "Hayden Cook", plannedStart: "2024-10-30", plannedEnd: "2024-11-04", duration: 6, actualStart: "2024-10-30", actualEnd: "2024-11-05", progress: 100, weight: 1.8, notes: "" },
      { id: "T035", category: "Installation Solar Panel", name: "ติดตั้งระบบไฟฟ้าฝั่ง AC - อาคาร B", assignedTo: "Hayden Cook", plannedStart: "2024-11-04", plannedEnd: "2024-11-09", duration: 6, actualStart: "2024-11-04", actualEnd: "2024-11-10", progress: 100, weight: 1.8, notes: "" },
      { id: "T036", category: "Installation Solar Panel", name: "ติดตั้งระบบไฟฟ้าฝั่ง AC - อาคาร C", assignedTo: "Hayden Cook", plannedStart: "2024-11-09", plannedEnd: "2024-11-14", duration: 6, actualStart: "2024-11-09", actualEnd: "", progress: 60, weight: 1.8, notes: "กำลังเดินสายไฟ" },
      { id: "T037", category: "Installation Solar Panel", name: "ติดตั้งระบบไฟฟ้าฝั่ง AC - อาคาร D", assignedTo: "Hayden Cook", plannedStart: "2024-11-14", plannedEnd: "2024-11-19", duration: 6, actualStart: "", actualEnd: "", progress: 0, weight: 1.8, notes: "" },

      { id: "T038", category: "Installation Solar Panel", name: "ส่งมอบแผงผลิตพลังงานแสงอาทิตย์ - อาคาร A", assignedTo: "Jens Martensson", plannedStart: "2024-11-10", plannedEnd: "2024-11-12", duration: 3, actualStart: "2024-11-09", actualEnd: "", progress: 50, weight: 1.0, notes: "แผงเข้าหน้างานแล้ว" },
      { id: "T039", category: "Installation Solar Panel", name: "ส่งมอบแผงผลิตพลังงานแสงอาทิตย์ - อาคาร B", assignedTo: "Jens Martensson", plannedStart: "2024-11-12", plannedEnd: "2024-11-14", duration: 3, actualStart: "", actualEnd: "", progress: 0, weight: 1.0, notes: "" },
      { id: "T040", category: "Installation Solar Panel", name: "ส่งมอบแผงผลิตพลังงานแสงอาทิตย์ - อาคาร C", assignedTo: "Jens Martensson", plannedStart: "2024-11-14", plannedEnd: "2024-11-16", duration: 3, actualStart: "", actualEnd: "", progress: 0, weight: 1.0, notes: "" },
      { id: "T041", category: "Installation Solar Panel", name: "ส่งมอบแผงผลิตพลังงานแสงอาทิตย์ - อาคาร D", assignedTo: "Jens Martensson", plannedStart: "2024-11-16", plannedEnd: "2024-11-17", duration: 2, actualStart: "", actualEnd: "", progress: 0, weight: 0.8, notes: "" },

      { id: "T042", category: "Installation Solar Panel", name: "ส่งมอบอินเวอร์เตอร์เข้าหน้างาน", assignedTo: "Nuria Acevedo", plannedStart: "2024-11-15", plannedEnd: "2024-11-22", duration: 8, actualStart: "", actualEnd: "", progress: 0, weight: 2.2, notes: "" },
      { id: "T043", category: "Installation Solar Panel", name: "ติดตั้งแผงผลิตไฟฟ้าพลังงานแสงอาทิตย์", assignedTo: "ทีมช่างติดตั้ง", plannedStart: "2024-11-20", plannedEnd: "2024-12-04", duration: 15, actualStart: "", actualEnd: "", progress: 0, weight: 4.5, notes: "" },
      { id: "T044", category: "Installation Solar Panel", name: "ติดตั้งอินเวอร์เตอร์", assignedTo: "ทีมช่างติดตั้ง", plannedStart: "2024-12-05", plannedEnd: "2024-12-12", duration: 8, actualStart: "", actualEnd: "", progress: 0, weight: 2.5, notes: "" },
      { id: "T045", category: "Installation Solar Panel", name: "ติดตั้งระบบกันย้อนและเชื่อมต่อเข้ากับอาคาร", assignedTo: "วิศวกรโครงการ", plannedStart: "2024-12-10", plannedEnd: "2024-12-17", duration: 8, actualStart: "", actualEnd: "", progress: 0, weight: 2.5, notes: "" },
      { id: "T046", category: "Installation Solar Panel", name: "ดำเนินการทดสอบระบบ (Commissioning)", assignedTo: "วิศวกรโครงการ", plannedStart: "2024-12-18", plannedEnd: "2025-01-01", duration: 15, actualStart: "", actualEnd: "", progress: 0, weight: 4.0, notes: "" },
      { id: "T047", category: "Installation Solar Panel", name: "อบรมการใช้งานและส่งมอบงาน", assignedTo: "STeP & TSUS", plannedStart: "2025-01-02", plannedEnd: "2025-01-09", duration: 8, actualStart: "", actualEnd: "", progress: 0, weight: 2.0, notes: "" }
    ];

    const DEFAULT_DAILY_LOGS = [
      { id: "L001", date: "2024-07-25", workers: 0, activity: "เริ่มโครงการ ขออนุมัติเอกสาร", notes: "สภาพอากาศแจ่มใส" },
      { id: "L002", date: "2024-07-26", workers: 0, activity: "เตรียมการหน้างาน", notes: "ปกติ" },
      { id: "L003", date: "2024-07-27", workers: 0, activity: "วันหยุดประจำสัปดาห์", notes: "-" },
      { id: "L004", date: "2024-07-28", workers: 0, activity: "วันหยุดประจำสัปดาห์", notes: "-" },
      { id: "L005", date: "2024-07-29", workers: 0, activity: "ประสานงานเจ้าหน้าที่", notes: "-" },
      { id: "L006", date: "2024-07-30", workers: 0, activity: "อนุมัติเอกสารเรียบร้อย", notes: "-" },
      { id: "L007", date: "2024-07-31", workers: 7, activity: "ทีมรื้อถอนเข้าพื้นที่ อาคาร A และ B", notes: "ฝนตกเล็กน้อยช่วงบ่าย" },
      { id: "L008", date: "2024-08-01", workers: 7, activity: "รื้อถอนอุปกรณ์เดิมต่อเนื่อง", notes: "ปกติ" },
      { id: "L009", date: "2024-08-02", workers: 4, activity: "ขนย้ายวัสดุออกจากพื้นที่", notes: "-" },
      { id: "L010", date: "2024-08-05", workers: 4, activity: "รื้อถอนโครงสร้าง อาคาร A", notes: "ปกติ" },
      { id: "L011", date: "2024-08-06", workers: 4, activity: "รื้อถอนโครงสร้าง อาคาร A ต่อเนื่อง", notes: "ปกติ" },
      { id: "L012", date: "2024-08-07", workers: 7, activity: "รื้อถอนโครงสร้าง อาคาร B", notes: "อากาศร้อนจัด" },
      { id: "L013", date: "2024-08-08", workers: 7, activity: "รื้อถอนโครงสร้าง อาคาร B ต่อเนื่อง", notes: "ปกติ" },
      { id: "L014", date: "2024-08-15", workers: 4, activity: "ปรับฐานรากและโครงสร้าง", notes: "ปกติ" },
      { id: "L015", date: "2024-08-16", workers: 4, activity: "งานประกอบโครงเหล็ก", notes: "ปกติ" },
      { id: "L016", date: "2024-08-25", workers: 4, activity: "เริ่มติดตั้งทางเดิน CatWalk", notes: "ติดตั้ง Safety Line" },
      { id: "L017", date: "2024-09-05", workers: 4, activity: "ติดตั้งอุปกรณ์ฐานรองรับแผง อาคาร A", notes: "ปกติ" },
      { id: "L018", date: "2024-09-15", workers: 4, activity: "ติดตั้งรางรองรับแผง และเริ่มงาน Carpark", notes: "ปกติ" },
      { id: "L019", date: "2024-09-25", workers: 4, activity: "เชื่อมประกอบโครงสร้างโรงรถ", notes: "ปกติ" },
      { id: "L020", date: "2024-10-05", workers: 3, activity: "ติดตั้งแผงผลิตไฟฟ้าเดิมและ Inverter โรงรถ", notes: "ปกติ" },
      { id: "L021", date: "2024-10-15", workers: 4, activity: "เริ่มงานระบบไฟฟ้าฝั่ง DC อาคาร A", notes: "ปกติ" },
      { id: "L022", date: "2024-10-30", workers: 4, activity: "เริ่มงานระบบไฟฟ้าฝั่ง AC อาคาร A", notes: "ปกติ" },
      { id: "L023", date: "2024-11-09", workers: 3, activity: "ตรวจรับแผงและติดตั้ง AC อาคาร C", notes: "สถานะปัจจุบัน" }
    ];

    /* =========================================================
       APPLICATION STATE & LOCAL STORAGE
       ========================================================= */
    const STORAGE_KEY = "AGY_PROJECT_PLANNER_DATA";

    let state = {
      project: Object.assign({}, DEFAULT_PROJECT),
      tasks: JSON.parse(JSON.stringify(DEFAULT_TASKS)),
      dailyLogs: JSON.parse(JSON.stringify(DEFAULT_DAILY_LOGS)),
      activeTab: "tab-scurve",
      chartSettings: {
        showPlanned: true,
        showActual: true,
        showForecast: true,
        interval: "daily"
      },
      taskFilters: {
        search: "",
        category: "ALL",
        status: "ALL"
      }
    };

    function loadState() {
      try {
        const saved = localStorage.getItem(STORAGE_KEY);
        if (saved) {
          const parsed = JSON.parse(saved);
          if (parsed && parsed.project && Array.isArray(parsed.tasks)) {
            state.project = parsed.project;
            state.tasks = parsed.tasks;
            if (Array.isArray(parsed.dailyLogs)) state.dailyLogs = parsed.dailyLogs;
          }
        }
      } catch (e) {
        console.warn("Could not load local storage", e);
      }
    }

    function saveState() {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify({
          project: state.project,
          tasks: state.tasks,
          dailyLogs: state.dailyLogs
        }));
      } catch (e) {
        console.error("Save error", e);
      }
    }

    function resetToSampleData() {
      if (confirm("คุณต้องการกู้คืนข้อมูลตัวอย่างโครงการ (PVCell Project) กลับมาใช่หรือไม่?")) {
        state.project = Object.assign({}, DEFAULT_PROJECT);
        state.tasks = JSON.parse(JSON.stringify(DEFAULT_TASKS));
        state.dailyLogs = JSON.parse(JSON.stringify(DEFAULT_DAILY_LOGS));
        saveState();
        initApp();
        showToast("กู้คืนข้อมูลตัวอย่าง PVCell Project เรียบร้อยแล้ว");
      }
    }

    /* =========================================================
       DATE UTILITIES
       ========================================================= */
    function parseDate(str) {
      if (!str) return null;
      const parts = str.split("-");
      if (parts.length !== 3) return null;
      return new Date(parseInt(parts[0], 10), parseInt(parts[1], 10) - 1, parseInt(parts[2], 10));
    }

    function formatDate(d) {
      if (!d || isNaN(d.getTime())) return "";
      const year = d.getFullYear();
      const month = String(d.getMonth() + 1).padStart(2, "0");
      const day = String(d.getDate()).padStart(2, "0");
      return `${year}-${month}-${day}`;
    }

    function formatThaiDate(d, short = false) {
      if (!d) return "-";
      if (typeof d === "string") d = parseDate(d);
      if (!d || isNaN(d.getTime())) return "-";

      const monthsTh = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."];
      const day = d.getDate();
      const month = monthsTh[d.getMonth()];
      const year = d.getFullYear();
      return `${day} ${month} ${year}`;
    }

    function diffDays(d1, d2) {
      if (!d1 || !d2) return 0;
      const utc1 = Date.UTC(d1.getFullYear(), d1.getMonth(), d1.getDate());
      const utc2 = Date.UTC(d2.getFullYear(), d2.getMonth(), d2.getDate());
      return Math.round((utc2 - utc1) / (1000 * 60 * 60 * 24));
    }

    function addDays(d, n) {
      const res = new Date(d.getTime());
      res.setDate(res.getDate() + n);
      return res;
    }

    /* =========================================================
       MATHEMATICAL S-CURVE & EARNED SCHEDULE CALCULATIONS
       ========================================================= */
    function normalizeWeights() {
      if (state.tasks.length === 0) return;

      if (state.project.weightMode === "duration") {
        let totalDur = 0;
        state.tasks.forEach(t => {
          const s = parseDate(t.plannedStart);
          const e = parseDate(t.plannedEnd);
          t.duration = (s && e) ? Math.max(1, diffDays(s, e) + 1) : 1;
          totalDur += t.duration;
        });
        if (totalDur > 0) {
          state.tasks.forEach(t => {
            t.weight = parseFloat(((t.duration / totalDur) * 100).toFixed(2));
          });
        }
      } else {
        let sum = state.tasks.reduce((acc, t) => acc + (parseFloat(t.weight) || 0), 0);
        if (sum === 0) {
          state.tasks.forEach(t => t.weight = 1);
        }
      }
    }

    function calculateProjectTimeline() {
      normalizeWeights();

      let pStart = parseDate(state.project.startDate);
      let pEnd = parseDate(state.project.endDate);

      // Expand to encompass all tasks if needed
      state.tasks.forEach(t => {
        const ts = parseDate(t.plannedStart);
        const te = parseDate(t.plannedEnd);
        if (ts && (!pStart || ts < pStart)) pStart = ts;
        if (te && (!pEnd || te > pEnd)) pEnd = te;
      });

      if (!pStart) pStart = new Date();
      if (!pEnd || pEnd < pStart) pEnd = addDays(pStart, 30);

      const statusDate = parseDate(state.project.statusDate) || pStart;

      // Generate date array safely (capped to prevent infinite loop)
      const dates = [];
      let cur = new Date(pStart.getTime());
      let safetyCounter = 0;
      while (cur <= pEnd && safetyCounter < 3650) {
        dates.push(new Date(cur.getTime()));
        cur = addDays(cur, 1);
        safetyCounter++;
      }

      const totalWeight = state.tasks.reduce((sum, t) => sum + (parseFloat(t.weight) || 0), 0) || 100;

      const plannedSeries = [];
      const actualSeries = [];
      const forecastSeries = [];

      dates.forEach(d => {
        const dateStr = formatDate(d);

        // 1. Planned Progress
        let plannedSum = 0;
        state.tasks.forEach(t => {
          const s = parseDate(t.plannedStart);
          const e = parseDate(t.plannedEnd);
          const w = parseFloat(t.weight) || 0;
          if (!s || !e) return;

          let taskPlan = 0;
          if (d < s) {
            taskPlan = 0;
          } else if (d >= e) {
            taskPlan = 100;
          } else {
            const taskDays = diffDays(s, e) + 1;
            const elapsed = diffDays(s, d) + 1;
            taskPlan = Math.min(100, (elapsed / taskDays) * 100);
          }
          plannedSum += (w * taskPlan);
        });
        const plannedPct = Math.min(100, parseFloat((plannedSum / totalWeight).toFixed(2)));
        plannedSeries.push({ date: d, dateStr, plannedPct });

        // 2. Actual Progress (up to statusDate)
        if (d <= statusDate) {
          let actualSum = 0;
          state.tasks.forEach(t => {
            const as = parseDate(t.actualStart) || parseDate(t.plannedStart);
            const ae = parseDate(t.actualEnd) || parseDate(t.plannedEnd);
            const prog = parseFloat(t.progress) || 0;
            const w = parseFloat(t.weight) || 0;
            if (!as) return;

            let taskActual = 0;
            if (prog === 0 || d < as) {
              taskActual = 0;
            } else if (prog >= 100 && ae && d >= ae) {
              taskActual = 100;
            } else {
              const targetEnd = (prog >= 100 && ae) ? ae : statusDate;
              if (d >= targetEnd) {
                taskActual = prog;
              } else {
                const totalSpan = Math.max(1, diffDays(as, targetEnd) + 1);
                const curSpan = Math.max(1, diffDays(as, d) + 1);
                taskActual = Math.min(prog, (curSpan / totalSpan) * prog);
              }
            }
            actualSum += (w * taskActual);
          });
          const actualPct = Math.min(100, parseFloat((actualSum / totalWeight).toFixed(2)));
          actualSeries.push({ date: d, dateStr, actualPct });
        }
      });

      // Status Date metrics
      const currentPlannedItem = plannedSeries.find(item => item.dateStr === state.project.statusDate) || plannedSeries[plannedSeries.length - 1];
      const currentActualItem = actualSeries[actualSeries.length - 1] || { actualPct: 0 };

      const plannedAtStatus = currentPlannedItem ? currentPlannedItem.plannedPct : 0;
      const actualAtStatus = currentActualItem ? currentActualItem.actualPct : 0;
      const variancePct = parseFloat((actualAtStatus - plannedAtStatus).toFixed(2));

      // Earned Schedule (ES)
      let earnedDate = pStart;
      for (let i = 0; i < plannedSeries.length; i++) {
        if (plannedSeries[i].plannedPct >= actualAtStatus) {
          earnedDate = plannedSeries[i].date;
          break;
        }
        if (i === plannedSeries.length - 1) earnedDate = plannedSeries[i].date;
      }
      const daysVariance = diffDays(statusDate, earnedDate);

      // Forecast Series (Guarded to prevent excessive loops)
      if (actualAtStatus > 0 && actualAtStatus < 100) {
        const elapsedDays = Math.max(1, diffDays(pStart, statusDate));
        const ratePerDay = actualAtStatus / elapsedDays;
        const remainingPct = 100 - actualAtStatus;
        const remainingDaysEst = Math.min(1000, Math.max(1, Math.ceil(remainingPct / Math.max(0.05, ratePerDay))));

        forecastSeries.push({ date: statusDate, dateStr: formatDate(statusDate), forecastPct: actualAtStatus });
        let fDate = new Date(statusDate.getTime());
        for (let i = 1; i <= remainingDaysEst; i++) {
          fDate = addDays(fDate, 1);
          const fPct = Math.min(100, parseFloat((actualAtStatus + (i * ratePerDay)).toFixed(2)));
          forecastSeries.push({ date: new Date(fDate.getTime()), dateStr: formatDate(fDate), forecastPct: fPct });
          if (fPct >= 100) break;
        }
      }

      return {
        pStart,
        pEnd,
        statusDate,
        totalDays: diffDays(pStart, pEnd) + 1,
        elapsedDays: Math.max(0, diffDays(pStart, statusDate) + 1),
        dates,
        plannedSeries,
        actualSeries,
        forecastSeries,
        plannedAtStatus,
        actualAtStatus,
        variancePct,
        daysVariance,
        earnedDate
      };
    }

    /* =========================================================
       CANVAS RENDERING ENGINE (High DPI, Smooth S-Curve)
       ========================================================= */
    let chartHoverInfo = null;

    function renderCharts() {
      const timeline = calculateProjectTimeline();
      updateKPICards(timeline);
      drawSCurveCanvas(timeline);
      drawManpowerCanvas();
      renderVarianceAnalysis(timeline);
    }

    function drawSCurveCanvas(timeline) {
      const canvas = document.getElementById("scurve-canvas");
      if (!canvas) return;

      // CRITICAL GUARD: If canvas is hidden (width/height <= 0), skip drawing to prevent zero/negative loop freezes!
      const rect = canvas.parentElement.getBoundingClientRect();
      if (!rect || rect.width <= 0 || rect.height <= 0) {
        return;
      }

      const ctx = canvas.getContext("2d");
      const dpr = window.devicePixelRatio || 1;
      const width = rect.width;
      const height = rect.height;

      canvas.width = width * dpr;
      canvas.height = height * dpr;
      ctx.scale(dpr, dpr);
      ctx.clearRect(0, 0, width, height);

      const pad = { top: 25, right: 35, bottom: 45, left: 55 };
      const plotW = Math.max(10, width - pad.left - pad.right);
      const plotH = Math.max(10, height - pad.top - pad.bottom);

      const isDark = document.body.getAttribute("data-theme") === "dark";
      const gridColor = isDark ? "rgba(255, 255, 255, 0.08)" : "rgba(0, 0, 0, 0.06)";
      const textColor = isDark ? "#94a3b8" : "#64748b";

      // 1. Draw Grid Lines (Y-Axis)
      ctx.lineWidth = 1;
      ctx.font = "11px " + (getComputedStyle(document.body).fontFamily || "sans-serif");
      ctx.textAlign = "right";
      ctx.textBaseline = "middle";

      for (let yPct = 0; yPct <= 100; yPct += 20) {
        const y = pad.top + plotH - (yPct / 100) * plotH;
        ctx.strokeStyle = gridColor;
        ctx.beginPath();
        ctx.moveTo(pad.left, y);
        ctx.lineTo(pad.left + plotW, y);
        ctx.stroke();

        ctx.fillStyle = textColor;
        ctx.fillText(yPct + "%", pad.left - 10, y);
      }

      // If no tasks, show friendly empty guide
      if (state.tasks.length === 0) {
        ctx.fillStyle = isDark ? "#64748b" : "#94a3b8";
        ctx.font = "14px " + (getComputedStyle(document.body).fontFamily || "sans-serif");
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText("ยังไม่มีรายการงานในโครงการ คลิก 'เพิ่มงานใหม่' หรือ 'โหลดตัวอย่าง PVCell' เพื่อเริ่มต้น", width / 2, height / 2);
        return;
      }

      // 2. Draw X-Axis Dates & Ticks (Strictly guarded step >= 1)
      const totalPoints = timeline.dates.length;
      if (totalPoints < 2) return;

      const numTicks = Math.max(1, Math.min(8, Math.floor(plotW / 90)));
      const step = Math.max(1, Math.ceil(totalPoints / numTicks));

      ctx.textAlign = "center";
      ctx.textBaseline = "top";

      for (let i = 0; i < totalPoints; i += step) {
        const x = pad.left + (i / (totalPoints - 1)) * plotW;
        ctx.strokeStyle = gridColor;
        ctx.beginPath();
        ctx.moveTo(x, pad.top);
        ctx.lineTo(x, pad.top + plotH);
        ctx.stroke();

        const d = timeline.dates[i];
        ctx.fillStyle = textColor;
        ctx.fillText(formatThaiDate(d, true), x, pad.top + plotH + 8);
      }

      function getX(d) {
        const diff = diffDays(timeline.pStart, d);
        return pad.left + Math.max(0, Math.min(plotW, (diff / (totalPoints - 1)) * plotW));
      }
      function getY(pct) {
        return pad.top + plotH - (pct / 100) * plotH;
      }

      // 3. Status Date Vertical Line
      const statusX = getX(timeline.statusDate);
      if (statusX >= pad.left && statusX <= pad.left + plotW) {
        ctx.save();
        ctx.setLineDash([5, 4]);
        ctx.strokeStyle = "#ef4444";
        ctx.lineWidth = 1.8;
        ctx.beginPath();
        ctx.moveTo(statusX, pad.top);
        ctx.lineTo(statusX, pad.top + plotH);
        ctx.stroke();

        ctx.setLineDash([]);
        ctx.fillStyle = "#ef4444";
        ctx.beginPath();
        if (typeof ctx.roundRect === "function") {
          ctx.roundRect(statusX - 45, pad.top - 20, 90, 18, 4);
        } else {
          ctx.rect(statusX - 45, pad.top - 20, 90, 18);
        }
        ctx.fill();

        ctx.fillStyle = "#ffffff";
        ctx.font = "bold 10px " + (getComputedStyle(document.body).fontFamily || "sans-serif");
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText("วันประเมินผล", statusX, pad.top - 11);
        ctx.restore();
      }

      // 4. Planned S-Curve
      if (state.chartSettings.showPlanned && timeline.plannedSeries.length > 1) {
        ctx.save();
        const grad = ctx.createLinearGradient(0, pad.top, 0, pad.top + plotH);
        grad.addColorStop(0, isDark ? "rgba(59, 130, 246, 0.22)" : "rgba(59, 130, 246, 0.12)");
        grad.addColorStop(1, "rgba(59, 130, 246, 0.0)");

        ctx.beginPath();
        ctx.moveTo(getX(timeline.plannedSeries[0].date), pad.top + plotH);
        timeline.plannedSeries.forEach((pt) => {
          ctx.lineTo(getX(pt.date), getY(pt.plannedPct));
        });
        ctx.lineTo(getX(timeline.plannedSeries[timeline.plannedSeries.length - 1].date), pad.top + plotH);
        ctx.closePath();
        ctx.fillStyle = grad;
        ctx.fill();

        ctx.beginPath();
        timeline.plannedSeries.forEach((pt, idx) => {
          const x = getX(pt.date);
          const y = getY(pt.plannedPct);
          if (idx === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        });
        ctx.strokeStyle = "#2563eb";
        ctx.lineWidth = 3;
        ctx.stroke();
        ctx.restore();
      }

      // 5. Actual S-Curve
      if (state.chartSettings.showActual && timeline.actualSeries.length > 1) {
        ctx.save();
        const gradA = ctx.createLinearGradient(0, pad.top, 0, pad.top + plotH);
        gradA.addColorStop(0, isDark ? "rgba(16, 185, 129, 0.3)" : "rgba(16, 185, 129, 0.18)");
        gradA.addColorStop(1, "rgba(16, 185, 129, 0.0)");

        ctx.beginPath();
        ctx.moveTo(getX(timeline.actualSeries[0].date), pad.top + plotH);
        timeline.actualSeries.forEach((pt) => {
          ctx.lineTo(getX(pt.date), getY(pt.actualPct));
        });
        ctx.lineTo(getX(timeline.actualSeries[timeline.actualSeries.length - 1].date), pad.top + plotH);
        ctx.closePath();
        ctx.fillStyle = gradA;
        ctx.fill();

        ctx.beginPath();
        timeline.actualSeries.forEach((pt, idx) => {
          const x = getX(pt.date);
          const y = getY(pt.actualPct);
          if (idx === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        });
        ctx.strokeStyle = "#10b981";
        ctx.lineWidth = 3.5;
        ctx.stroke();

        const lastPt = timeline.actualSeries[timeline.actualSeries.length - 1];
        if (lastPt) {
          const lx = getX(lastPt.date);
          const ly = getY(lastPt.actualPct);
          ctx.fillStyle = "#10b981";
          ctx.beginPath();
          ctx.arc(lx, ly, 5.5, 0, Math.PI * 2);
          ctx.fill();
          ctx.lineWidth = 2;
          ctx.strokeStyle = "#ffffff";
          ctx.stroke();
        }
        ctx.restore();
      }

      // 6. Forecast S-Curve
      if (state.chartSettings.showForecast && timeline.forecastSeries.length > 1) {
        ctx.save();
        ctx.setLineDash([6, 5]);
        ctx.beginPath();
        timeline.forecastSeries.forEach((pt, idx) => {
          const x = getX(pt.date);
          const y = getY(pt.forecastPct);
          if (idx === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        });
        ctx.strokeStyle = "#f59e0b";
        ctx.lineWidth = 2.5;
        ctx.stroke();
        ctx.restore();
      }

      // 7. Interactive Hover Cursor
      if (chartHoverInfo && chartHoverInfo.active) {
        const hoverX = chartHoverInfo.x;
        if (hoverX >= pad.left && hoverX <= pad.left + plotW) {
          ctx.save();
          ctx.strokeStyle = isDark ? "rgba(255,255,255,0.4)" : "rgba(0,0,0,0.3)";
          ctx.lineWidth = 1;
          ctx.setLineDash([3, 3]);
          ctx.beginPath();
          ctx.moveTo(hoverX, pad.top);
          ctx.lineTo(hoverX, pad.top + plotH);
          ctx.stroke();

          if (chartHoverInfo.point) {
            const py = getY(chartHoverInfo.point.plannedPct);
            ctx.fillStyle = "#2563eb";
            ctx.beginPath();
            ctx.arc(hoverX, py, 4, 0, Math.PI * 2);
            ctx.fill();

            if (chartHoverInfo.point.actualPct !== null) {
              const ay = getY(chartHoverInfo.point.actualPct);
              ctx.fillStyle = "#10b981";
              ctx.beginPath();
              ctx.arc(hoverX, ay, 4.5, 0, Math.PI * 2);
              ctx.fill();
            }
          }
          ctx.restore();
        }
      }
    }

    /* Manpower Headcount Bar Chart */
    function drawManpowerCanvas() {
      const canvas = document.getElementById("manpower-canvas");
      if (!canvas) return;

      const rect = canvas.parentElement.getBoundingClientRect();
      if (!rect || rect.width <= 0 || rect.height <= 0) {
        return;
      }

      const ctx = canvas.getContext("2d");
      const dpr = window.devicePixelRatio || 1;
      const width = rect.width;
      const height = rect.height;

      canvas.width = width * dpr;
      canvas.height = height * dpr;
      ctx.scale(dpr, dpr);
      ctx.clearRect(0, 0, width, height);

      const logs = [...state.dailyLogs].sort((a,b) => (a.date > b.date ? 1 : -1));
      if (logs.length === 0) {
        ctx.fillStyle = "#94a3b8";
        ctx.textAlign = "center";
        ctx.fillText("ยังไม่มีข้อมูลกำลังคนหน้างาน (สามารถกด 'บันทึกคนงานประจำวัน' เพื่อเพิ่มข้อมูลได้)", width / 2, height / 2);
        return;
      }

      const pad = { top: 20, right: 30, bottom: 40, left: 45 };
      const plotW = Math.max(10, width - pad.left - pad.right);
      const plotH = Math.max(10, height - pad.top - pad.bottom);

      const maxWorkers = Math.max(10, Math.max(...logs.map(l => parseInt(l.workers) || 0)) + 2);
      const isDark = document.body.getAttribute("data-theme") === "dark";
      const barColor = isDark ? "#818cf8" : "#6366f1";

      ctx.lineWidth = 1;
      ctx.font = "11px " + (getComputedStyle(document.body).fontFamily || "sans-serif");
      ctx.textAlign = "right";
      ctx.textBaseline = "middle";

      for (let w = 0; w <= maxWorkers; w += 4) {
        const y = pad.top + plotH - (w / maxWorkers) * plotH;
        ctx.strokeStyle = isDark ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.06)";
        ctx.beginPath();
        ctx.moveTo(pad.left, y);
        ctx.lineTo(pad.left + plotW, y);
        ctx.stroke();

        ctx.fillStyle = isDark ? "#94a3b8" : "#64748b";
        ctx.fillText(w + " คน", pad.left - 8, y);
      }

      const barW = Math.min(24, Math.max(8, (plotW / logs.length) - 4));
      logs.forEach((item, idx) => {
        const x = pad.left + (idx / (logs.length - 1 || 1)) * (plotW - barW);
        const count = parseInt(item.workers) || 0;
        const barH = (count / maxWorkers) * plotH;
        const y = pad.top + plotH - barH;

        ctx.fillStyle = barColor;
        ctx.beginPath();
        if (typeof ctx.roundRect === "function") {
          ctx.roundRect(x, y, barW, barH, [3, 3, 0, 0]);
        } else {
          ctx.rect(x, y, barW, barH);
        }
        ctx.fill();

        if (idx % Math.ceil(logs.length / 8) === 0 || idx === logs.length - 1) {
          ctx.fillStyle = isDark ? "#94a3b8" : "#64748b";
          ctx.textAlign = "center";
          ctx.textBaseline = "top";
          ctx.fillText(formatThaiDate(item.date, true), x + barW / 2, pad.top + plotH + 8);
        }
      });
    }

    /* Canvas Hover / Tooltip Interaction */
    function setupCanvasHover() {
      const canvas = document.getElementById("scurve-canvas");
      const tooltip = document.getElementById("chart-tooltip");
      if (!canvas || !tooltip) return;

      canvas.addEventListener("mousemove", (e) => {
        if (state.tasks.length === 0) return;
        const rect = canvas.getBoundingClientRect();
        if (!rect || rect.width <= 0) return;

        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        const timeline = calculateProjectTimeline();
        const pad = { top: 25, right: 35, bottom: 45, left: 55 };
        const plotW = Math.max(10, rect.width - pad.left - pad.right);

        if (x < pad.left || x > pad.left + plotW) {
          chartHoverInfo = { active: false };
          tooltip.style.display = "none";
          drawSCurveCanvas(timeline);
          return;
        }

        const ratio = (x - pad.left) / plotW;
        const index = Math.max(0, Math.min(timeline.dates.length - 1, Math.round(ratio * (timeline.dates.length - 1))));
        const date = timeline.dates[index];
        const dateStr = formatDate(date);

        const planItem = timeline.plannedSeries[index];
        const actItem = timeline.actualSeries.find(item => item.dateStr === dateStr);

        const plannedPct = planItem ? planItem.plannedPct : 0;
        const actualPct = actItem ? actItem.actualPct : null;
        const variance = actualPct !== null ? (actualPct - plannedPct).toFixed(1) : null;

        chartHoverInfo = {
          active: true,
          x,
          y,
          point: { date, dateStr, plannedPct, actualPct, variance }
        };

        tooltip.style.display = "block";
        tooltip.style.left = `${e.clientX}px`;
        tooltip.style.top = `${e.clientY - 15}px`;

        let html = `
          <div class="tooltip-date">📅 ${formatThaiDate(date)}</div>
          <div class="tooltip-row">
            <span>แผนงานสะสม:</span>
            <strong style="color:#60a5fa;">${plannedPct.toFixed(1)}%</strong>
          </div>
        `;
        if (actualPct !== null) {
          const varColor = variance >= 0 ? "#34d399" : "#f87171";
          const varText = variance >= 0 ? `+${variance}% (เร็วกว่าแผน)` : `${variance}% (ล่าช้ากว่าแผน)`;
          html += `
            <div class="tooltip-row">
              <span>ทำจริงสะสม:</span>
              <strong style="color:#34d399;">${actualPct.toFixed(1)}%</strong>
            </div>
            <div class="tooltip-row variance">
              <span>ผลต่าง (SV):</span>
              <span style="color:${varColor};">${varText}</span>
            </div>
          `;
        } else {
          html += `<div style="font-size:0.75rem; color:#94a3b8; margin-top:4px;">* วันที่อยู่หลังวันประเมินผล</div>`;
        }
        tooltip.innerHTML = html;

        drawSCurveCanvas(timeline);
      });

      canvas.addEventListener("mouseleave", () => {
        chartHoverInfo = { active: false };
        tooltip.style.display = "none";
        drawSCurveCanvas(calculateProjectTimeline());
      });
    }

    function toggleCurve(curve) {
      if (curve === "planned") state.chartSettings.showPlanned = !state.chartSettings.showPlanned;
      if (curve === "actual") state.chartSettings.showActual = !state.chartSettings.showActual;
      if (curve === "forecast") state.chartSettings.showForecast = !state.chartSettings.showForecast;
      drawSCurveCanvas(calculateProjectTimeline());
    }

    function downloadChartImage() {
      const canvas = document.getElementById("scurve-canvas");
      if (!canvas) return;
      const link = document.createElement("a");
      link.download = `S-Curve_${state.project.name}_${state.project.statusDate}.png`;
      link.href = canvas.toDataURL("image/png");
      link.click();
      showToast("บันทึกรูปกราฟ S-Curve เรียบร้อยแล้ว");
    }

    /* =========================================================
       UPDATE KPI CARDS & STATUS
       ========================================================= */
    function updateKPICards(timeline) {
      if (!timeline) timeline = calculateProjectTimeline();

      document.getElementById("lbl-project-name").childNodes[0].nodeValue = state.project.name + " ";
      document.getElementById("lbl-project-lead").innerText = state.project.lead;
      document.getElementById("lbl-project-date-range").innerText = `${formatThaiDate(timeline.pStart)} ถึง ${formatThaiDate(timeline.pEnd)}`;
      document.getElementById("status-date-input").value = state.project.statusDate;

      document.getElementById("kpi-days-elapsed").innerHTML = `${timeline.elapsedDays} <span class="unit">/ ${timeline.totalDays} วัน</span>`;
      const timePct = Math.min(100, (timeline.elapsedDays / timeline.totalDays) * 100).toFixed(1);
      document.getElementById("kpi-time-pct").innerText = `${timePct}%`;

      document.getElementById("kpi-planned-pct").innerHTML = `${timeline.plannedAtStatus.toFixed(1)} <span class="unit">%</span>`;
      document.getElementById("kpi-actual-pct").innerHTML = `${timeline.actualAtStatus.toFixed(1)} <span class="unit">%</span>`;

      const vVal = timeline.variancePct;
      const vSign = vVal > 0 ? "+" : "";
      document.getElementById("kpi-variance-val").innerHTML = `${vSign}${vVal.toFixed(1)} <span class="unit">%</span>`;

      const vBadge = document.getElementById("kpi-variance-badge");
      const vDays = document.getElementById("kpi-days-variance");

      if (vVal > 0.5) {
        vBadge.className = "badge badge-success";
        vBadge.innerText = "เร็วกว่าแผนงาน";
        vDays.innerText = `เร็วกว่า +${timeline.daysVariance} วัน`;
        vDays.style.color = "var(--success)";
      } else if (vVal < -0.5) {
        vBadge.className = "badge badge-danger";
        vBadge.innerText = "ล่าช้ากว่าแผน";
        vDays.innerText = `ล่าช้า ${timeline.daysVariance} วัน`;
        vDays.style.color = "var(--danger)";
      } else {
        vBadge.className = "badge badge-warning";
        vBadge.innerText = "ตรงตามแผนงาน";
        vDays.innerText = "ตามแผน (0 วัน)";
        vDays.style.color = "var(--text-muted)";
      }

      const totalWorkers = state.dailyLogs.reduce((acc, l) => acc + (parseInt(l.workers) || 0), 0);
      const avgWorkers = state.dailyLogs.length ? (totalWorkers / state.dailyLogs.length).toFixed(1) : 0;
      const maxWorkers = state.dailyLogs.length ? Math.max(...state.dailyLogs.map(l => parseInt(l.workers) || 0)) : 0;

      document.getElementById("kpi-manpower-total").innerHTML = `${totalWorkers} <span class="unit">Man-days</span>`;
      document.getElementById("kpi-manpower-avg").innerText = avgWorkers;
      document.getElementById("kpi-manpower-max").innerText = maxWorkers;
      document.getElementById("tab-task-count").innerText = state.tasks.length;
      document.getElementById("gantt-item-count").innerText = `${state.tasks.length} รายการ`;
      document.getElementById("manpower-log-count").innerText = `${state.dailyLogs.length} รายการ`;
    }

    function renderVarianceAnalysis(timeline) {
      const svDesc = document.getElementById("perf-sv-desc");
      const spiDesc = document.getElementById("perf-spi-desc");
      const esDesc = document.getElementById("perf-es-desc");

      const v = timeline.variancePct;
      const spi = timeline.plannedAtStatus > 0 ? (timeline.actualAtStatus / timeline.plannedAtStatus).toFixed(2) : "1.00";

      if (v >= 0) {
        svDesc.innerHTML = `<strong style="color:var(--success);">+${v.toFixed(1)}% (เป็นบวก)</strong> โครงการส่งมอบงานได้เร็วกว่าเป้าหมายที่กำหนดไว้`;
      } else {
        svDesc.innerHTML = `<strong style="color:var(--danger);">${v.toFixed(1)}% (ติดลบ)</strong> โครงการมีความล่าช้ากว่าแผนสะสม จำเป็นต้องเร่งรัดงาน`;
      }

      if (parseFloat(spi) >= 1.0) {
        spiDesc.innerHTML = `<strong style="color:var(--success);">SPI = ${spi}</strong> ประสิทธิภาพตารางการดำเนินงานอยู่ในเกณฑ์ดีเยี่ยม (SPI ≥ 1.0)`;
      } else {
        spiDesc.innerHTML = `<strong style="color:var(--danger);">SPI = ${spi}</strong> ประสิทธิภาพต่ำกว่าแผนงาน (SPI &lt; 1.0) ควรพิจารณาเพิ่มทรัพยากร`;
      }

      const diff = timeline.daysVariance;
      if (diff > 0) {
        esDesc.innerHTML = `ผลงานปัจจุบันเทียบเท่ากับแผนล่วงหน้าไปแล้ว <strong style="color:var(--success);">+${diff} วัน</strong> (Earned Date: ${formatThaiDate(timeline.earnedDate)})`;
      } else if (diff < 0) {
        esDesc.innerHTML = `ผลงานปัจจุบันล่าช้ากว่าตารางเวลาเทียบเท่า <strong style="color:var(--danger);">${diff} วัน</strong> (Earned Date: ${formatThaiDate(timeline.earnedDate)})`;
      } else {
        esDesc.innerHTML = `ผลงานดำเนินไปสอดคล้องกับกำหนดการของแผนงานอย่างสมดุล (On Track)`;
      }
    }

    /* =========================================================
       GANTT CHART RENDERING
       ========================================================= */
    function renderGantt() {
      const thead = document.getElementById("gantt-thead");
      const tbody = document.getElementById("gantt-tbody");
      if (!thead || !tbody) return;

      const timeline = calculateProjectTimeline();
      const catFilter = document.getElementById("gantt-category-filter").value;

      let filteredTasks = state.tasks;
      if (catFilter !== "ALL") {
        filteredTasks = filteredTasks.filter(t => t.category === catFilter);
      }

      const catSelect = document.getElementById("gantt-category-filter");
      const currentCat = catSelect.value;
      const categories = [...new Set(state.tasks.map(t => t.category))];
      catSelect.innerHTML = `<option value="ALL">ทุกหมวดหมู่งาน (All Categories)</option>` +
        categories.map(c => `<option value="${c}" ${c === currentCat ? 'selected' : ''}>${c}</option>`).join("");

      const totalDays = timeline.dates.length;
      let headerMonthsHtml = `<th class="gantt-task-col" rowspan="2">รายการงาน (Task Name)</th>`;
      let headerDaysHtml = "";

      timeline.dates.forEach((d) => {
        const dayOfWeek = ["อา", "จ", "อ", "พ", "พฤ", "ศ", "ส"][d.getDay()];
        const isStatusDate = formatDate(d) === state.project.statusDate;
        const cellStyle = isStatusDate ? "background:#fee2e2; color:#ef4444; font-weight:700;" : "";

        headerDaysHtml += `<th style="width:28px; min-width:28px; text-align:center; padding:3px 0; font-size:0.72rem; ${cellStyle}">
          <div>${d.getDate()}</div>
          <div style="font-size:0.65rem; color:var(--text-muted);">${dayOfWeek}</div>
        </th>`;
      });

      headerMonthsHtml += `<th colspan="${totalDays}" style="text-align:center; background:var(--bg-subtle);">ไทม์ไลน์รายวัน (${formatThaiDate(timeline.pStart)} - ${formatThaiDate(timeline.pEnd)})</th>`;

      thead.innerHTML = `
        <tr class="gantt-header-row">${headerMonthsHtml}</tr>
        <tr class="gantt-header-row">${headerDaysHtml}</tr>
      `;

      if (filteredTasks.length === 0) {
        tbody.innerHTML = `
          <tr>
            <td colspan="${totalDays + 1}" style="text-align:center; padding:40px; color:var(--text-muted);">
              ยังไม่มีรายการงานในแผนภูมิแกนต์ <button class="btn btn-primary btn-sm" onclick="openTaskModal(null)" style="margin-left:8px;">เพิ่มงานใหม่</button>
            </td>
          </tr>
        `;
        return;
      }

      let rowsHtml = "";
      let currentCategory = "";

      filteredTasks.forEach(task => {
        if (task.category !== currentCategory) {
          currentCategory = task.category;
          rowsHtml += `
            <tr class="category-row">
              <td class="gantt-task-col" style="font-weight:700; background:var(--bg-subtle); color:var(--primary);">
                📁 ${currentCategory}
              </td>
              <td colspan="${totalDays}" style="background:var(--bg-subtle);"></td>
            </tr>
          `;
        }

        const pStart = parseDate(task.plannedStart) || timeline.pStart;
        const pEnd = parseDate(task.plannedEnd) || timeline.pEnd;
        const pOffset = Math.max(0, diffDays(timeline.pStart, pStart));
        const pDuration = Math.max(1, diffDays(pStart, pEnd) + 1);

        const dayColWidth = 28;
        const barLeft = pOffset * dayColWidth;
        const barWidth = pDuration * dayColWidth;

        const prog = parseFloat(task.progress) || 0;
        const actWidth = (prog / 100) * barWidth;

        rowsHtml += `
          <tr>
            <td class="gantt-task-col" title="${task.name}" onclick="openTaskModal('${task.id}')" style="cursor:pointer;">
              <div style="font-weight:500; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:280px;">
                ${task.name}
              </div>
              <div style="font-size:0.75rem; color:var(--text-muted); display:flex; justify-content:space-between; margin-top:2px;">
                <span>${task.assignedTo || '-'}</span>
                <span>${task.duration} วัน • <strong style="color:${prog === 100 ? 'var(--success)' : 'var(--primary)'};">${prog}%</strong></span>
              </div>
            </td>
            <td colspan="${totalDays}" class="gantt-timeline-cell">
              <div class="gantt-bar-container">
                <div class="gantt-planned-bar" style="left:${barLeft}px; width:${barWidth}px;" title="แผนงาน: ${task.plannedStart} ถึง ${task.plannedEnd} (${task.duration} วัน)"></div>
                ${prog > 0 ? `<div class="gantt-actual-bar" style="left:${barLeft}px; width:${actWidth}px;" title="ผลงานจริง: ${prog}%"></div>` : ''}
              </div>
            </td>
          </tr>
        `;
      });

      tbody.innerHTML = rowsHtml;
    }

    function scrollGanttToToday() {
      const container = document.getElementById("gantt-scroll-container");
      const timeline = calculateProjectTimeline();
      const offset = diffDays(timeline.pStart, timeline.statusDate);
      if (container && offset > 0) {
        container.scrollTo({ left: offset * 28 - 150, behavior: "smooth" });
      }
    }

    /* =========================================================
       TASK STATUS HELPER
       ========================================================= */
    function getTaskStatusBadgeHtml(prog, plannedEndStr) {
      const pend = parseDate(plannedEndStr);
      const statusD = parseDate(state.project.statusDate);

      if (prog >= 100) {
        return `<span class="badge badge-success">เสร็จสมบูรณ์</span>`;
      } else if (pend && statusD && pend < statusD) {
        return `<span class="badge badge-danger">ล่าช้ากว่าแผน</span>`;
      } else if (prog > 0) {
        return `<span class="badge badge-info">กำลังดำเนินงาน</span>`;
      } else {
        return `<span class="badge badge-neutral">ยังไม่เริ่ม</span>`;
      }
    }

    /* =========================================================
       TASK MANAGEMENT TABLE RENDERING & DELETION
       ========================================================= */
    function renderTasks() {
      const tbody = document.getElementById("task-tbody");
      if (!tbody) return;

      const search = state.taskFilters.search.toLowerCase();
      const cat = state.taskFilters.category;
      const stat = state.taskFilters.status;

      let list = state.tasks.filter(t => {
        if (search && !t.name.toLowerCase().includes(search) && !(t.assignedTo || '').toLowerCase().includes(search)) return false;
        if (cat !== "ALL" && t.category !== cat) return false;
        if (stat === "completed" && t.progress < 100) return false;
        if (stat === "in_progress" && (t.progress <= 0 || t.progress >= 100)) return false;
        if (stat === "not_started" && t.progress > 0) return false;
        if (stat === "delayed") {
          const pend = parseDate(t.plannedEnd);
          const statusD = parseDate(state.project.statusDate);
          if (!(pend && statusD && pend < statusD && t.progress < 100)) return false;
        }
        return true;
      });

      // Update Category Dropdown
      const catSelect = document.getElementById("task-category-filter");
      const currentCat = catSelect.value;
      const categories = [...new Set(state.tasks.map(t => t.category))];
      catSelect.innerHTML = `<option value="ALL">ทุกหมวดหมู่งาน (All Categories)</option>` +
        categories.map(c => `<option value="${c}" ${c === currentCat ? 'selected' : ''}>${c}</option>`).join("");

      // Update Datalist in modal
      const datalist = document.getElementById("category-datalist");
      if (datalist) {
        datalist.innerHTML = categories.map(c => `<option value="${c}">`).join("");
      }

      // If no tasks at all
      if (state.tasks.length === 0) {
        tbody.innerHTML = `
          <tr>
            <td colspan="12" style="text-align:center; padding:45px 20px;">
              <div style="font-size:2.2rem; margin-bottom:10px;">📋</div>
              <div style="font-weight:600; font-size:1.1rem; color:var(--text-main); margin-bottom:6px;">ยังไม่มีรายการงานในโครงการ</div>
              <div style="color:var(--text-muted); font-size:0.85rem; margin-bottom:16px;">
                ตารางงานว่างแล้ว พร้อมสำหรับใส่รายการงานใหม่ของคุณ หรือคุณสามารถโหลดตัวอย่างเพื่อศึกษาได้
              </div>
              <div style="display:flex; justify-content:center; gap:10px;">
                <button class="btn btn-primary" onclick="openTaskModal(null)">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                  เพิ่มงานแรกของคุณ
                </button>
                <button class="btn btn-secondary" onclick="resetToSampleData()">
                  🔄 โหลดตัวอย่าง PVCell Project
                </button>
              </div>
            </td>
          </tr>
        `;
        updateBatchDeleteButton();
        return;
      }

      // If filtered out
      if (list.length === 0) {
        tbody.innerHTML = `<tr><td colspan="12" style="text-align:center; padding:30px; color:var(--text-muted);">ไม่พบรายการงานที่ตรงกับเงื่อนไขการค้นหา</td></tr>`;
        updateBatchDeleteButton();
        return;
      }

      let html = "";
      list.forEach((t, index) => {
        const prog = parseFloat(t.progress) || 0;
        const badgeHtml = getTaskStatusBadgeHtml(prog, t.plannedEnd);

        html += `
          <tr id="task-row-${t.id}">
            <td style="text-align:center;">
              <input type="checkbox" class="task-checkbox" value="${t.id}" onchange="onTaskCheckboxChange()" style="cursor:pointer;">
            </td>
            <td style="color:var(--text-muted); font-size:0.75rem;">${index + 1}</td>
            <td style="white-space:nowrap;"><span class="badge badge-neutral" style="font-size:0.75rem;">${t.category}</span></td>
            <td>
              <strong style="color:var(--text-main); font-weight:600; cursor:pointer;" onclick="openTaskModal('${t.id}')">${t.name}</strong>
              ${t.notes ? `<div style="font-size:0.75rem; color:var(--text-muted);">📝 ${t.notes}</div>` : ''}
            </td>
            <td style="white-space:nowrap; color:var(--text-muted);">${t.assignedTo || '-'}</td>
            <td style="white-space:nowrap; font-size:0.8rem;">
              ${formatThaiDate(t.plannedStart, true)} - ${formatThaiDate(t.plannedEnd, true)}
            </td>
            <td style="text-align:center; font-weight:600;">${t.duration} วัน</td>
            <td id="actual-date-cell-${t.id}" style="white-space:nowrap; font-size:0.8rem; color:var(--text-muted);">
              ${t.actualStart ? formatThaiDate(t.actualStart, true) : '-'} ${t.actualEnd ? 'ถึง ' + formatThaiDate(t.actualEnd, true) : ''}
            </td>
            <td>
              <div class="progress-slider-cell">
                <input type="range" class="progress-slider" min="0" max="100" value="${prog}" 
                  oninput="handleTaskProgressInput('${t.id}', this.value)" 
                  onchange="handleTaskProgressChange('${t.id}', this.value)">
                <span class="progress-pct-badge" id="prog-badge-${t.id}" style="color:${prog === 100 ? 'var(--success)' : 'var(--primary)'};">${prog}%</span>
              </div>
            </td>
            <td style="text-align:right; font-weight:600;">${t.weight}%</td>
            <td id="status-cell-${t.id}" style="text-align:center;">${badgeHtml}</td>
            <td style="text-align:center;">
              <div style="display:flex; justify-content:center; gap:4px;">
                <button class="btn-icon btn-sm" onclick="openTaskModal('${t.id}')" title="แก้ไขงาน">✏️</button>
                <button class="btn-icon btn-sm" onclick="deleteTask('${t.id}')" title="ลบงานนี้" style="color:var(--danger);">🗑️</button>
              </div>
            </td>
          </tr>
        `;
      });

      tbody.innerHTML = html;
      updateBatchDeleteButton();
    }

    function filterTasks() {
      state.taskFilters.search = document.getElementById("task-search-input").value;
      state.taskFilters.category = document.getElementById("task-category-filter").value;
      state.taskFilters.status = document.getElementById("task-status-filter").value;
      renderTasks();
    }

    /* INSTANT SLIDER UPDATE: Changes Status badge and % immediately on drag without any lag */
    function handleTaskProgressInput(taskId, newProg) {
      const prog = parseFloat(newProg);
      const badgeEl = document.getElementById(`prog-badge-${taskId}`);
      if (badgeEl) {
        badgeEl.innerText = `${prog}%`;
        badgeEl.style.color = prog === 100 ? "var(--success)" : "var(--primary)";
      }

      const statusCell = document.getElementById(`status-cell-${taskId}`);
      const task = state.tasks.find(t => t.id === taskId);
      if (statusCell && task) {
        statusCell.innerHTML = getTaskStatusBadgeHtml(prog, task.plannedEnd);
      }
    }

    /* SAVE ON RELEASE: Updates dates, saves state, and updates KPIs without infinite loop */
    function handleTaskProgressChange(taskId, newProg) {
      const task = state.tasks.find(t => t.id === taskId);
      if (!task) return;

      task.progress = parseFloat(newProg);
      if (task.progress >= 100 && !task.actualEnd) {
        task.actualEnd = state.project.statusDate || formatDate(new Date());
      }
      if (task.progress > 0 && !task.actualStart) {
        task.actualStart = task.plannedStart;
      }

      saveState();

      // Update actual dates cell in the row
      const actualDateCell = document.getElementById(`actual-date-cell-${taskId}`);
      if (actualDateCell) {
        actualDateCell.innerText = `${task.actualStart ? formatThaiDate(task.actualStart, true) : '-'} ${task.actualEnd ? 'ถึง ' + formatThaiDate(task.actualEnd, true) : ''}`;
      }

      // Update KPI cards immediately
      const timeline = calculateProjectTimeline();
      updateKPICards(timeline);

      // Only draw charts if the corresponding tab is visible
      if (state.activeTab === "tab-scurve") {
        drawSCurveCanvas(timeline);
      } else if (state.activeTab === "tab-gantt") {
        renderGantt();
      }

      showToast(`อัปเดตความคืบหน้า "${task.name}" เป็น ${task.progress}% เรียบร้อย`);
    }

    function autoCalculateWeights() {
      state.project.weightMode = "duration";
      normalizeWeights();
      saveState();
      renderTasks();
      const timeline = calculateProjectTimeline();
      updateKPICards(timeline);
      if (state.activeTab === "tab-scurve") drawSCurveCanvas(timeline);
      else if (state.activeTab === "tab-gantt") renderGantt();
      showToast("คำนวณค่าน้ำหนักงานตามสัดส่วนระยะเวลาสำเร็จ");
    }

    /* =========================================================
       TASK DELETION METHODS (Single, Batch, Clear All)
       ========================================================= */

    // 1. Delete Single Task
    function deleteTask(taskId) {
      const task = state.tasks.find(t => t.id === taskId);
      if (!task) return;
      if (confirm(`คุณต้องการลบรายการงาน "${task.name}" ใช่หรือไม่?`)) {
        state.tasks = state.tasks.filter(t => t.id !== taskId);
        normalizeWeights();
        saveState();
        renderTasks();
        const timeline = calculateProjectTimeline();
        updateKPICards(timeline);
        if (state.activeTab === "tab-scurve") drawSCurveCanvas(timeline);
        else if (state.activeTab === "tab-gantt") renderGantt();
        showToast(`ลบรายการ "${task.name}" เรียบร้อยแล้ว`);
      }
    }

    // 2. Delete Task from Inside the Modal
    function deleteTaskFromModal() {
      const id = document.getElementById("modal-task-id").value;
      if (!id) return;
      const task = state.tasks.find(t => t.id === id);
      if (!task) return;

      if (confirm(`คุณต้องการลบรายการงาน "${task.name}" ใช่หรือไม่?`)) {
        state.tasks = state.tasks.filter(t => t.id !== id);
        normalizeWeights();
        saveState();
        closeTaskModal();
        renderTasks();
        const timeline = calculateProjectTimeline();
        updateKPICards(timeline);
        if (state.activeTab === "tab-scurve") drawSCurveCanvas(timeline);
        else if (state.activeTab === "tab-gantt") renderGantt();
        showToast(`ลบรายการ "${task.name}" เรียบร้อยแล้ว`);
      }
    }

    // 3. Clear ALL Tasks (To start fresh for a new project)
    function clearAllTasks() {
      if (state.tasks.length === 0) {
        showToast("ไม่มีรายการงานในระบบ");
        return;
      }
      if (confirm(`⚠️ ยืนยันการลบรายการงานทั้งหมด (${state.tasks.length} รายการ)?\n\nการดำเนินการนี้จะลบรายการงานเดิมออกทั้งหมดเพื่อให้คุณเริ่มต้นใส่แผนงานใหม่\n(คุณสามารถกู้คืนตัวอย่าง PVCell Project ได้ตลอดเวลา)`)) {
        state.tasks = [];
        saveState();
        renderTasks();
        const timeline = calculateProjectTimeline();
        updateKPICards(timeline);
        if (state.activeTab === "tab-scurve") drawSCurveCanvas(timeline);
        else if (state.activeTab === "tab-gantt") renderGantt();
        showToast("ล้างรายการงานทั้งหมดเรียบร้อยแล้ว พร้อมสำหรับงานใหม่");
      }
    }

    // 4. Batch Delete Selected Tasks
    function deleteSelectedTasks() {
      const checkedBoxes = Array.from(document.querySelectorAll(".task-checkbox:checked"));
      const idsToDelete = checkedBoxes.map(cb => cb.value);
      if (idsToDelete.length === 0) return;

      if (confirm(`คุณต้องการลบรายการงานที่เลือกจำนวน ${idsToDelete.length} รายการ ใช่หรือไม่?`)) {
        state.tasks = state.tasks.filter(t => !idsToDelete.includes(t.id));
        normalizeWeights();
        saveState();
        renderTasks();
        const timeline = calculateProjectTimeline();
        updateKPICards(timeline);
        if (state.activeTab === "tab-scurve") drawSCurveCanvas(timeline);
        else if (state.activeTab === "tab-gantt") renderGantt();
        showToast(`ลบรายการงานที่เลือก ${idsToDelete.length} รายการ เรียบร้อยแล้ว`);
      }
    }

    function toggleSelectAllTasks(checked) {
      const checkboxes = document.querySelectorAll(".task-checkbox");
      checkboxes.forEach(cb => cb.checked = checked);
      updateBatchDeleteButton();
    }

    function onTaskCheckboxChange() {
      updateBatchDeleteButton();
    }

    function updateBatchDeleteButton() {
      const checked = document.querySelectorAll(".task-checkbox:checked");
      const btn = document.getElementById("btn-batch-delete");
      const countSpan = document.getElementById("batch-delete-count");
      const thSelectAll = document.getElementById("th-select-all");

      if (countSpan) countSpan.innerText = checked.length;
      if (btn) {
        btn.style.display = checked.length > 0 ? "inline-flex" : "none";
      }
      if (thSelectAll) {
        const all = document.querySelectorAll(".task-checkbox");
        thSelectAll.checked = all.length > 0 && checked.length === all.length;
      }
    }

    /* =========================================================
       NEW PROJECT MODAL
       ========================================================= */
    function openNewProjectModal() {
      document.getElementById("new-project-name").value = "";
      document.getElementById("new-project-lead").value = "";
      const today = formatDate(new Date());
      document.getElementById("new-project-start").value = today;
      document.getElementById("new-project-end").value = formatDate(addDays(new Date(), 90));
      document.getElementById("new-project-clear-tasks").checked = true;
      document.getElementById("new-project-modal").classList.add("open");
    }

    function closeNewProjectModal() {
      document.getElementById("new-project-modal").classList.remove("open");
    }

    function submitNewProjectModal() {
      const name = document.getElementById("new-project-name").value.trim() || "โครงการใหม่";
      const lead = document.getElementById("new-project-lead").value.trim() || "-";
      const startDate = document.getElementById("new-project-start").value;
      const endDate = document.getElementById("new-project-end").value;
      const clearTasks = document.getElementById("new-project-clear-tasks").checked;

      state.project.name = name;
      state.project.lead = lead;
      state.project.startDate = startDate || formatDate(new Date());
      state.project.endDate = endDate || formatDate(addDays(new Date(), 90));
      state.project.statusDate = state.project.startDate;

      if (clearTasks) {
        state.tasks = [];
        state.dailyLogs = [];
      }

      saveState();
      closeNewProjectModal();
      renderTasks();
      renderDailyLogs();
      const timeline = calculateProjectTimeline();
      updateKPICards(timeline);
      if (state.activeTab === "tab-scurve") drawSCurveCanvas(timeline);
      else if (state.activeTab === "tab-gantt") renderGantt();
      showToast(`สร้างโครงการ "${name}" สำเร็จเรียบร้อย`);
    }

    /* =========================================================
       MANPOWER & DAILY LOGS TABLE RENDERING
       ========================================================= */
    function renderDailyLogs() {
      const tbody = document.getElementById("manpower-tbody");
      if (!tbody) return;

      const logs = [...state.dailyLogs].sort((a,b) => (a.date < b.date ? 1 : -1));
      if (logs.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:30px; color:var(--text-muted);">ยังไม่มีรายการบันทึกประจำวัน</td></tr>`;
        return;
      }

      let html = "";
      logs.forEach(l => {
        html += `
          <tr>
            <td><strong>${formatThaiDate(l.date)}</strong></td>
            <td style="text-align:center;"><span class="badge badge-info" style="font-size:0.85rem;">${l.workers} คน</span></td>
            <td>${l.activity || '-'}</td>
            <td style="color:var(--text-muted);">${l.notes || '-'}</td>
            <td style="text-align:center;">
              <button class="btn-icon btn-sm" onclick="deleteDailyLog('${l.id}')" title="ลบรายการ" style="color:var(--danger);">🗑️</button>
            </td>
          </tr>
        `;
      });
      tbody.innerHTML = html;
    }

    /* =========================================================
       MODALS LOGIC
       ========================================================= */
    function openTaskModal(taskId) {
      const modal = document.getElementById("task-modal");
      const title = document.getElementById("task-modal-title");
      const btnDelete = document.getElementById("btn-modal-delete-task");

      if (taskId) {
        const task = state.tasks.find(t => t.id === taskId);
        if (!task) return;
        title.innerHTML = `✏️ แก้ไขรายการงาน: ${task.name}`;
        document.getElementById("modal-task-id").value = task.id;
        document.getElementById("modal-task-name").value = task.name;
        document.getElementById("modal-task-category").value = task.category;
        document.getElementById("modal-task-assigned").value = task.assignedTo || "";
        document.getElementById("modal-task-pstart").value = task.plannedStart;
        document.getElementById("modal-task-pend").value = task.plannedEnd;
        document.getElementById("modal-task-duration").value = task.duration;
        document.getElementById("modal-task-weight").value = task.weight || "";
        document.getElementById("modal-task-astart").value = task.actualStart || "";
        document.getElementById("modal-task-aend").value = task.actualEnd || "";
        document.getElementById("modal-task-progress").value = task.progress;
        document.getElementById("modal-task-progress-val").innerText = task.progress;
        document.getElementById("modal-task-notes").value = task.notes || "";
        if (btnDelete) btnDelete.style.display = "inline-flex";
      } else {
        title.innerHTML = `➕ เพิ่มรายการงานใหม่`;
        document.getElementById("modal-task-id").value = "";
        document.getElementById("modal-task-name").value = "";
        document.getElementById("modal-task-category").value = "General";
        document.getElementById("modal-task-assigned").value = "";
        document.getElementById("modal-task-pstart").value = state.project.statusDate || formatDate(new Date());
        document.getElementById("modal-task-pend").value = formatDate(addDays(parseDate(state.project.statusDate) || new Date(), 7));
        document.getElementById("modal-task-duration").value = "8";
        document.getElementById("modal-task-weight").value = "";
        document.getElementById("modal-task-astart").value = "";
        document.getElementById("modal-task-aend").value = "";
        document.getElementById("modal-task-progress").value = 0;
        document.getElementById("modal-task-progress-val").innerText = "0";
        document.getElementById("modal-task-notes").value = "";
        if (btnDelete) btnDelete.style.display = "none";
      }
      modal.classList.add("open");
    }

    function calculateModalDuration() {
      const s = parseDate(document.getElementById("modal-task-pstart").value);
      const e = parseDate(document.getElementById("modal-task-pend").value);
      if (s && e) {
        document.getElementById("modal-task-duration").value = Math.max(1, diffDays(s, e) + 1);
      }
    }

    function closeTaskModal() {
      document.getElementById("task-modal").classList.remove("open");
    }

    function saveTaskModal() {
      const id = document.getElementById("modal-task-id").value;
      const name = document.getElementById("modal-task-name").value.trim();
      const category = document.getElementById("modal-task-category").value.trim() || "General";
      const assignedTo = document.getElementById("modal-task-assigned").value.trim();
      const plannedStart = document.getElementById("modal-task-pstart").value;
      const plannedEnd = document.getElementById("modal-task-pend").value;
      const duration = parseInt(document.getElementById("modal-task-duration").value) || 1;
      const weight = parseFloat(document.getElementById("modal-task-weight").value) || 0;
      const actualStart = document.getElementById("modal-task-astart").value;
      const actualEnd = document.getElementById("modal-task-aend").value;
      const progress = parseFloat(document.getElementById("modal-task-progress").value) || 0;
      const notes = document.getElementById("modal-task-notes").value.trim();

      if (!name) {
        alert("กรุณาระบุชื่องาน");
        return;
      }
      if (!plannedStart || !plannedEnd) {
        alert("กรุณาระบุวันที่เริ่มและสิ้นสุดตามแผน");
        return;
      }

      if (id) {
        const task = state.tasks.find(t => t.id === id);
        if (task) {
          Object.assign(task, {
            name, category, assignedTo, plannedStart, plannedEnd, duration, weight, actualStart, actualEnd, progress, notes
          });
        }
      } else {
        const newId = "T" + String(Date.now()).slice(-4);
        state.tasks.push({
          id: newId,
          name, category, assignedTo, plannedStart, plannedEnd, duration, weight, actualStart, actualEnd, progress, notes
        });
      }

      normalizeWeights();
      saveState();
      closeTaskModal();
      renderTasks();
      const timeline = calculateProjectTimeline();
      updateKPICards(timeline);
      if (state.activeTab === "tab-scurve") drawSCurveCanvas(timeline);
      else if (state.activeTab === "tab-gantt") renderGantt();
      showToast("บันทึกรายการงานเรียบร้อยแล้ว");
    }

    /* Project Settings Modal */
    function openProjectSettingsModal() {
      document.getElementById("cfg-project-name").value = state.project.name;
      document.getElementById("cfg-project-lead").value = state.project.lead;
      document.getElementById("cfg-project-start").value = state.project.startDate;
      document.getElementById("cfg-project-end").value = state.project.endDate;
      document.getElementById("cfg-weight-mode").value = state.project.weightMode;
      document.getElementById("project-modal").classList.add("open");
    }
    function closeProjectSettingsModal() {
      document.getElementById("project-modal").classList.remove("open");
    }
    function saveProjectSettingsModal() {
      state.project.name = document.getElementById("cfg-project-name").value.trim() || "My Project";
      state.project.lead = document.getElementById("cfg-project-lead").value.trim() || "-";
      state.project.startDate = document.getElementById("cfg-project-start").value;
      state.project.endDate = document.getElementById("cfg-project-end").value;
      state.project.weightMode = document.getElementById("cfg-weight-mode").value;

      saveState();
      closeProjectSettingsModal();
      renderTasks();
      const timeline = calculateProjectTimeline();
      updateKPICards(timeline);
      if (state.activeTab === "tab-scurve") drawSCurveCanvas(timeline);
      else if (state.activeTab === "tab-gantt") renderGantt();
      showToast("บันทึกการตั้งค่าโครงการเรียบร้อยแล้ว");
    }

    /* Daily Log Modal */
    function openAddDailyLogModal() {
      document.getElementById("modal-log-id").value = "";
      document.getElementById("modal-log-date").value = state.project.statusDate;
      document.getElementById("modal-log-workers").value = "4";
      document.getElementById("modal-log-activity").value = "";
      document.getElementById("modal-log-notes").value = "";
      document.getElementById("daily-log-modal").classList.add("open");
    }
    function closeDailyLogModal() {
      document.getElementById("daily-log-modal").classList.remove("open");
    }
    function saveDailyLogModal() {
      const date = document.getElementById("modal-log-date").value;
      const workers = parseInt(document.getElementById("modal-log-workers").value) || 0;
      const activity = document.getElementById("modal-log-activity").value.trim();
      const notes = document.getElementById("modal-log-notes").value.trim();

      if (!date) {
        alert("กรุณาระบุวันที่");
        return;
      }

      const id = "L" + String(Date.now());
      state.dailyLogs.push({ id, date, workers, activity, notes });
      saveState();
      closeDailyLogModal();
      renderDailyLogs();
      drawManpowerCanvas();
      updateKPICards();
      showToast("บันทึกคนงานประจำวันเรียบร้อยแล้ว");
    }
    function deleteDailyLog(logId) {
      if (confirm("คุณต้องการลบบันทึกประจำวันนี้ใช่หรือไม่?")) {
        state.dailyLogs = state.dailyLogs.filter(l => l.id !== logId);
        saveState();
        renderDailyLogs();
        drawManpowerCanvas();
        updateKPICards();
        showToast("ลบบันทึกเรียบร้อย");
      }
    }

    /* =========================================================
       IMPORT / EXPORT / THEME / TABS
       ========================================================= */
    function onStatusDateChange(newDate) {
      if (!newDate) return;
      state.project.statusDate = newDate;
      saveState();
      const timeline = calculateProjectTimeline();
      updateKPICards(timeline);
      renderTasks();
      if (state.activeTab === "tab-scurve") drawSCurveCanvas(timeline);
      else if (state.activeTab === "tab-gantt") renderGantt();
      showToast(`เปลี่ยนวันประเมินผลเป็น: ${formatThaiDate(newDate)}`);
    }

    function switchTab(tabId) {
      document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));

      const activeBtn = Array.from(document.querySelectorAll(".tab-btn")).find(b => b.getAttribute("onclick").includes(tabId));
      if (activeBtn) activeBtn.classList.add("active");

      const target = document.getElementById(tabId);
      if (target) target.classList.add("active");

      state.activeTab = tabId;

      // Small delay allows browser to apply display: block so getBoundingClientRect has real dimensions
      requestAnimationFrame(() => {
        if (tabId === "tab-scurve") {
          renderCharts();
        } else if (tabId === "tab-gantt") {
          renderGantt();
        } else if (tabId === "tab-tasks") {
          renderTasks();
        } else if (tabId === "tab-manpower") {
          drawManpowerCanvas();
          renderDailyLogs();
        }
      });
    }

    function toggleTheme() {
      const current = document.body.getAttribute("data-theme");
      const next = current === "dark" ? "light" : "dark";
      document.body.setAttribute("data-theme", next);
      if (state.activeTab === "tab-scurve") drawSCurveCanvas(calculateProjectTimeline());
      else if (state.activeTab === "tab-gantt") renderGantt();
      else if (state.activeTab === "tab-manpower") drawManpowerCanvas();
    }

    function exportDataJSON() {
      const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(state, null, 2));
      const downloadAnchor = document.createElement("a");
      downloadAnchor.setAttribute("href", dataStr);
      downloadAnchor.setAttribute("download", `ProjectPlanner_${state.project.name}_${formatDate(new Date())}.json`);
      document.body.appendChild(downloadAnchor);
      downloadAnchor.click();
      downloadAnchor.remove();
      showToast("ส่งออกข้อมูลเป็น JSON สำเร็จ");
    }

    function triggerImportJSON() {
      document.getElementById("json-file-input").click();
    }

    function importDataJSON(event) {
      const file = event.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const parsed = JSON.parse(e.target.result);
          if (parsed && parsed.project && Array.isArray(parsed.tasks)) {
            state.project = parsed.project;
            state.tasks = parsed.tasks;
            if (Array.isArray(parsed.dailyLogs)) state.dailyLogs = parsed.dailyLogs;
            saveState();
            initApp();
            showToast("นำเข้าข้อมูลโครงการสำเร็จเรียบร้อย");
          } else {
            alert("รูปแบบไฟล์ JSON ไม่ถูกต้อง");
          }
        } catch (err) {
          alert("ไม่สามารถอ่านไฟล์ JSON ได้: " + err.message);
        }
      };
      reader.readAsText(file);
      event.target.value = "";
    }

    function exportToCSV() {
      let csvContent = "\uFEFF"; // UTF-8 BOM
      csvContent += "ID,หมวดหมู่,ชื่องาน,ผู้รับผิดชอบ,วันที่เริ่มตามแผน,วันที่สิ้นสุดตามแผน,ระยะเวลา(วัน),วันที่เริ่มจริง,วันที่สิ้นสุดจริง,ความคืบหน้า(%),น้ำหนัก(%)\n";

      state.tasks.forEach(t => {
        csvContent += `"${t.id}","${t.category}","${t.name}","${t.assignedTo || ''}","${t.plannedStart}","${t.plannedEnd}",${t.duration},"${t.actualStart || ''}","${t.actualEnd || ''}",${t.progress},${t.weight}\n`;
      });

      const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.setAttribute("href", url);
      link.setAttribute("download", `Tasks_${state.project.name}_${formatDate(new Date())}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      showToast("ส่งออกข้อมูลเป็น CSV สำเร็จ");
    }

    function showToast(text) {
      const toast = document.getElementById("toast-msg");
      document.getElementById("toast-text").innerText = text;
      toast.classList.add("show");
      setTimeout(() => {
        toast.classList.remove("show");
      }, 3000);
    }

    /* =========================================================
       INITIALIZATION
       ========================================================= */
    function initApp() {
      loadState();
      renderTasks();
      renderDailyLogs();
      setupCanvasHover();

      // Render charts if on S-Curve tab
      renderCharts();

      window.addEventListener("resize", () => {
        if (state.activeTab === "tab-scurve") drawSCurveCanvas(calculateProjectTimeline());
        else if (state.activeTab === "tab-gantt") renderGantt();
        else if (state.activeTab === "tab-manpower") drawManpowerCanvas();
      });
    }

    window.addEventListener("DOMContentLoaded", initApp);
  </script>
</body>
</html>
"""

def main():
    target_path = r"c:\Users\Pond\OneDrive\Antigavity\index.html"
    print(f"Writing application to {target_path}...")
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(HTML_TEMPLATE.strip())
    print("Done! File size:", os.path.getsize(target_path), "bytes")

if __name__ == "__main__":
    main()
