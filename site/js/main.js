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
  const { communes, contour, base } = JSON.parse(blocCarte.dataset.carte);
  const carte = L.map(blocCarte, { scrollWheelZoom: false });
  carte.attributionControl.setPrefix(false);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 15,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  }).addTo(carte);
  if (contour.length > 2) {
    L.polygon(contour, { color: "#df5b15", weight: 2, fillColor: "#df5b15", fillOpacity: 0.12 }).addTo(carte);
  }
  communes.forEach(({ nom, lat, lon }) => {
    const estBase = nom === base;
    L.circleMarker([lat, lon], {
      radius: estBase ? 9 : 6,
      color: "#fff",
      weight: 2,
      fillColor: estBase ? "#1a1a1a" : "#df5b15",
      fillOpacity: 1,
    })
      .bindTooltip(estBase ? `${nom} – notre atelier` : nom, { permanent: estBase, direction: "top", offset: [0, -8] })
      .addTo(carte);
  });
  if (communes.length) {
    carte.fitBounds(communes.map((c) => [c.lat, c.lon]), { padding: [30, 30] });
  }
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
