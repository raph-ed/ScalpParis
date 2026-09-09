let map = null;
let markersLayer = null;

document.addEventListener("DOMContentLoaded", () => {
    initMap();

    const btnRechercher = document.getElementById("btn-rechercher");
    const btnExporter = document.getElementById("btn-exporter");
    const formFeedback = document.getElementById("form-feedback");
    const feedbackToggle = document.getElementById("feedback-toggle");
    const feedbackPopover = document.getElementById("feedback-popover");
    const feedbackClose = document.getElementById("feedback-close");
    const linkViewFeedbacks = document.getElementById("link-view-feedbacks");
    const modalFeedbacks = document.getElementById("modal-feedbacks");
    const modalClose = document.getElementById("modal-close");

    btnRechercher.addEventListener("click", executerRecherche);

    btnExporter.addEventListener("click", () => {
        const cp = document.getElementById("code_postal").value;
        const sec = document.getElementById("secteur").value;
        window.location.href = `/api/export?code_postal=${cp}&secteur=${sec}`;
    });

    feedbackToggle.addEventListener("click", () => {
        feedbackPopover.classList.toggle("hidden");
    });

    feedbackClose.addEventListener("click", () => {
        feedbackPopover.classList.add("hidden");
    });

    formFeedback.addEventListener("submit", async (e) => {
        e.preventDefault();
        const note = parseInt(document.getElementById("feedback-note").value, 10);
        const comm = document.getElementById("feedback-comm").value;

        const res = await fetch("/api/feedback", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ avis_note: note, commentaire: comm })
        });

        if (res.ok) {
            alert("Retour enregistre dans la base de donnees locale.");
            formFeedback.reset();
            feedbackPopover.classList.add("hidden");
        }
    });

    linkViewFeedbacks.addEventListener("click", async (e) => {
        e.preventDefault();
        await chargerFeedbacks();
        modalFeedbacks.classList.remove("hidden");
    });

    modalClose.addEventListener("click", () => {
        modalFeedbacks.classList.add("hidden");
    });
});

function initMap() {
    map = L.map("map").setView([48.8566, 2.3522], 13);

    // Fond de carte satellite haute résolution (Esri World Imagery)
    L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", {
        attribution: "Tiles &copy; Esri, Earthstar Geographics",
        maxZoom: 19
    }).addTo(map);

    // Calque de transport et noms de voies en surimpression pour le repérage
    L.tileLayer("https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Transportation/MapServer/tile/{z}/{y}/{x}", {
        maxZoom: 19,
        opacity: 0.85
    }).addTo(map);

    markersLayer = L.layerGroup().addTo(map);
}

async function executerRecherche() {
    const cp = document.getElementById("code_postal").value;
    const sec = document.getElementById("secteur").value;
    const btn = document.getElementById("btn-rechercher");
    const resultsArea = document.getElementById("results-area");
    const btnExporter = document.getElementById("btn-exporter");

    btn.textContent = "Extraction en direct...";
    btn.disabled = true;

    try {
        const response = await fetch(`/api/recherche?code_postal=${cp}&secteur=${sec}`);
        const data = await response.json();

        afficherResultats(data);
        resultsArea.classList.remove("hidden");
        btnExporter.disabled = false;
        
        // Forcer le redimensionnement correct de Leaflet après affichage du conteneur
        setTimeout(() => { map.invalidateSize(); }, 200);
    } catch (err) {
        alert("Une anomalie s'est produite lors de la connexion a l'API Sirene.");
    } finally {
        btn.textContent = "Lancer l'extraction";
        btn.disabled = false;
    }
}

function afficherResultats(data) {
    document.getElementById("kpi-marge").textContent = `${data.statistiques.rendement_moyen_pct} %`;
    document.getElementById("kpi-ca").textContent = `${data.statistiques.ca_moyen.toLocaleString("fr-FR")} EUR`;
    document.getElementById("kpi-count").textContent = data.statistiques.nombre_etablissements;
    document.getElementById("kpi-score").textContent = `${data.statistiques.score_opportunite} / 100`;

    markersLayer.clearLayers();
    const bounds = [];

    data.etablissements.forEach(item => {
        // Marqueurs contrastés visibles sur l'imagerie satellite
        const marker = L.circleMarker([item.latitude, item.longitude], {
            radius: 8,
            fillColor: item.couleur_hex,
            color: "#ffffff",
            weight: 2,
            opacity: 1,
            fillOpacity: 0.95
        });

        marker.bindPopup(`
            <div style="font-family: monospace; font-size: 12px; color: #111;">
                <strong>${item.nom}</strong><br>
                ${item.adresse}<br><br>
                Statut: <b>${item.niveau_affluence}</b><br>
                CA Annuel: ${item.chiffre_affaires.toLocaleString("fr-FR")} EUR<br>
                Marge Nette: ${item.marge_nette_pct} %
            </div>
        `);

        marker.addTo(markersLayer);
        bounds.push([item.latitude, item.longitude]);
    });

    if (bounds.length > 0) {
        map.fitBounds(bounds, { padding: [40, 40] });
    }

    const prodContainer = document.getElementById("products-container");
    prodContainer.innerHTML = "";
    data.produits_phares.forEach(p => {
        const card = document.createElement("div");
        card.className = "product-card";
        card.innerHTML = `
            <div class="product-name">${p.produit}</div>
            <div class="product-meta">Prix Moyen: ${p.prix_moyen.toFixed(2)} EUR</div>
            <div class="product-meta">Indice Demande: ${p.indice_popularite} / 100</div>
        `;
        prodContainer.appendChild(card);
    });

    remplirTable("table-plus-rentables", data.plus_rentables);
    remplirTable("table-moins-rentables", data.moins_rentables);
}

function remplirTable(tableId, records) {
    const tbody = document.querySelector(`#${tableId} tbody`);
    tbody.innerHTML = "";
    records.forEach(r => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${r.nom}</td>
            <td>${r.marge} %</td>
            <td>${r.ca.toLocaleString("fr-FR")} EUR</td>
        `;
        tbody.appendChild(row);
    });
}

async function chargerFeedbacks() {
    const res = await fetch("/api/feedbacks/liste");
    const items = await res.json();
    const tbody = document.querySelector("#table-feedbacks tbody");
    tbody.innerHTML = "";

    items.forEach(i => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${i.date}</td>
            <td><b>${i.avis_note} / 10</b></td>
            <td>${i.commentaire}</td>
        `;
        tbody.appendChild(row);
    });
}
