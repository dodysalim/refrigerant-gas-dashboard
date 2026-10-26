/**
 * GasRef Pro - Main Application Logic (ES6 Javascript)
 * Handles tab navigation, search/filtering, Chart.js, calculators and simulations.
 */

document.addEventListener("DOMContentLoaded", () => {
    // --- ESTADO GLOBAL ---
    let dataset = []; // Datos de refrigerantes cargados del JSON
    let activeFilters = {
        search: "",
        category: "all",
        type: "all",
        safety: "all",
        gwp: 15000,
        bp: 100
    };
    
    // Instancias de Gráficos (Chart.js)
    let scatterChart = null;
    let donutChart = null;
    let calcPTChart = null;
    let compareChart = null;

    // --- ELEMENTOS DEL DOM ---
    // Navegación
    const menuItems = document.querySelectorAll(".menu-item");
    const sections = document.querySelectorAll(".content-section");
    const pageTitle = document.getElementById("page-title");
    const pageSubtitle = document.getElementById("page-subtitle");
    
    // Filtros e Búsqueda
    const searchInput = document.getElementById("global-search");
    const catButtons = document.querySelectorAll(".cat-btn");
    const typeSelect = document.getElementById("filter-type");
    const safetySelect = document.getElementById("filter-safety");
    const gwpSlider = document.getElementById("filter-gwp");
    const gwpDisplay = document.getElementById("gwp-val-display");
    const bpSlider = document.getElementById("filter-bp");
    const bpDisplay = document.getElementById("bp-val-display");
    const clearFiltersBtn = document.getElementById("btn-clear-filters");
    const resultsCount = document.getElementById("results-count");
    const tableBody = document.getElementById("table-body");

    // Calculadora P-T
    const calcGasSelect = document.getElementById("calc-gas-select");
    const calcTempSlider = document.getElementById("calc-temp-slider");
    const calcTempDisplay = document.getElementById("calc-temp-display");
    
    // Resumen de la calculadora
    const calcSummaryBadge = document.getElementById("calc-summary-badge");
    const calcSummaryName = document.getElementById("calc-summary-name");
    const calcSummaryFormula = document.getElementById("calc-summary-formula");
    const calcSummaryCritTemp = document.getElementById("calc-summary-crit-temp");
    const calcSummaryCritPres = document.getElementById("calc-summary-crit-pres");
    const calcSummaryGlide = document.getElementById("calc-summary-glide");
    
    // Resultados de la calculadora
    const calcPressBubbleBar = document.getElementById("calc-press-bubble-bar");
    const calcPressBubblePsi = document.getElementById("calc-press-bubble-psi");
    const calcPressDewBar = document.getElementById("calc-press-dew-bar");
    const calcPressDewPsi = document.getElementById("calc-press-dew-psi");
    const calcSupercriticalAlert = document.getElementById("calc-supercritical-alert");
    const calcDewContainer = document.getElementById("calc-dew-container");

    // Comparador
    const compareGasSelects = document.querySelectorAll(".select-compare-gas");

    // Ciclo de Refrigeración
    const cycleGasSelect = document.getElementById("cycle-gas-select");
    const cycleEvapTemp = document.getElementById("cycle-evap-temp");
    const cycleEvapTempDisplay = document.getElementById("cycle-evap-temp-display");
    const cycleCondTemp = document.getElementById("cycle-cond-temp");
    const cycleCondTempDisplay = document.getElementById("cycle-cond-temp-display");
    
    const cyclePLow = document.getElementById("cycle-p-low");
    const cyclePLowPsi = document.getElementById("cycle-p-low-psi");
    const cyclePHigh = document.getElementById("cycle-p-high");
    const cyclePHighPsi = document.getElementById("cycle-p-high-psi");
    const cycleCompRatio = document.getElementById("cycle-comp-ratio");
    
    // Diagrama Ciclo
    const diagCompRatio = document.getElementById("diag-comp-ratio");
    const diagCondPres = document.getElementById("diag-cond-pres");
    const diagCondTemp = document.getElementById("diag-cond-temp");
    const diagEvapPres = document.getElementById("diag-evap-pres");
    const diagEvapTemp = document.getElementById("diag-evap-temp");
    const cycleActiveGasBadge = document.getElementById("cycle-active-gas-badge");

    // Modal
    const modal = document.getElementById("gas-details-modal");
    const modalCloseBtn = document.getElementById("modal-close-btn");
    const modalBanner = document.getElementById("modal-banner");
    const modalCategoryBadge = document.getElementById("modal-category-badge");
    const modalAshraeName = document.getElementById("modal-ashrae-name");
    const modalChemicalName = document.getElementById("modal-chemical-name");
    const modalFormula = document.getElementById("modal-formula");
    const modalGwp = document.getElementById("modal-gwp");
    const modalOdp = document.getElementById("modal-odp");
    const modalSafety = document.getElementById("modal-safety");
    const modalDescription = document.getElementById("modal-description");
    const modalProsList = document.getElementById("modal-pros-list");
    const modalConsList = document.getElementById("modal-cons-list");
    const modalBp = document.getElementById("modal-bp");
    const modalCt = document.getElementById("modal-ct");
    const modalOil = document.getElementById("modal-oil");
    const modalStatus = document.getElementById("modal-status");
    const modalAlternatives = document.getElementById("modal-alternatives");

    // --- TABS / NAVEGACIÓN ---
    menuItems.forEach(item => {
        item.addEventListener("click", (e) => {
            e.preventDefault();
            const targetSecId = item.getAttribute("href").substring(1);
            
            // Activar botón
            menuItems.forEach(m => m.classList.remove("active"));
            item.classList.add("active");
            
            // Activar Sección
            sections.forEach(sec => {
                sec.classList.remove("active");
                if (sec.id === `sec-${targetSecId}`) {
                    sec.classList.add("active");
                }
            });

            // Actualizar títulos
            switch(targetSecId) {
                case "dashboard":
                    pageTitle.textContent = "Panel de Control de Refrigeración";
                    pageSubtitle.textContent = "Análisis avanzado de 55 gases refrigerantes básicos, intermedios e industriales.";
                    break;
                case "pt-calculator":
                    pageTitle.textContent = "Calculadora Presión - Temperatura";
                    pageSubtitle.textContent = "Cálculo en tiempo real de presiones de saturación aplicando termodinámica analítica.";
                    // Redibujar gráfico para evitar bugs de tamaño en contenedor oculto
                    setTimeout(updateCalculatorChart, 100);
                    break;
                case "comparator":
                    pageTitle.textContent = "Comparador Termodinámico de Gases";
                    pageSubtitle.textContent = "Compare curvas de presión y métricas ecológicas lado a lado.";
                    setTimeout(updateCompareChart, 100);
                    break;
                case "refrigeration-cycle":
                    pageTitle.textContent = "Simulador de Ciclo de Refrigeración";
                    pageSubtitle.textContent = "Visualización de presiones y flujos en un ciclo cerrado de compresión.";
                    break;
                case "star-schema":
                    pageTitle.textContent = "Arquitectura del Modelo de Datos";
                    pageSubtitle.textContent = "Esquema Estrella estructurado para analíticas de alto rendimiento OLAP.";
                    break;
            }
        });
    });

    // --- CARGA DE DATOS ---
    async function loadData() {
        // Bypass de CORS si el archivo se abre con file:// leyendo el script precargado
        if (window.REFRIGERANTS_DATA && window.REFRIGERANTS_DATA.length > 0) {
            dataset = window.REFRIGERANTS_DATA;
            console.log("[+] Dataset cargado localmente (CORS Bypass exitoso):", dataset.length, "gases.");
            initializeDashboard();
            return;
        }

        try {
            console.log("[+] Solicitando JSON consolidado via fetch...");
            const response = await fetch("data/refrigerants_dashboard.json");
            if (!response.ok) {
                throw new Error("HTTP error " + response.status);
            }
            dataset = await response.json();
            console.log("[+] Dataset cargado con éxito via fetch:", dataset.length, "gases.");
            
            initializeDashboard();
        } catch (error) {
            console.error("[✘] Error cargando JSON, usando fallback de seguridad local:", error);
            document.body.insertAdjacentHTML('afterbegin', `
                <div style="background-color: #ef4444; color: white; padding: 1rem; text-align: center; font-weight: bold; position: fixed; top: 0; left: 0; width: 100%; z-index: 10000; box-shadow: 0 4px 10px rgba(0,0,0,0.5); font-family: sans-serif;">
                    Atención: Bloqueo de CORS del navegador. Use un servidor local ("python -m http.server 8000") o asegúrese de que "data/refrigerants_dashboard_data.js" esté disponible.
                </div>
            `);
        }
    }

    // --- INICIALIZACIÓN ---
    function initializeDashboard() {
        // Llenar selectores
        populateSelects();
        
        // Renderizar tabla por primera vez
        renderTable();
        
        // Crear gráficos generales
        buildScatterChart();
        buildDonutChart();
        
        // Lanzar calculadora P-T inicial (R-134a es id: 1)
        calcGasSelect.value = "1";
        triggerCalculatorUpdate();
        
        // Inicializar comparador (R-22, R-407C, R-427A)
        document.getElementById("compare-gas-1").value = "16"; // R-22
        document.getElementById("compare-gas-2").value = "19"; // R-407C
        document.getElementById("compare-gas-3").value = "25"; // R-427A
        triggerComparisonUpdate();

        // Inicializar ciclo
        cycleGasSelect.value = "1"; // R-134a
        triggerCycleUpdate();

        // Registrar Event Listeners
        registerFiltersEvents();
    }

    function populateSelects() {
        // Selector de la calculadora, comparador y ciclo
        let optionsHtml = "";
        dataset.forEach(gas => {
            optionsHtml += `<option value="${gas.refrigerant_key}">${gas.ashrae_name} (${gas.compound_type})</option>`;
        });
        
        calcGasSelect.innerHTML = optionsHtml;
        cycleGasSelect.innerHTML = optionsHtml;
        
        compareGasSelects.forEach(select => {
            select.innerHTML = optionsHtml;
        });
    }

    // --- SISTEMA DE FILTRADO Y BÚSQUEDA ---
    function registerFiltersEvents() {
        // Búsqueda por texto
        searchInput.addEventListener("input", (e) => {
            activeFilters.search = e.target.value.toLowerCase().trim();
            renderTable();
        });

        // Categoría (Básica, Intermedia, Industrial)
        catButtons.forEach(btn => {
            btn.addEventListener("click", () => {
                catButtons.forEach(b => b.classList.remove("active"));
                btn.classList.add("active");
                activeFilters.category = btn.getAttribute("data-category");
                renderTable();
            });
        });

        // Tipo
        typeSelect.addEventListener("change", (e) => {
            activeFilters.type = e.target.value;
            renderTable();
        });

        // Seguridad
        safetySelect.addEventListener("change", (e) => {
            activeFilters.safety = e.target.value;
            renderTable();
        });

        // Sliders
        gwpSlider.addEventListener("input", (e) => {
            const val = parseInt(e.target.value);
            activeFilters.gwp = val;
            gwpDisplay.textContent = val === 15000 ? "Cualquiera" : `< ${val.toLocaleString()}`;
            renderTable();
        });

        bpSlider.addEventListener("input", (e) => {
            const val = parseInt(e.target.value);
            activeFilters.bp = val;
            bpDisplay.textContent = val === 100 ? "Cualquiera" : `< ${val}°C`;
            renderTable();
        });

        // Limpiar Filtros
        clearFiltersBtn.addEventListener("click", () => {
            searchInput.value = "";
            catButtons.forEach(b => {
                b.classList.remove("active");
                if (b.getAttribute("data-category") === "all") b.classList.add("active");
            });
            typeSelect.value = "all";
            safetySelect.value = "all";
            gwpSlider.value = 15000;
            gwpDisplay.textContent = "Cualquiera";
            bpSlider.value = 100;
            bpDisplay.textContent = "Cualquiera";

            activeFilters = {
                search: "",
                category: "all",
                type: "all",
                safety: "all",
                gwp: 15000,
                bp: 100
            };
            renderTable();
        });

        // Calculadora
        calcGasSelect.addEventListener("change", triggerCalculatorUpdate);
        calcTempSlider.addEventListener("input", triggerCalculatorUpdate);

        // Comparador
        compareGasSelects.forEach(select => {
            select.addEventListener("change", triggerComparisonUpdate);
        });

        // Ciclo
        cycleGasSelect.addEventListener("change", triggerCycleUpdate);
        cycleEvapTemp.addEventListener("input", triggerCycleUpdate);
        cycleCondTemp.addEventListener("input", triggerCycleUpdate);

        // Modal
        modalCloseBtn.addEventListener("click", () => modal.classList.add("hide"));
        modal.addEventListener("click", (e) => {
            if (e.target === modal) modal.classList.add("hide");
        });
    }

    function getFilteredData() {
        return dataset.filter(gas => {
            // 1. Búsqueda por texto
            const matchesText = gas.ashrae_name.toLowerCase().includes(activeFilters.search) ||
                               gas.chemical_name.toLowerCase().includes(activeFilters.search) ||
                               gas.chemical_formula.toLowerCase().includes(activeFilters.search) ||
                               gas.primary_oil.toLowerCase().includes(activeFilters.search) ||
                               gas.description.toLowerCase().includes(activeFilters.search);
                               
            // 2. Filtro de Categoría
            const matchesCat = activeFilters.category === "all" || gas.category === activeFilters.category;
            
            // 3. Filtro de Tipo
            const matchesType = activeFilters.type === "all" || gas.compound_type === activeFilters.type;
            
            // 4. Filtro de Seguridad
            const matchesSafety = activeFilters.safety === "all" || gas.safety_group.includes(activeFilters.safety);
            
            // 5. Filtro de GWP
            const matchesGwp = gas.gwp <= activeFilters.gwp;
            
            // 6. Filtro de Punto de Ebullición
            const matchesBp = gas.boiling_point_c <= activeFilters.bp;

            return matchesText && matchesCat && matchesType && matchesSafety && matchesGwp && matchesBp;
        });
    }

    // --- RENDIMIENTO DE TABLA ---
    function renderTable() {
        const filtered = getFilteredData();
        resultsCount.textContent = `Mostrando ${filtered.length} gases`;
        
        tableBody.innerHTML = "";
        
        if (filtered.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="9" style="text-align: center; color: var(--text-muted); padding: 3rem;">Ningún gas coincide con los filtros aplicados.</td></tr>`;
            return;
        }

        filtered.forEach(gas => {
            const tr = document.createElement("tr");
            
            // Clase de categoría para color de borde izquierdo sutil
            let catClass = "cat-basic";
            if (gas.category === "Intermediate") catClass = "cat-intermediate";
            if (gas.category === "Industrial") catClass = "cat-industrial";
            
            let safetyClass = "safety-a1";
            if (gas.safety_group.includes("2L")) safetyClass = "safety-a2l";
            else if (gas.safety_group.includes("3")) safetyClass = "safety-a3";
            else if (gas.safety_group.startsWith("B")) safetyClass = "safety-tox";

            tr.innerHTML = `
                <td>
                    <div class="gas-row-title">
                        <span class="dot-indicator" style="background-color: ${gas.color_hex}; box-shadow: 0 0 8px ${gas.color_hex};"></span>
                        <strong>${gas.ashrae_name}</strong>
                    </div>
                </td>
                <td><span class="gas-row-formula">${gas.chemical_formula}</span></td>
                <td><span class="btn-pill ${catClass}">${gas.category}</span></td>
                <td><strong>${gas.gwp.toLocaleString()}</strong></td>
                <td><span style="color: ${gas.odp > 0 ? 'var(--color-danger)' : 'var(--color-success)'}; font-weight: bold;">${gas.odp}</span></td>
                <td><span class="safety-badge ${safetyClass}">${gas.safety_group}</span></td>
                <td>${gas.boiling_point_c}°C</td>
                <td>${gas.primary_oil}</td>
                <td style="font-weight: bold; color: var(--color-accent);">${gas.true_replacement}</td>
                <td><button class="btn-action-view" data-id="${gas.refrigerant_key}">Ver ficha</button></td>
            `;

            // Registrar evento de clic en toda la fila excepto en el botón si quisiéramos,
            // pero para simplificar, al botón directamente.
            tr.querySelector(".btn-action-view").addEventListener("click", () => {
                showGasDetails(gas.refrigerant_key);
            });
            
            tableBody.appendChild(tr);
        });

        // --- ACTUALIZACIÓN DINÁMICA DE MÉTRICAS ---
        const metricTotalGases = document.getElementById("metric-total-gases");
        const metricAvgGwp = document.getElementById("metric-avg-gwp");
        const metricPctOdp = document.getElementById("metric-pct-odp");
        const metricNaturalCount = document.getElementById("metric-natural-count");

        if (filtered.length > 0) {
            metricTotalGases.textContent = filtered.length;
            
            const avgGwp = filtered.reduce((acc, curr) => acc + curr.gwp, 0) / filtered.length;
            metricAvgGwp.textContent = Math.round(avgGwp).toLocaleString();

            const zeroOdpCount = filtered.filter(g => g.odp === 0).length;
            const pctOdp = (zeroOdpCount / filtered.length) * 100;
            metricPctOdp.textContent = pctOdp.toFixed(1) + "%";

            const naturalCount = filtered.filter(g => g.compound_type === "Natural").length;
            metricNaturalCount.textContent = naturalCount;
        } else {
            metricAvgGwp.textContent = "0";
            metricPctOdp.textContent = "0%";
            metricNaturalCount.textContent = "0";
        }
    }

    // --- DYNAMIC CYLINDER VISUALIZER ---
    function adjustColorBrightness(hex, percent) {
        hex = hex.replace(/^\s*#|\s*$/g, '');
        if (hex.length === 3) {
            hex = hex.replace(/(.)/g, '$1$1');
        }
        let r = parseInt(hex.substr(0, 2), 16);
        let g = parseInt(hex.substr(2, 2), 16);
        let b = parseInt(hex.substr(4, 2), 16);

        r = Math.max(0, Math.min(255, r + (r * (percent / 100))));
        g = Math.max(0, Math.min(255, g + (g * (percent / 100))));
        b = Math.max(0, Math.min(255, b + (b * (percent / 100))));

        const rHex = Math.round(r).toString(16).padStart(2, '0');
        const gHex = Math.round(g).toString(16).padStart(2, '0');
        const bHex = Math.round(b).toString(16).padStart(2, '0');

        return `#${rHex}${gHex}${bHex}`;
    }

    function generateDynamicCylinderSVG(gas) {
        const mainColor = gas.color_hex || "#7f8c8d";
        const gasName = gas.ashrae_name;
        const safetyGroup = gas.safety_group;
        
        let safetyColor = "#2ecc71"; // Verde para A1
        if (safetyGroup.includes("2L")) safetyColor = "#f1c40f"; // Amarillo para A2L
        else if (safetyGroup.includes("3")) safetyColor = "#e74c3c"; // Rojo para A3
        else if (safetyGroup.startsWith("B")) safetyColor = "#9b59b6"; // Púrpura para toxicidad
        
        return `
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 220" width="100%" height="100%" style="filter: drop-shadow(0 6px 12px rgba(0,0,0,0.55)); transform: translateY(5px); transform-origin: center;">
            <defs>
                <linearGradient id="body-grad-${gasName}" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stop-color="${adjustColorBrightness(mainColor, -40)}" />
                    <stop offset="25%" stop-color="${adjustColorBrightness(mainColor, 10)}" />
                    <stop offset="50%" stop-color="${adjustColorBrightness(mainColor, 40)}" />
                    <stop offset="75%" stop-color="${mainColor}" />
                    <stop offset="100%" stop-color="${adjustColorBrightness(mainColor, -50)}" />
                </linearGradient>
                <radialGradient id="dome-grad-${gasName}" cx="50%" cy="30%" r="50%" fx="40%" fy="20%">
                    <stop offset="0%" stop-color="${adjustColorBrightness(mainColor, 60)}" />
                    <stop offset="50%" stop-color="${mainColor}" />
                    <stop offset="100%" stop-color="${adjustColorBrightness(mainColor, -40)}" />
                </radialGradient>
                <linearGradient id="metal-grad-${gasName}" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stop-color="#7f8c8d" />
                    <stop offset="50%" stop-color="#e2e2e2" />
                    <stop offset="100%" stop-color="#95a5a6" />
                </linearGradient>
                <linearGradient id="brass-grad-${gasName}" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stop-color="#d35400" />
                    <stop offset="50%" stop-color="#f39c12" />
                    <stop offset="100%" stop-color="#8e44ad" />
                </linearGradient>
            </defs>

            <!-- Válvula Superior -->
            <rect x="74" y="14" width="12" height="12" fill="url(#metal-grad-${gasName})" rx="2"/>
            <ellipse cx="80" cy="14" rx="14" ry="4" fill="url(#metal-grad-${gasName})"/>
            <rect x="71" y="9" width="18" height="5" fill="#333" rx="1"/>
            <rect x="77" y="24" width="6" height="8" fill="url(#brass-grad-${gasName})"/>
            
            <!-- Shroud / Cuello Protector -->
            <path d="M52,36 C52,24 62,22 68,22 L92,22 C98,22 108,24 108,36 L104,44 L56,44 Z" fill="url(#metal-grad-${gasName})" stroke="#7f8c8d" stroke-width="0.5"/>
            <ellipse cx="68" cy="32" rx="7" ry="3" fill="#07090c"/>
            <ellipse cx="92" cy="32" rx="7" ry="3" fill="#07090c"/>

            <!-- Domo -->
            <path d="M30,72 C30,42 130,42 130,72 Z" fill="url(#dome-grad-${gasName})"/>

            <!-- Cuerpo principal -->
            <rect x="30" y="71" width="100" height="110" fill="url(#body-grad-${gasName})"/>
            
            <!-- Banda de Seguridad Color -->
            <rect x="30" y="115" width="100" height="18" fill="${safetyColor}" opacity="0.95"/>
            <text x="80" y="127" fill="#000" font-family="'Outfit', sans-serif" font-size="8" font-weight="900" text-anchor="middle" letter-spacing="0.5">${safetyGroup} CLASE</text>

            <!-- Etiqueta del Gas -->
            <rect x="42" y="80" width="76" height="30" fill="rgba(255,255,255,0.95)" rx="3" />
            <text x="80" y="95" fill="#141722" font-family="'Outfit', sans-serif" font-size="12" font-weight="900" text-anchor="middle">${gasName}</text>
            <text x="80" y="105" fill="#555" font-family="'Inter', sans-serif" font-size="6.5" font-weight="700" text-anchor="middle">${gas.chemical_formula}</text>

            <!-- Anillo Base -->
            <path d="M30,180 C30,188 130,188 130,180 L126,192 C126,198 34,198 34,192 Z" fill="url(#metal-grad-${gasName})"/>
        </svg>
        `;
    }

    function updateCylinderVisualizer(gas, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const name = gas.ashrae_name;
        let imgSource = null;

        // Primero intentar obtener la imagen real específica clasificada en carpetas
        if (window.REFRIGERANTS_IMAGES_MAP && window.REFRIGERANTS_IMAGES_MAP[name]) {
            imgSource = window.REFRIGERANTS_IMAGES_MAP[name].web;
            console.log(`[+] Cargada foto real de catálogo para ${name}: ${imgSource}`);
        }

        // Si no está mapeada, usar el mapeo cromático por defecto
        if (!imgSource) {
            const nameUpper = name.toUpperCase();
            const type = gas.compound_type.toUpperCase();
            
            if (nameUpper === "R-134A" || nameUpper === "R-513A" || nameUpper === "R-450A") {
                imgSource = "images/r134a.png"; // Celeste claro HFC estándar
            } else if (nameUpper === "R-22" || nameUpper === "R-408A" || nameUpper === "R-409A" || nameUpper === "R-417A" || nameUpper === "R-437A") {
                imgSource = "images/r22.png"; // Verde claro HCFC/HFC de transición
            } else if (nameUpper === "R-290" || nameUpper === "R-600A" || nameUpper === "R-1270" || nameUpper === "R-600" || nameUpper === "R-1150" || type === "HC") {
                imgSource = "images/r290.png"; // Verde oliva oscuro para Hidrocarburos inflamables
            } else if (nameUpper === "R-404A" || nameUpper === "R-422D" || nameUpper === "R-422A" || nameUpper === "R-438A") {
                imgSource = "images/r404a.png"; // Naranja HFC de media/baja temperatura
            } else if (nameUpper === "R-410A" || nameUpper === "R-410B" || nameUpper === "R-32") {
                imgSource = "images/r410a.png"; // Rosa/Fucsia HFC de alta presión
            } else if (nameUpper === "R-507" || nameUpper === "R-507A" || nameUpper === "R-508B" || nameUpper === "R-23") {
                imgSource = "images/r507.png"; // Turquesa/Teal mezclas azeotrópicas
            } else if (nameUpper === "R-717" || nameUpper === "R-729" || nameUpper === "R-718") {
                imgSource = "images/r717.png"; // Plateado industrial para Amoníaco/Aire/Agua
            } else if (nameUpper === "R-407C" || nameUpper === "R-407A" || nameUpper === "R-407F" || nameUpper === "R-427A" || nameUpper === "R-424A") {
                imgSource = "images/r407c.png"; // Marrón medio para la serie R-407
            } else if (nameUpper === "R-744") {
                imgSource = "images/r744.png"; // Gris oscuro/Negro para CO2 industrial
            } else if (nameUpper === "R-12" || nameUpper === "R-11" || nameUpper === "R-113" || nameUpper === "R-114" || nameUpper === "R-115" || nameUpper === "R-502" || type === "CFC") {
                imgSource = "images/r12.png"; // Rojo para CFCs tradicionales prohibidos / de alta flamabilidad
            } else if (nameUpper.startsWith("R-1234") || nameUpper.startsWith("R-1233") || type === "HFO" || nameUpper === "R-515B" || nameUpper === "R-454C" || nameUpper === "R-455A" || nameUpper === "R-454B") {
                imgSource = "images/r1234yf.png"; // Plateado blanco con banda roja para HFOs modernos
            } else {
                // Fallback inteligente según propiedades termodinámicas
                if (gas.boiling_point_c < -40) {
                    imgSource = "images/r404a.png"; // Mezclas de alta presión
                } else if (gas.gwp > 3000) {
                    imgSource = "images/r407c.png"; // Serie HFC de alto GWP
                } else {
                    imgSource = "images/r134a.png"; // Estándar general
                }
            }
        }

        container.innerHTML = `<img src="${imgSource}" alt="Cilindro de ${gas.ashrae_name}" style="max-width: 100%; max-height: 100%; object-fit: contain; filter: drop-shadow(0 5px 10px rgba(0,0,0,0.5)); transition: all 0.3s ease;">`;
    }

    // --- DETALLE MODAL ---
    function showGasDetails(id) {
        const gas = dataset.find(g => g.refrigerant_key === id);
        if (!gas) return;

        // Banner color por categoría
        let bannerGradient = "linear-gradient(135deg, rgba(46, 204, 113, 0.7) 0%, rgba(39, 174, 96, 0.7) 100%)";
        if (gas.category === "Intermediate") bannerGradient = "linear-gradient(135deg, rgba(52, 152, 219, 0.7) 0%, rgba(41, 128, 185, 0.7) 100%)";
        if (gas.category === "Industrial") bannerGradient = "linear-gradient(135deg, rgba(155, 89, 182, 0.7) 0%, rgba(142, 68, 173, 0.7) 100%)";

        modalBanner.style.background = bannerGradient;
        modalCategoryBadge.textContent = `${gas.category} Refrigeration System`;
        modalCategoryBadge.style.color = gas.color_hex;
        
        modalAshraeName.textContent = gas.ashrae_name;
        modalChemicalName.textContent = gas.chemical_name;
        modalFormula.textContent = gas.chemical_formula;
        modalGwp.textContent = gas.gwp.toLocaleString();
        modalOdp.textContent = gas.odp;
        modalSafety.textContent = gas.safety_group;
        modalDescription.textContent = gas.description;
        modalBp.textContent = `${gas.boiling_point_c} °C`;
        modalCt.textContent = `${gas.critical_temp_c} °C`;
        modalOil.textContent = gas.primary_oil;
        modalStatus.textContent = gas.status;
        modalAlternatives.textContent = gas.alternatives;

        // Cargar imagen o renderizar cilindro dinámicamente según el gas
        updateCylinderVisualizer(gas, "modal-cylinder-visual");

        const modalTrueReplacement = document.getElementById("modal-true-replacement");
        if (modalTrueReplacement) {
            modalTrueReplacement.textContent = gas.true_replacement;
        }

        // Llenar listas pros/cons
        modalProsList.innerHTML = "";
        gas.pros.split(",").forEach(item => {
            if (item.trim()) {
                const li = document.createElement("li");
                li.textContent = item.trim();
                modalProsList.appendChild(li);
            }
        });

        modalConsList.innerHTML = "";
        gas.cons.split(",").forEach(item => {
            if (item.trim()) {
                const li = document.createElement("li");
                li.textContent = item.trim();
                modalConsList.appendChild(li);
            }
        });

        // Mostrar
        modal.classList.remove("hide");
    }

    // --- GRÁFICOS ---
    function buildScatterChart() {
        const ctx = document.getElementById("scatterChart").getContext("2d");
        
        // Estructurar datos
        const basicData = [];
        const intermediateData = [];
        const industrialData = [];
        
        dataset.forEach(gas => {
            const pt = { x: gas.boiling_point_c, y: gas.critical_temp_c, label: gas.ashrae_name };
            if (gas.category === "Basic") basicData.push(pt);
            else if (gas.category === "Intermediate") intermediateData.push(pt);
            else if (gas.category === "Industrial") industrialData.push(pt);
        });

        scatterChart = new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [
                    {
                        label: 'Refrigeración Básica',
                        data: basicData,
                        backgroundColor: '#2ecc71',
                        borderColor: '#2ecc71',
                        pointRadius: 6,
                        pointHoverRadius: 9
                    },
                    {
                        label: 'Refrigeración Intermedia',
                        data: intermediateData,
                        backgroundColor: '#3498db',
                        borderColor: '#3498db',
                        pointRadius: 6,
                        pointHoverRadius: 9
                    },
                    {
                        label: 'Refrigeración Industrial',
                        data: industrialData,
                        backgroundColor: '#9b59b6',
                        borderColor: '#9b59b6',
                        pointRadius: 6,
                        pointHoverRadius: 9
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: { color: '#f3f4f6', font: { family: 'Inter', weight: '600' } }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.raw.label}: Ebullición: ${context.raw.x}°C, T. Crítica: ${context.raw.y}°C`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: { display: true, text: 'Punto de Ebullición a 1 atm (°C)', color: '#9ca3af', font: { weight: 'bold' } },
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#9ca3af' }
                    },
                    y: {
                        title: { display: true, text: 'Temperatura Crítica (°C)', color: '#9ca3af', font: { weight: 'bold' } },
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#9ca3af' }
                    }
                }
            }
        });
    }

    function buildDonutChart() {
        const ctx = document.getElementById("donutChart").getContext("2d");
        
        // Contar compuestos
        const counts = {};
        dataset.forEach(gas => {
            counts[gas.compound_type] = (counts[gas.compound_type] || 0) + 1;
        });

        const labels = Object.keys(counts);
        const data = Object.values(counts);

        donutChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: [
                        '#3498db', // HFC
                        '#2ecc71', // HC
                        '#9b59b6', // Natural
                        '#f1c40f', // HCFC
                        '#1abc9c', // HFO
                        '#e67e22', // CFC
                        '#e74c3c'  // HFO/HFC
                    ],
                    borderWidth: 1,
                    borderColor: '#141722'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: { color: '#9ca3af', font: { size: 10 } }
                    }
                },
                cutout: '60%'
            }
        });
    }

    // --- CALCULADORA P-T MÉTODOS ---
    function triggerCalculatorUpdate() {
        const gasId = parseInt(calcGasSelect.value);
        const tempC = parseInt(calcTempSlider.value);
        
        calcTempDisplay.textContent = `${tempC.toFixed(1)} °C`;
        
        const gas = dataset.find(g => g.refrigerant_key === gasId);
        if (!gas) return;

        // Actualizar resumen rápido
        calcSummaryBadge.textContent = gas.ashrae_name;
        calcSummaryBadge.style.backgroundColor = gas.color_hex;
        calcSummaryName.textContent = gas.chemical_name;
        calcSummaryFormula.textContent = gas.chemical_formula;
        calcSummaryCritTemp.textContent = `${gas.critical_temp_c} °C`;
        calcSummaryCritPres.textContent = `${gas.critical_pressure_bar} bar`;
        
        // Glide
        let glide = 0;
        if (gas.ashrae_name === "R-407C") glide = 5.0;
        else if (gas.ashrae_name === "R-455A") glide = 12.0;
        else if (gas.ashrae_name.startsWith("R-4")) glide = 2.0;
        calcSummaryGlide.textContent = glide > 0 ? `${glide.toFixed(1)} °C` : "0.0 °C (Azeótropo/Puro)";

        // Actualizar visualización del cilindro en la calculadora
        updateCylinderVisualizer(gas, "calc-cylinder-visual");

        // Estatus Supercrítico
        if (tempC >= gas.critical_temp_c) {
            calcPressBubbleBar.textContent = "---";
            calcPressBubblePsi.textContent = "---";
            calcPressDewBar.textContent = "---";
            calcPressDewPsi.textContent = "---";
            calcSupercriticalAlert.classList.remove("hide");
            return;
        } else {
            calcSupercriticalAlert.classList.add("hide");
        }

        // Buscar puntos de presión
        let pBubbleAbs = 0;
        let pDewAbs = 0;

        const bubblePoint = gas.pt_points.find(p => p.temp_c === tempC && p.state.includes("Bubble"));
        if (bubblePoint) {
            pBubbleAbs = bubblePoint.p_bar;
        } else {
            pBubbleAbs = calculateVaporPressureInterpolated(gas, tempC, "Bubble");
        }

        const pBubbleGauge = Math.max(0, pBubbleAbs - 1.01325);
        calcPressBubbleBar.innerHTML = `${pBubbleGauge.toFixed(2)} <span style="font-size: 1.1rem; color: var(--text-secondary); font-weight: 500;">barg</span> <span style="font-size: 0.8rem; color: var(--text-muted); display: block; font-weight: normal; margin-top: 0.2rem;">(${pBubbleAbs.toFixed(2)} bara abs)</span>`;
        calcPressBubblePsi.innerHTML = `${(pBubbleGauge * 14.5038).toFixed(1)} <span style="font-size: 1.1rem; color: var(--text-secondary); font-weight: 500;">psig</span> <span style="font-size: 0.8rem; color: var(--text-muted); display: block; font-weight: normal; margin-top: 0.2rem;">(${(pBubbleAbs * 14.5038).toFixed(1)} psia abs)</span>`;

        // Mostrar o no Dew point (Glide)
        if (glide > 0) {
            calcDewContainer.classList.remove("hide");
            const dewPoint = gas.pt_points.find(p => p.temp_c === tempC && p.state.includes("Dew"));
            if (dewPoint) {
                pDewAbs = dewPoint.p_bar;
            } else {
                pDewAbs = calculateVaporPressureInterpolated(gas, tempC, "Dew");
            }
            const pDewGauge = Math.max(0, pDewAbs - 1.01325);
            calcPressDewBar.innerHTML = `${pDewGauge.toFixed(2)} <span style="font-size: 1.1rem; color: var(--text-secondary); font-weight: 500;">barg</span> <span style="font-size: 0.8rem; color: var(--text-muted); display: block; font-weight: normal; margin-top: 0.2rem;">(${pDewAbs.toFixed(2)} bara abs)</span>`;
            calcPressDewPsi.innerHTML = `${(pDewGauge * 14.5038).toFixed(1)} <span style="font-size: 1.1rem; color: var(--text-secondary); font-weight: 500;">psig</span> <span style="font-size: 0.8rem; color: var(--text-muted); display: block; font-weight: normal; margin-top: 0.2rem;">(${(pDewAbs * 14.5038).toFixed(1)} psia abs)</span>`;
        } else {
            // Si no hay glide, ocultamos el Dew point
            calcDewContainer.classList.add("hide");
        }

        updateCalculatorChart();
    }

    // Interpolador usando el motor termodinámico de Clausius-Clapeyron en JS!
    function calculateVaporPressureInterpolated(gas, temp_c, type) {
        if (temp_c >= gas.critical_temp_c) return gas.critical_pressure_bar;
        
        let glide = 0;
        if (type === "Dew") {
            if (gas.ashrae_name === "R-407C") glide = 5.0;
            else if (gas.ashrae_name === "R-455A") glide = 12.0;
            else if (gas.ashrae_name.startsWith("R-4")) glide = 2.0;
        }
        
        const evaluated_temp = temp_c - glide;
        
        // Trouton termodinámico
        const T = evaluated_temp + 273.15;
        const T_b = gas.boiling_point_c + 273.15;
        const T_c = gas.critical_temp_c + 273.15;
        const P_c = gas.critical_pressure_bar;
        
        let trouton = 10.5;
        if (gas.compound_type === "Natural") {
            trouton = gas.ashrae_name === "R-717" ? 12.8 : 10.6;
        }
        
        const ln_p = Math.log(1.01325) + trouton * T_b * (1.0 / T_b - 1.0 / T);
        let p_abs = Math.exp(ln_p);
        
        const T_r = T / T_c;
        if (T_r > 0.6) {
            const correction = 1.0 + 0.15 * Math.sin(Math.PI * (T_r - 0.6) / 0.4);
            p_abs = p_abs * correction;
        }
        
        return Math.min(Math.max(p_abs, 0.005), P_c);
    }

    function updateCalculatorChart() {
        const gasId = parseInt(calcGasSelect.value);
        const currentTemp = parseInt(calcTempSlider.value);
        const gas = dataset.find(g => g.refrigerant_key === gasId);
        if (!gas) return;

        // Generar puntos continuos para graficar
        const labels = [];
        const bubbleData = [];
        const dewData = [];
        const verticalLineData = [];

        // Filtramos puntos por debajo de la crítica
        const graphTemps = [];
        for (let t = -50; t <= Math.min(70, Math.floor(gas.critical_temp_c - 1)); t += 5) {
            graphTemps.push(t);
        }

        graphTemps.forEach(t => {
            labels.push(t);
            const pBubble = calculateVaporPressureInterpolated(gas, t, "Bubble");
            bubbleData.push(pBubble);
            
            let glide = 0;
            if (gas.ashrae_name === "R-407C") glide = 5.0;
            else if (gas.ashrae_name === "R-455A") glide = 12.0;
            else if (gas.ashrae_name.startsWith("R-4")) glide = 2.0;
            
            if (glide > 0) {
                const pDew = calculateVaporPressureInterpolated(gas, t, "Dew");
                dewData.push(pDew);
            } else {
                dewData.push(pBubble);
            }
        });

        // Crear o actualizar
        const ctx = document.getElementById("calcPTChart").getContext("2d");
        
        if (calcPTChart) {
            calcPTChart.destroy();
        }

        document.getElementById("calc-chart-title").textContent = `Curva de Saturated Pressure (P-T) de ${gas.ashrae_name}`;

        const datasets = [{
            label: 'Presión de Burbuja (Líquido)',
            data: bubbleData,
            borderColor: gas.color_hex,
            backgroundColor: 'transparent',
            borderWidth: 3,
            tension: 0.3,
            pointRadius: 2
        }];

        // Agregar curva dew si hay glide notable
        let glide = 0;
        if (gas.ashrae_name === "R-407C") glide = 5.0;
        else if (gas.ashrae_name === "R-455A") glide = 12.0;
        else if (gas.ashrae_name.startsWith("R-4")) glide = 2.0;
        
        if (glide > 0) {
            datasets.push({
                label: 'Presión de Rocío (Vapor)',
                data: dewData,
                borderColor: '#00e1d9',
                backgroundColor: 'transparent',
                borderWidth: 2,
                borderDash: [5, 5],
                tension: 0.3,
                pointRadius: 2
            });
        }

        // Punto operativo actual
        const currentP = calculateVaporPressureInterpolated(gas, currentTemp, "Bubble");
        datasets.push({
            label: 'Punto de Trabajo Actual',
            data: labels.map(t => t === Math.round(currentTemp/5)*5 ? currentP : null),
            borderColor: '#ef4444',
            backgroundColor: '#ef4444',
            pointRadius: 8,
            pointHoverRadius: 10,
            showLine: false
        });

        calcPTChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#f3f4f6' }
                    }
                },
                scales: {
                    x: {
                        title: { display: true, text: 'Temperatura (°C)', color: '#9ca3af' },
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#9ca3af' }
                    },
                    y: {
                        title: { display: true, text: 'Presión Absoluta (bar)', color: '#9ca3af' },
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#9ca3af' }
                    }
                }
            }
        });
    }

    // --- COMPARADOR MÉTODOS ---
    function triggerComparisonUpdate() {
        const id1 = parseInt(document.getElementById("compare-gas-1").value);
        const id2 = parseInt(document.getElementById("compare-gas-2").value);
        const id3 = parseInt(document.getElementById("compare-gas-3").value);

        const gas1 = dataset.find(g => g.refrigerant_key === id1);
        const gas2 = dataset.find(g => g.refrigerant_key === id2);
        const gas3 = dataset.find(g => g.refrigerant_key === id3);

        if (!gas1 || !gas2 || !gas3) return;

        // Cabeceras de tabla
        document.getElementById("comp-h-gas1").textContent = gas1.ashrae_name;
        document.getElementById("comp-h-gas2").textContent = gas2.ashrae_name;
        document.getElementById("comp-h-gas3").textContent = gas3.ashrae_name;

        // Fórmulas
        document.getElementById("comp-formula-gas1").textContent = gas1.chemical_formula;
        document.getElementById("comp-formula-gas2").textContent = gas2.chemical_formula;
        document.getElementById("comp-formula-gas3").textContent = gas3.chemical_formula;

        // Tipos
        document.getElementById("comp-type-gas1").textContent = gas1.compound_type;
        document.getElementById("comp-type-gas2").textContent = gas2.compound_type;
        document.getElementById("comp-type-gas3").textContent = gas3.compound_type;

        // Sustituto Recomendado
        document.getElementById("comp-replacement-gas1").textContent = gas1.true_replacement;
        document.getElementById("comp-replacement-gas2").textContent = gas2.true_replacement;
        document.getElementById("comp-replacement-gas3").textContent = gas3.true_replacement;

        // Seguridad
        document.getElementById("comp-safety-gas1").textContent = gas1.safety_group;
        document.getElementById("comp-safety-gas2").textContent = gas2.safety_group;
        document.getElementById("comp-safety-gas3").textContent = gas3.safety_group;

        // Aceites
        document.getElementById("comp-oil-gas1").textContent = gas1.primary_oil;
        document.getElementById("comp-oil-gas2").textContent = gas2.primary_oil;
        document.getElementById("comp-oil-gas3").textContent = gas3.primary_oil;

        // Ebullición
        document.getElementById("comp-bp-gas1").textContent = `${gas1.boiling_point_c} °C`;
        document.getElementById("comp-bp-gas2").textContent = `${gas2.boiling_point_c} °C`;
        document.getElementById("comp-bp-gas3").textContent = `${gas3.boiling_point_c} °C`;

        // Crítica
        document.getElementById("comp-ct-gas1").textContent = `${gas1.critical_temp_c} °C`;
        document.getElementById("comp-ct-gas2").textContent = `${gas2.critical_temp_c} °C`;
        document.getElementById("comp-ct-gas3").textContent = `${gas3.critical_temp_c} °C`;

        // ODP
        document.getElementById("comp-odp-gas1").innerHTML = `<span style="color:${gas1.odp > 0 ? 'var(--color-danger)' : 'var(--color-success)'}; font-weight:bold;">${gas1.odp}</span>`;
        document.getElementById("comp-odp-gas2").innerHTML = `<span style="color:${gas2.odp > 0 ? 'var(--color-danger)' : 'var(--color-success)'}; font-weight:bold;">${gas2.odp}</span>`;
        document.getElementById("comp-odp-gas3").innerHTML = `<span style="color:${gas3.odp > 0 ? 'var(--color-danger)' : 'var(--color-success)'}; font-weight:bold;">${gas3.odp}</span>`;

        // GWP
        document.getElementById("comp-gwp-gas1").textContent = gas1.gwp.toLocaleString();
        document.getElementById("comp-gwp-gas2").textContent = gas2.gwp.toLocaleString();
        document.getElementById("comp-gwp-gas3").textContent = gas3.gwp.toLocaleString();

        updateCompareChart(gas1, gas2, gas3);
    }

    function updateCompareChart(g1, g2, g3) {
        if (!g1) {
            const id1 = parseInt(document.getElementById("compare-gas-1").value);
            const id2 = parseInt(document.getElementById("compare-gas-2").value);
            const id3 = parseInt(document.getElementById("compare-gas-3").value);
            g1 = dataset.find(g => g.refrigerant_key === id1);
            g2 = dataset.find(g => g.refrigerant_key === id2);
            g3 = dataset.find(g => g.refrigerant_key === id3);
        }
        if (!g1 || !g2 || !g3) return;

        const labels = [-50, -40, -30, -20, -10, 0, 10, 20, 30, 40, 50, 60, 70];
        
        const data1 = labels.map(t => calculateVaporPressureInterpolated(g1, t, "Bubble"));
        const data2 = labels.map(t => calculateVaporPressureInterpolated(g2, t, "Bubble"));
        const data3 = labels.map(t => calculateVaporPressureInterpolated(g3, t, "Bubble"));

        const ctx = document.getElementById("compareChart").getContext("2d");
        
        if (compareChart) {
            compareChart.destroy();
        }

        compareChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: g1.ashrae_name,
                        data: data1,
                        borderColor: g1.color_hex,
                        backgroundColor: 'transparent',
                        borderWidth: 3,
                        tension: 0.3
                    },
                    {
                        label: g2.ashrae_name,
                        data: data2,
                        borderColor: g2.color_hex,
                        backgroundColor: 'transparent',
                        borderWidth: 2,
                        tension: 0.3
                    },
                    {
                        label: g3.ashrae_name,
                        data: data3,
                        borderColor: g3.color_hex,
                        backgroundColor: 'transparent',
                        borderWidth: 2,
                        borderDash: [4, 4],
                        tension: 0.3
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: '#f3f4f6' } }
                },
                scales: {
                    x: {
                        title: { display: true, text: 'Temperatura (°C)', color: '#9ca3af' },
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#9ca3af' }
                    },
                    y: {
                        title: { display: true, text: 'Presión Absoluta (bar)', color: '#9ca3af' },
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#9ca3af' }
                    }
                }
            }
        });
    }

    // --- CICLO DE REFRIGERACIÓN MÉTODOS ---
    function triggerCycleUpdate() {
        const gasId = parseInt(cycleGasSelect.value);
        const evapTemp = parseInt(cycleEvapTemp.value);
        const condTemp = parseInt(cycleCondTemp.value);

        cycleEvapTempDisplay.textContent = `${evapTemp} °C`;
        cycleCondTempDisplay.textContent = `${condTemp} °C`;

        const gas = dataset.find(g => g.refrigerant_key === gasId);
        if (!gas) return;

        // Calcular presiones
        let pLow = calculateVaporPressureInterpolated(gas, evapTemp, "Bubble");
        let pHigh = calculateVaporPressureInterpolated(gas, condTemp, "Bubble");

        // Si supera temperatura crítica en condensación, limitamos a la crítica
        if (condTemp >= gas.critical_temp_c) {
            pHigh = gas.critical_pressure_bar;
        }
        if (evapTemp >= gas.critical_temp_c) {
            pLow = gas.critical_pressure_bar;
        }

        // Actualizar métricas del ciclo
        // Calcular presiones manométricas (barg / psig) para coincidir con la lectura real de manómetros de técnicos
        const pLowGauge = Math.max(0, pLow - 1.01325);
        const pHighGauge = Math.max(0, pHigh - 1.01325);

        // Actualizar métricas del ciclo
        cyclePLow.innerHTML = `${pLowGauge.toFixed(2)} <span style="font-size: 0.8rem; font-weight: normal; color: var(--text-muted);">barg</span> <span style="font-size: 0.75rem; font-weight: normal; color: var(--text-muted); display: block; margin-top: 0.1rem;">(${pLow.toFixed(2)} bara abs)</span>`;
        cyclePLowPsi.innerHTML = `${(pLowGauge * 14.5038).toFixed(1)} <span style="font-size: 0.8rem; font-weight: normal; color: var(--text-muted);">psig</span> <span style="font-size: 0.75rem; font-weight: normal; color: var(--text-muted); display: block; margin-top: 0.1rem;">(${(pLow * 14.5038).toFixed(1)} psia abs)</span>`;
        
        cyclePHigh.innerHTML = `${pHighGauge.toFixed(2)} <span style="font-size: 0.8rem; font-weight: normal; color: var(--text-muted);">barg</span> <span style="font-size: 0.75rem; font-weight: normal; color: var(--text-muted); display: block; margin-top: 0.1rem;">(${pHigh.toFixed(2)} bara abs)</span>`;
        cyclePHighPsi.innerHTML = `${(pHighGauge * 14.5038).toFixed(1)} <span style="font-size: 0.8rem; font-weight: normal; color: var(--text-muted);">psig</span> <span style="font-size: 0.75rem; font-weight: normal; color: var(--text-muted); display: block; margin-top: 0.1rem;">(${(pHigh * 14.5038).toFixed(1)} psia abs)</span>`;

        const ratio = pHigh / pLow;
        cycleCompRatio.textContent = ratio.toFixed(2);
        
        if (ratio > 6.0) {
            cycleCompRatio.style.color = "var(--color-danger)";
        } else if (ratio > 4.5) {
            cycleCompRatio.style.color = "var(--color-warning)";
        } else {
            cycleCompRatio.style.color = "var(--color-success)";
        }

        // Actualizar diagrama
        cycleActiveGasBadge.textContent = `Activo: ${gas.ashrae_name}`;
        diagCompRatio.textContent = `RC: ${ratio.toFixed(2)}`;
        diagCondPres.innerHTML = `${pHighGauge.toFixed(2)} <span style="font-size: 0.7rem; color: rgba(255,255,255,0.6);">barg</span> <span style="font-size: 0.65rem; color: rgba(255,255,255,0.4); display:block;">(${pHigh.toFixed(2)} bara)</span>`;
        diagCondTemp.textContent = `${condTemp.toFixed(1)} °C`;
        diagEvapPres.innerHTML = `${pLowGauge.toFixed(2)} <span style="font-size: 0.7rem; color: rgba(255,255,255,0.6);">barg</span> <span style="font-size: 0.65rem; color: rgba(255,255,255,0.4); display:block;">(${pLow.toFixed(2)} bara)</span>`;
        diagEvapTemp.textContent = `${evapTemp.toFixed(1)} °C`;
    }

    // Lanzar carga inicial
    loadData();
});
