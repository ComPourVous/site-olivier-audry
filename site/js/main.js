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

// Flèches du carrousel des réalisations
const piste = document.querySelector(".carrousel-piste");
document.querySelectorAll(".carrousel-fleche").forEach((fleche) =>
  fleche.addEventListener("click", () => {
    const pas = piste.querySelector("li").offsetWidth + 20;
    piste.scrollBy({ left: fleche.classList.contains("suivant") ? pas : -pas, behavior: "smooth" });
  })
);
