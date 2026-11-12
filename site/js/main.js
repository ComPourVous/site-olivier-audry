// Menu mobile
const boutonMenu = document.querySelector(".menu-bouton");
const menu = document.querySelector(".menu");
boutonMenu.addEventListener("click", () => {
  const ouvert = menu.classList.toggle("ouvert");
  boutonMenu.setAttribute("aria-expanded", ouvert);
});
menu.querySelectorAll("a").forEach((lien) =>
  lien.addEventListener("click", () => {
    menu.classList.remove("ouvert");
    boutonMenu.setAttribute("aria-expanded", false);
  })
);

// Carte de la zone d'intervention (OpenStreetMap)
const blocCarte = document.getElementById("carte");
if (blocCarte && window.L) {
  const { centre, rayon_km, nom } = JSON.parse(blocCarte.dataset.carte);
  const carte = L.map(blocCarte, { scrollWheelZoom: false, zoomSnap: 0.25 }).setView(centre, 10);
  carte.attributionControl.setPrefix(false);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 15,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  }).addTo(carte);
  const zone = L.circle(centre, {
    radius: rayon_km * 1000,
    color: "#df5b15",
    weight: 2,
    fillColor: "#df5b15",
    fillOpacity: 0.12,
  }).addTo(carte);
  L.circleMarker(centre, { radius: 9, color: "#fff", weight: 2, fillColor: "#1a1a1a", fillOpacity: 1 })
    .bindTooltip(`${nom} – notre atelier`, { permanent: true, direction: "top", offset: [0, -8] })
    .addTo(carte);
  carte.fitBounds(zone.getBounds(), { padding: [20, 20] });
  // Molette active seulement après un clic, pour ne pas bloquer le défilement de la page
  carte.on("click", () => carte.scrollWheelZoom.enable());
  carte.on("mouseout", () => carte.scrollWheelZoom.disable());
}

// Flèches du carrousel des réalisations
const piste = document.querySelector(".carrousel-piste");
document.querySelectorAll(".carrousel-fleche").forEach((fleche) =>
  fleche.addEventListener("click", () => {
    const pas = piste.querySelector("li").offsetWidth + 20;
    piste.scrollBy({ left: fleche.classList.contains("suivant") ? pas : -pas, behavior: "smooth" });
  })
);
