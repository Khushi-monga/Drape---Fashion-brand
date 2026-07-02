document.addEventListener("DOMContentLoaded", () => {

    /* =========================
       FILTER CHIPS
    ========================= */

    const chips = document.querySelectorAll(".chip");

    chips.forEach(chip => {

        chip.addEventListener("click", () => {

            chips.forEach(c => c.classList.remove("active"));
            chip.classList.add("active");

        });

    });


    /* =========================
       WISHLIST BUTTON
    ========================= */

    document.querySelectorAll(".product-card button").forEach(button => {

        button.addEventListener("click", e => {

            e.preventDefault();

            button.classList.toggle("liked");

            const icon = button.querySelector("i");

            icon.classList.toggle("fa-regular");
            icon.classList.toggle("fa-solid");

        });

    });

});

document.querySelectorAll(".product-card").forEach((card, index) => {
    card.style.animationDelay = `${index * 70}ms`;
});